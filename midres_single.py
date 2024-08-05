#!/usr/bin/env python3


def main():
    import numpy as np
    import logging
    import coloredlogs
    import argparse
    import tifffile as tiff
    from skimage.transform import resize

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help="input file", metavar='PATH')
    parser.add_argument('-o', '--output', help="output file", metavar='PATH')
    parser.add_argument('-xy', '--xyscale', help="xy scaling from full-res to analysis-res", type=float,
                        default=8)
    parser.add_argument('-z', '--zscale', help="z scaling from full-res to analysis-res", type=float,
                        default=2.5)
    parser.add_argument('-s0', help="minimum slice", type=int, default=0)
    parser.add_argument('-s1', help="maximum slice", type=int, default=1000000000)
    args = parser.parse_args()

    logger.info('opening input TIFF file...')
    img = tiff.TiffFile(args.input)
    p = img.pages[0]
    shape = (len(img.pages), int(p.shape[1] / args.xyscale), int(p.shape[0] / args.xyscale))
    mid = np.zeros(shape).astype(p.dtype)

    for i in range(args.s0, args.s1):
        p = img.pages[i]
        mid[i] = resize(p.asarray(), (mid.shape[1], mid.shape[2]), preserve_range=True)
        i += 1

    mid2 = resize(mid, (int(mid.shape[0] / args.zscale), mid.shape[1], mid.shape[2]), preserve_range=True)

    logger.info('writing output image')
    tiff.imwrite(args.output, mid2.astype(p.dtype))


if __name__ == "__main__":
    main()
