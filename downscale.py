#!/usr/bin/env python3


def main():
    import numpy as np
    from zetastitcher import VirtualFusedVolume
    import logging
    import coloredlogs
    import argparse
    import tifffile as tiff
    from skimage.transform import rescale

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help="vfv yml path", metavar='PATH')
    parser.add_argument('-o', '--output', help="downscale base path", metavar='PATH')
    parser.add_argument('-xy', '--xyscale', help="xy scaling from full-res to analysis-res", type=int,
                        default=6)
    parser.add_argument('-z', '--zscale', help="z scaling from full-res to analysis-res", type=int,
                        default=2)
    args = parser.parse_args()

    vfv = VirtualFusedVolume(args.input)
    scale_tup = tuple((1/args.zscale, 1/args.xyscale, 1/args.xyscale))

    n_files = int(vfv.shape[0]/args.zscale)
    for i in np.arange(n_files):
        temp = vfv[(i*args.zscale):((i+1)*args.zscale), ...]
        image = rescale(temp, scale_tup)
        filename = args.output + "_%03d.tiff" % i
        tiff.imwrite(filename, image)


if __name__ == "__main__":
    main()
