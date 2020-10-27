#!/usr/bin/python3


def main():
    from niftiutils import nii2tif
    import logging
    import coloredlogs
    import argparse

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input nifti image path', metavar='PATH')
    parser.add_argument('-o', '--output', help="output tiff image path", metavar='PATH')
    args = parser.parse_args()

    nii2tif(args.input, args.output)


if __name__ == "__main__":
    main()
