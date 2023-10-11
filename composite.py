#!/usr/bin/env python3


def main():
    import logging
    import coloredlogs
    import tifffile
    import os
    import argparse
    import numpy as np
    from zetastitcher import InputFile
    from skimage.transform import rescale

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--red', help="RED images folder", metavar='PATH')
    parser.add_argument('-g', '--green', help="GREEN images folder", metavar='PATH')
    parser.add_argument('-o', '--output', help="output folder", metavar='PATH')
    parser.add_argument('-z', '--zip', help="zip files as input", action='store_true', default=False)

    args = parser.parse_args()

    scale = (0.5, 0.25, 0.25) # hardcoded
    green_dir = os.listdir(args.green)
    red_dir = os.listdir(args.red)
    for name in green_dir:
        if 'x_' in name:
            green_path = os.path.join(args.green, name)
            handle = InputFile(green_path)
            green = handle.whole()
            if args.zip:
                green = rescale(green, scale, channel_axis=None, anti_aliasing=False, preserve_range=True)
            logger.info('opened GREEN image %s', green_path)
            token = name[0:17]
            red_name = next((name2 for name2 in red_dir if token in name2), None)
            red_path = os.path.join(args.red, red_name)
            handle = InputFile(red_path)
            red = handle.whole()
            if args.zip:
                red = rescale(red, scale, channel_axis=None, anti_aliasing=False, preserve_range=True)
            logger.info('opened RED image %s', red_path)
            shape = green.shape
            merge = np.zeros((shape[0], 2, shape[1], shape[2])).astype(green.dtype)
            merge[:, 0, ...] = red
            merge[:, 1, ...] = green
            merge_path = os.path.join(args.output, name)
            tifffile.imwrite(merge_path, merge, imagej=True, photometric=True, metadata={'mode':'composite'},
                             compression='zlib')
            logger.info('composite image saved to %s', merge_path)


if __name__ == "__main__":
    main()
