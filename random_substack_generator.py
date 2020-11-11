#!/usr/bin/python3


def main():
    import logging
    import coloredlogs
    import os
    import argparse
    import skimage.external.tifffile as tiff
    from zetastitcher import VirtualFusedVolume
    import random
    import numpy as np

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help="input stitch yml file", metavar='PATH')
    parser.add_argument('-o', '--output', help="output base path", metavar='PATH')
    parser.add_argument('-s', '--suffix', help="output file suffix", metavar='SUFFIX')
    parser.add_argument('-n', '--nstacks', type=int, default=13, help="number of substacks to generate")
    parser.add_argument('-xs', '--xsize', type=int, default=480, help="x size of the substack (in voxels)")
    parser.add_argument('-ys', '--ysize', type=int, default=480, help="y size of the substack (in voxels)")
    parser.add_argument('-zs', '--zsize', type=int, default=480, help="z size of the substack (in voxels)")
    parser.add_argument('-t', '--threshold', type=int, default=150, help="threshold of 95% percentile")

    args = parser.parse_args()

    vfv = VirtualFusedVolume(args.input)
    random.seed()
    limits = vfv.shape
    n = 0

    while n < args.nstacks:
        logger.info('generating substack # %d' % n)
        x = random.randint(0, limits[2]-(args.xsize+1))
        y = random.randint(0, limits[1]-(args.ysize+1))
        z = random.randint(0, limits[0]-(args.zsize+1))

        temp = vfv[z:(z+args.zsize), y:(y+args.ysize), x:(x+args.xsize)]
        if np.percentile(temp, 95) > args.threshold:
            path = os.path.join(args.output, args.suffix + '_%04d_%05d_%05d.tiff' % (z, y, x))
            tiff.imsave(path, temp)
            n = n+1


if __name__ == "__main__":
    main()
