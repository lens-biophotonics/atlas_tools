#!/usr/bin/env python3


def main():
    from zetastitcher import InputFile
    import logging
    import coloredlogs
    import tifffile as tiff
    from scipy.signal import fftconvolve
    import argparse
    import numpy as np
    import os

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input image path', metavar='PATH')
    parser.add_argument('-o', '--output', help='output base path', metavar='PATH')
    parser.add_argument('-s1xy', type=float, default=13.0, help="smaller xy sigma")
    parser.add_argument('-s1z', type=float, default=7.0, help="smaller z sigma")
    parser.add_argument('-s2xy', type=float, default=26.0, help="larger xy sigma")
    parser.add_argument('-s2z', type=float, default=14.0, help="larger z sigma")
    args = parser.parse_args()

    s1xy = args.s1xy
    s1z = args.s1z
    s2xy = args.s2xy
    s2z = args.s2z

    logger.info('preparing DoG kernel...')
    sizexy = int(args.s2xy) * 2 -1
    sizez = int(args.s2z) * 2 - 1
    dog_kernel = np.zeros((sizez, sizexy, sizexy))
    metaxy = (sizexy - 1) / 2
    metaz = (sizez - 1) / 2

    for x in np.arange(sizexy):
        for y in np.arange(sizexy):
            for z in np.arange(sizez):
                dog_kernel[z ,y, x] = np.exp(- ((x-metaxy)**2 + (y-metaxy)**2)/s1xy**2 - ((z - metaz) /s1z)**2) / \
                                      (s1xy * s1xy * s1z) - np.exp(- ((x-metaxy)**2 + (y-metaxy)**2)/s2xy**2 - \
                                      ((z - metaz) / s2z)**2 ) / (s2xy * s2xy * s2z)

    logger.info('filtering image...')
    handle = InputFile(args.input)
    inimage = handle.whole()
    conv = fftconvolve(inimage, dog_kernel, mode='same')

    base, file = os.path.split(args.input)
    name, ext = os.path.splitext(file)
    if not os.path.exists(args.output):
        os.makedirs(args.output, 0o775)
    path = os.path.join(args.output, name + "_dog.tiff")
    logger.info('saving output to %s...', path)
    tiff.imwrite(path, conv.astype('uint16'))


if __name__ == "__main__":
    main()
