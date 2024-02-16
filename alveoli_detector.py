#!/usr/bin/env python3


def main():
    import numpy as np
    import os
    import logging
    import coloredlogs
    import argparse
    import tifffile as tiff
    from zetastitcher import VirtualFusedVolume

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--volume', help="vfv yml path", metavar='PATH')
    parser.add_argument('-ds', '--downscaled', help="downscaled image file", metavar='PATH')
    parser.add_argument('-b', '--blocksize', help="size of blocks at desired resolution", type=int,
                        default=320)
    parser.add_argument('-xy', '--xyscale', help="xy scaling from full-res to analysis-res", type=float,
                        default=8)
    parser.add_argument('-xy', '--zscale', help="z scaling from full-res to analysis-res", type=float,
                        default=2.5)
    parser.add_argument('-r', '--rightchannel', help="name of the right channel", default='638')
    parser.add_argument('-l', '--leftchannel', help="name of the left channel", default='561')
    parser.add_argument('-d', '--debug', help="debug mode", action='store_true', default=False)
    args = parser.parse_args()

    ds = tiff.imread(args.downscaled)
    thr = 150   # threshold
    msc = 2   # scale from downscale to mask
    dscxy = 16  # xy scale from full-res to downscale
    dscz = 5    # z scale from full-res to downscale
    ms = mask(ds, thr, msc)

    xstep = (args.blocksize * args.xyscale) / (msc * dscxy)
    ystep = (args.blocksize * args.xyscale) / (msc * dscxy)
    zstep = (args.blocksize * args.zscale) / (msc * dscz)

    vfv = VirtualFusedVolume(args.volume)
    volume = []
    surface = []

    for x in np.arange(0, ms.shape[2], xstep):
        for y in np.arange(0, ms.shape[1], ystep):
            for z in np.arange(0, ms.shape[0], zstep):
                if np.any(ms[z:(z + zstep), y:(y + ystep), x:(x + xstep)]):
                    block = vfv[(z*args.zscale):((z*args.zscale) + args.blocksize),
                            (y*args.yscale):((y*args.yscale) + args.blocksize),
                            (x*args.xscale):((x*args.xscale) + args.blocksize)]
                    alveomask = segment(block, 180)
                    vol, surf = morpho(alveomask)
                    volume.append(vol)
                    surface.append(surf)



def mask(image, threshold, scale):
    from skimage.transform import rescale
    from skimage.morphology import binary_opening, binary_closing, ball
    im2 = rescale(image, 1/scale, preserve_range=True)
    im3 = im2>threshold
    im3 = binary_closing(im3, ball(5))
    im3 = binary_opening(im3, ball(3))
    return(im3)


def segment(image, threshold):
    from skimage.morphology import binary_opening, ball, skeletonize_3d, remove_small_holes
    import numpy as np
    import skan
    from scipy.ndimage import distance_transform_edt
    from skimage.segmentation import watershed
    from skimage.measure import label

    im = image<threshold

    # remove holes from binary data and extract pixel-wise skeleton
    ims = remove_small_holes(binary_opening(im, ball(3)), area_threshold=100000)
    sk = skeletonize_3d(ims)

    # extract vectorial skeleton and prune it
    skeleton1 = skan.Skeleton(sk)
    branch_data1 = skan.summarize(skeleton1)

    pruning = np.zeros(sk.shape)
    for index, element in branch_data1.iterrows():  # IMPORTANT: max branch length is set to 15
        if element['branch-type'] == 1 and element['branch-distance'] <= 15:
            path = skeleton1.path_coordinates(index)
            for px in path:
                pruning[px[0], px[1], px[2]] = 255
        elif element['branch-type'] == 3 or element['branch-type'] == 0:
            path = skeleton1.path_coordinates(index)
            for px in path:
                pruning[px[0], px[1], px[2]] = 255
    for index, element in branch_data1.iterrows():  # a correction to avoid removing connection points
        if element['branch-type'] == 1 and element['branch-distance'] > 15:
            path = skeleton1.path_coordinates(index)
            for px in path:
                pruning[px[0], px[1], px[2]] = 0
        elif element['branch-type'] == 2:
            path = skeleton1.path_coordinates(index)
            for px in path:
                pruning[px[0], px[1], px[2]] = 0

    # extract pruned skeleton
    skpruned = sk - pruning
    skeleton = skan.Skeleton(skpruned)
    branch_data = skan.summarize(skeleton)
    j2e = branch_data[branch_data['branch-type'] == 1]

    j2ef = j2e[j2e['branch-distance'] > 15]

    # create skeleton image with different color for each branch
    markers = np.zeros(sk2s.shape)
    n = 0
    m = j2ef.shape[0]
    for index, element in branch_data.iterrows():
        if element['branch-type'] == 1 and element['branch-distance'] > 15:  # j-2-e
            n += 1
            path = skeleton.path_coordinates(index)
            for px in path:
                markers[px[0], px[1], px[2]] = n
        elif element['branch-type'] == 2:  # j-2-j
            m += 1
            path = skeleton.path_coordinates(index)
            for px in path:
                markers[px[0], px[1], px[2]] = m

    # separate different volumes using watershed
    ed = distance_transform_edt(ims)
    wt = watershed(-ed, markers=markers.astype('int64'), mask=ims, compactness=10)

    # cleanup watershed, preserving only alveoli
    wtlab = np.copy(wt)
    wtlab[np.where(np.logical_and(wtlab < j2ef.shape[0], wtlab>0))] = 1
    wtlab[np.where(wtlab >= j2ef.shape[0])] = 0
    labels = label(wtlab)
    for n in range(labels.max()):
        s = np.sum(wtlab[labels == n])
        if s < 50000:
            wtlab[labels == n] = 0
        elif s > 1000000:
            if np.max(wtlab[labels == n]) == 1:
                wtlab[labels == n] = 0
    return wtlab


def morpho(alveomask):
    import numpy as np
    from skimage.morphology import binary_dilation
    from skimage.measure import label

    vol = []
    surf = []
    labels = label(alveomask)
    for n in np.arange(labels.max()):
        temp = labels == n
        u = temp.sum()
        temp2 = binary_dilation(temp)
        v = temp2.sum()
        vol.append(u)
        surf.append(v - u)

    return vol, surf
