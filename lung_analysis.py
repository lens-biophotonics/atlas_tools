#!/usr/bin/env python3


def main():
    import logging
    import coloredlogs
    import argparse
    import tifffile as tiff
    from skimage.measure import label, regionprops
    from skimage.morphology import binary_closing
    from scipy.ndimage import binary_fill_holes
    from skimage.transform import rescale
    import numpy as np

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='INFO', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help="input file base", metavar='PATH')
    args = parser.parse_args()

    logger.info('opening segmented image')

    a = tiff.imread(args.input + '_Simple Segmentation.tiff')
    b = a < 2

    blabels = label(b)
    bregions = regionprops(blabels)
    sorted_regions = sorted(bregions, key=lambda x: x.area, reverse=True)

    logger.info('extracting alveoli')
    volumes, surfaces, alveoli_image = alveoli_finder(sorted_regions, b.shape)

    volvec = np.array(volumes) * 125 # volumes in um^3
    survec = np.array(surfaces) * 25 # volumes in um^2
    s2v = (survec/volvec) * 1000 # in mm-1

    logger.info('opening original image to get tissue volume')
    u = tiff.imread(args.input + '.tiff')
    v = rescale(u, 0.5, preserve_range=True)
    v1 = v > 150
    v2 = binary_closing(v1, footprint=np.ones((11, 11, 11)))
    v2 = binary_fill_holes(v2)
    vr = rescale(v2, 2, preserve_range=True)
    norm = np.sum(vr).astype('float') * 125 / 1000000000 # volume in mm^3


    np.savetxt(args.input + '_volumes.csv', volvec, delimiter=',')
    np.savetxt(args.input + '_surfaces.csv', survec, delimiter=',')
    np.savetxt(args.input + '_surface_2_volume.csv', s2v, delimiter=',')
    tiff.imwrite(args.input + '_alveoli_image.tiff', alveoli_image.astype('uint8'))
    print('Alveolar volume is ' + str(volvec.mean()) + '+/-' + str(volvec.std()) + ' um^3 (mean +/- std)')
    print('Alveolar surface is ' + str(survec.mean()) + '+/-' + str(survec.std()) + ' um^2 (mean +/- std)')
    print('Alveolar surface/volume ratio is ' + str(s2v.mean()) + '+/-' + str(s2v.std())
          + ' mm^-1 (mean +/- std)')
    print('Alveolar volume ratio is ' + str(np.sum(volvec)/(1000000000 * norm)))
    print('Alveolar surface density is ' + str(np.sum(survec)/(1000000 * norm)) + ' mm^-1')
    print('Alveolar density is ' + str(len(volvec)/norm) + ' mm^-3')
    print(str(len(volvec)) + 'alveoli detected in the volume')

    logger.info('saving report to file')
    with open(args.input + '_report.txt', 'w') as f:
        f.write('Alveolar volume is ' + str(volvec.mean()) + '+/-' + str(volvec.std()) + ' um^3 (mean +/- std)')
        f.write('Alveolar surface is ' + str(survec.mean()) + '+/-' + str(survec.std()) + ' um^2 (mean +/- std)')
        f.write('Alveolar surface/volume ratio is ' + str(s2v.mean()) + '+/-' + str(s2v.std())
              + ' mm^-1 (mean +/- std)')
        f.write('Alveolar volume ratio is ' + str(np.sum(volvec) / (1000000000 * norm)))
        f.write('Alveolar surface density is ' + str(np.sum(survec) / (1000000 * norm)) + ' mm^-1')
        f.write('Alveolar density is ' + str(len(volvec) / norm) + ' mm^-3')
        f.write(str(len(volvec)) + ' alveoli detected in the volume')

    logger.info('done')


def alveoli_finder(sorted_regions, shape):
    import logging
    import coloredlogs
    from skimage.morphology import skeletonize
    from scipy.ndimage import distance_transform_edt
    from skimage.segmentation import watershed
    from skimage.measure import label, regionprops, marching_cubes, mesh_surface_area
    import numpy as np
    import skan

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='INFO', logger=logger)

    alveolim = np.zeros(shape).astype('uint8')
    volumes = []  # list to append all volumes
    surfaces = []  # list to append all surfaces
    counter = 0

    # now, loop over connected components to identify alveoli in each of them
    for region in sorted_regions:
        # 2 controls to exclude too small regions (aspecific segmentation) and blood vessels (which are highly
        # elliptical and large
        if region.area > 500:  # THIS IS A PARAMETER
            if counter % 100 == 0:
                logger.info('processed %d of %d components', counter, len(sorted_regions))
            counter += 1
            e = region.axis_major_length / region.axis_minor_length
            if (e < 2) or (region.area < 30000):  # THESE ARE PARAMETERS
                # here the real stuff. Start with generating a binary image of the component
                reg = region.image
                zmin = region.bbox[0]
                zmax = region.bbox[3]
                ymin = region.bbox[1]
                ymax = region.bbox[4]
                xmin = region.bbox[2]
                xmax = region.bbox[5]
                # now extract the morphological skeleton and then a vectorial representation using skan
                try:
                    sk = skeletonize(reg)
                    skeleton = skan.Skeleton(sk)
                    branch_data = skan.summarize(skeleton)
                    # refine the skeleton selecting only junction-to-end (j2e) branches which are long enough
                    j2e = branch_data[np.logical_and(branch_data['branch-type'] == 1,
                                                     branch_data['branch-distance'] >= 10)]
                    # generate 'cleaned-up' skeleton image where all j2e have
                    # clearly defined values, different from others
                    n = 0
                    m = j2e.shape[0]
                    seeds = np.zeros_like(reg).astype('int64')
                    for index, element in branch_data.iterrows():
                        if element['branch-type'] == 1 and element['branch-distance'] >= 10:  # THIS IS A PARAMETER
                            n += 1
                            path = skeleton.path_coordinates(index)
                            for px in path:
                                seeds[px[0], px[1], px[2]] = n
                        elif element['branch-type'] == 2 or element['branch-type'] == 0 or element['branch-type'] == 3:
                            m += 1
                            path = skeleton.path_coordinates(index)
                            for px in path:
                                seeds[px[0], px[1], px[2]] = m
                    # further cleanup to remove spurious branches from thick bronchi
                    ed = distance_transform_edt(reg)
                    for n in np.arange(j2e.shape[0]):
                        if np.max((seeds == n) * ed) > 10:  # THIS IS A PARAMETER
                            seeds[seeds == n] = 0
                    # now perform watershed
                    water = watershed(-ed, markers=seeds.astype('int64'), mask=reg, compactness=0.01)
                    water[water > j2e.shape[0]] = 0  # remove j2j watersheds
                    alveolim[zmin:zmax, ymin:ymax, xmin:xmax] += (water > 0).astype('uint8') * 255
                    # label the alveoli image
                    comp = label(water)
                    alveoli = regionprops(comp)
                    for alveolo in alveoli:
                        try:
                            v, f, n, va = marching_cubes(alveolo.image)
                            temp = mesh_surface_area(v, f)
                            volumes.append(alveolo.area)
                            surfaces.append(temp)
                        except:
                            ghi = 1
                except:
                    if region.area < 1500:
                        alveolim[zmin:zmax, ymin:ymax, xmin:xmax] += (reg > 0).astype('uint8') * 255
                        comp = label(reg)
                        alveoli = regionprops(comp)
                        for alveolo in alveoli:
                            volumes.append(alveolo.area)
                            v, f, n, va = marching_cubes(alveolo.image)
                            surfaces.append(mesh_surface_area(v, f))

    return volumes, surfaces, alveolim


if __name__ == "__main__":
    main()
