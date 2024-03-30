#!/usr/bin/env python3
import os.path


def main():
    import numpy as np
    import logging
    import coloredlogs
    import argparse
    import tifffile as tiff
    from zetastitcher import VirtualFusedVolume
    from skimage.transform import rescale

    logger = logging.getLogger(__name__)
    vfv_logger = logging.getLogger("{0}.{1}")
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    vfv_logger.setLevel(logging.ERROR)
    coloredlogs.install(level='INFO', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--volume', help="vfv yml path", metavar='PATH')
    parser.add_argument('-ds', '--downscaled', help="downscaled image file", metavar='PATH')
    parser.add_argument('-b', '--blocksize', help="size of blocks at desired resolution", type=int,
                        default=300)
    parser.add_argument('-xy', '--xyscale', help="xy scaling from full-res to analysis-res", type=float,
                        default=8)
    parser.add_argument('-z', '--zscale', help="z scaling from full-res to analysis-res", type=float,
                        default=2.5)
    parser.add_argument('-o', '--outpath', help="output base path", metavar='PATH')
    args = parser.parse_args()

    logger.info('reading downscaled image...')

    ds = tiff.imread(args.downscaled)
    thr = 150  # threshold
    msc = 2  # scale from downscale to mask
    dscxy = 16  # xy scale from full-res to downscale
    dscz = 5  # z scale from full-res to downscale
    ms = mask(ds, thr, msc)

    xred = args.xyscale / (msc * dscxy)
    yred = args.xyscale / (msc * dscxy)
    zred = args.zscale / (msc * dscz)

    xstep = int(args.blocksize * xred)
    ystep = int(args.blocksize * yred)
    zstep = int(args.blocksize * zred)

    vfv = VirtualFusedVolume(args.volume)
    xm = vfv.shape[2]
    ym = vfv.shape[1]
    zm = vfv.shape[0]
    vols = []
    surfs = []
    scale_tup = tuple((args.zscale, args.xyscale, args.xyscale))
    out_shape = tuple(int(l / r) for l, r in zip(vfv.shape, scale_tup))
    out_mask = np.zeros(out_shape).astype('uint8')

    n = 1
    n_blocks = (int(out_shape[2] / args.blocksize) + 1) * (int(out_shape[1] / args.blocksize) +
                                                           1) * (int(out_shape[0] / args.blocksize) + 1)

    for x in np.arange(0, out_shape[2], args.blocksize):
        xr = int(x * xred)
        xv1 = int(x * args.xyscale)
        xv2 = int(np.clip((x + args.blocksize) * args.xyscale, 0, xm))
        for y in np.arange(0, out_shape[1], args.blocksize):
            yr = int(y * yred)
            yv1 = int(y * args.xyscale)
            yv2 = int(np.clip((y + args.blocksize) * args.xyscale, 0, ym))
            for z in np.arange(0, out_shape[0], args.blocksize):
                zr = int(z * zred)
                if np.any(ms[zr:(zr + zstep), yr:(yr + ystep), xr:(xr + xstep)]):
                    logger.info('processing block %d of %d', n, n_blocks)
                    zmin = int(z * args.zscale)
                    zmax = int(np.clip((z + args.blocksize) * args.zscale, 0, zm))
                    block_ds = np.zeros((int((zmax - zmin) / args.zscale), int((yv2 - yv1) / args.xyscale),
                                         int((xv2 - xv1) / args.xyscale))).astype('uint16')
                    for zeta in np.arange(0, args.blocksize, 10):
                        zv1 = int((z + zeta) * args.zscale)
                        zv2 = int(np.clip((z + zeta + 10) * args.zscale, 0, zm))
                        if zv1 < zm:
                            block = vfv[zv1:zv2, yv1:yv2, xv1:xv2]
                            block_ds[zeta:np.clip(zeta + 10, 0, block_ds.shape[0]),...] = rescale(block,
                                (1 / args.zscale, 1 / args.xyscale, 1 / args.xyscale), preserve_range=True)
                    tiff.imwrite('/home/silvestri/Lavoro/Experiments/Pini/block'+str(n)+'.tiff',block_ds)
                    try:
                        alveomask = segment(block_ds, 180)
                        vol, surf = morpho(alveomask)
                        vols.append(vol)
                        surfs.append(surf)
                        out_mask[z:int(zmax / args.zscale),
                                 y:int(yv2 / args.xyscale), x:int(xv2 / args.xyscale)] = alveomask.astype('uint8')
                    except:
                        logger.warning('error while processing block %d', n)
                n += 1

    tiff.imwrite(args.outpath + '.tiff', out_mask)
    np.savetxt(args.outpath + '_vol.csv', vols, delimiter=',', fmt='%d')
    np.savetxt(args.outpath + '_surf.csv', surfs, delimiter=',', fmt='%d')


def mask(image, threshold, scale):
    from skimage.transform import rescale
    from skimage.morphology import binary_opening, binary_closing, ball
    im2 = rescale(image, 1 / scale, preserve_range=True)
    im3 = im2 > threshold
    im3 = binary_closing(im3, ball(5))
    im3 = binary_opening(im3, ball(3))
    return im3


def segment(image, threshold):
    from skimage.morphology import binary_opening, ball, skeletonize_3d, remove_small_holes
    import numpy as np
    import skan
    from scipy.ndimage import distance_transform_edt
    from skimage.segmentation import watershed
    from skimage.measure import label

    im = image < threshold

    # remove holes from binary data and extract pixel-wise skeleton
    ims = remove_small_holes(binary_opening(im, ball(3)), area_threshold=100000)
    sk = skeletonize_3d(ims)

    # if the skeleton is empty, directly return a black array
    if sk.max() == 0:
        return sk.astype('int64')

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

    if skpruned.max() == 0.0:
        return skpruned.astype('int64')

    skeleton = skan.Skeleton(skpruned)
    branch_data = skan.summarize(skeleton)
    j2e = branch_data[branch_data['branch-type'] == 1]

    j2ef = j2e[j2e['branch-distance'] > 15]

    # create skeleton image with different color for each branch
    markers = np.zeros(sk.shape)
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

    # cleanup watershed, preserving only alveoli with reasonable size
    wtlab = np.copy(wt)
    wtlab[np.where(np.logical_and(wtlab < j2ef.shape[0], wtlab > 0))] = 1
    wtlab[np.where(wtlab >= j2ef.shape[0])] = 0
    labels = label(wtlab)
    for n in range(labels.max() + 1):
        s = np.sum(wtlab[labels == n])
        if s < 700:
            wtlab[labels == n] = 0
        elif s > 70000:
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
        tempo = temp.astype('float')
        u = tempo.sum()
        temp2 = binary_dilation(temp)
        tempo2 = temp2.astype('float')
        v = tempo2.sum()
        vol.append(u)
        surf.append(v - u)

    return vol, surf


if __name__ == "__main__":
    main()
