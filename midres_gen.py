#!/usr/bin/env python3


def main():
    import numpy as np
    from zetastitcher import VirtualFusedVolume
    import logging
    import coloredlogs
    import argparse
    import tifffile as tiff
    from skimage.transform import resize

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help="vfv yml path", metavar='PATH')
    parser.add_argument('-o', '--output', help="midres image file", metavar='PATH')
    parser.add_argument('-xy', '--xyscale', help="xy scaling from full-res to analysis-res", type=float,
                        default=8)
    parser.add_argument('-z', '--zscale', help="z scaling from full-res to analysis-res", type=float,
                        default=2.5)
    args = parser.parse_args()

    vfv = VirtualFusedVolume(args.input)
    scale_tup = tuple((args.zscale, args.xyscale, args.xyscale))
    out_shape = tuple(int(l / r) for l, r in zip(vfv.shape, scale_tup))
    out_image = np.zeros(out_shape).astype('uint16')
    # temp = np.zeros((args.zscale*2, vfv.shape[1], vfv.shape[2])).astype('uint16')

    for z in np.arange(0, out_image.shape[0], 2):
        temp = vfv[(z * args.zscale):((z + 2) * args.zscale), ...]
        out_image[z:z+2, ...] = resize(temp, (2, out_shape[1], out_shape[2]))

    tiff.imwrite(args.output, out_image, compression='lzw')


if __name__ == "__main__":
    main()
