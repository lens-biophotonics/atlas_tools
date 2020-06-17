#!/usr/bin/python3


def main():
    import logging
    import coloredlogs
    import argparse
    import skimage.external.tifffile as tiff
    import scipy.ndimage.binary_opening as opening

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help="input tiff file", metavar='PATH')
    parser.add_argument('-o', '--output', help="output tiff file", metavar='PATH')
    parser.add_argument('-t', '--threshold', type=int, default=110, help="brightness threshold")

    args = parser.parse_args()

    logger.info('opening %s...', args.input)
    in_image = tiff.imread(args.input)
    out_image = ((in_image > args.threshold)*255).astype('uint8')
    out_image = opening(out_image, iterations=2)
    logger.info('writing result to %s...', args.output)
    tiff.imsave(args.output, out_image)


if __name__ == "__main__":
    main()
