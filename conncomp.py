#!/usr/bin/env python3


def main():
    import numpy as np
    import logging
    import coloredlogs
    import argparse
    import tifffile as tiff
    import os
    from scipy.spatial.qhull import QhullError
    from scipy import spatial
    spatial.QhullError = QhullError
    from skimage.morphology import label
    from skimage.measure import regionprops

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help="image folder path", metavar='PATH')
    parser.add_argument('-o', '--output', help="output base path", metavar='PATH')
    parser.add_argument('-t', '--threshold', help="binarization threshold", type=float, default=0.01)
    parser.add_argument('-b', '--batch', help="batch size", type=int, default=100)
    args = parser.parse_args()

    lista = os.listdir(args.input)
    test = tiff.imread(os.path.join(args.input, lista[0]))

    a = np.zeros((args.batch, test.shape[1], test.shape[2]))
    limit = int(len(lista) / args.batch)
    rem = len(lista) % args.batch
    print(rem)
    print(limit)
    print(args.batch)
    print(len(lista))

    aree = []
    coords = []

    for n in np.arange(0, limit, args.batch):
        logger.info('processing batch #%d', n)
        for m in np.arange(0, args.batch):
            a[m, ...] = tiff.imread(os.path.join(args.input, lista[m+n]))
        b = a > args.threshold
        c = label(b)
        props = regionprops(c)
        for prop in props:
            aree.append(prop.area)
            centro = list(prop.centroid)
            centro[0] += n
            coords.append(tuple(centro))

    a1 = np.zeros((rem, test.shape[1], test.shape[2]))

    logger.info('processing last batch')
    for m in np.arange(0, rem):
        a1[m, ...] = tiff.imread(os.path.join(args.input, lista[limit + m]))
    b1 = a1 > args.threshold
    c1 = label(b1)
    props = regionprops(c1)
    for prop in props:
        aree.append(prop.area)
        centro = list(prop.centroid)
        centro[0] += limit
        coords.append(tuple(centro))

    aree2 = np.array(aree)
    coords2 = np.array(coords)

    np.savetxt(os.path.join(args.output, 'areas.csv'), aree2)
    np.savetxt(os.path.join(args.output, 'coordinates.csv'), coords2)


if __name__ == "__main__":
    main()
