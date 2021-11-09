#!/usr/bin/python3


def main():
    import logging
    import coloredlogs
    import argparse
    from zetastitcher import InputFile
    import tifffile as tiff
    from scipy.ndimage import binary_opening as opening

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help="input tiff file", metavar='PATH')
    parser.add_argument('-o', '--output', help="output tiff file", metavar='PATH')
    parser.add_argument('-t', '--threshold', type=int, default=110, help="brightness threshold")

    args = parser.parse_args()

    logger.info('opening %s...', args.input)
    handle = InputFile(args.input)
    in_image = handle.whole()
    out_image = ((in_image > args.threshold))
    out_image = opening(out_image, iterations=2)
    logger.info('writing result to %s...', args.output)
    tiff.imwrite(args.output, (out_image*255).astype('uint8'), compression='zlib')


if __name__ == "__main__":
    main()
