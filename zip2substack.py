#!/usr/bin/env python3


def main():
    from zetastitcher import InputFile
    import tifffile as tiff
    import logging
    import coloredlogs
    import argparse

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='INFO', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help="input zip file", metavar='PATH')
    parser.add_argument('-o', '--output', help="output tiff file", metavar='PATH')
    parser.add_argument('-s', '--slice', help="first slice", type=int)
    parser.add_argument('-l', '--length', help="number of slices", type=int, default=1)

    args = parser.parse_args()

    logger.info('opening input file...')
    a = InputFile(args.input)
    b = a[args.slice:(args.slice + args.length), ...]

    logger.info('saving output tiff...')
    tiff.imwrite(args.output, b)


if __name__ == "__main__":
    main()
