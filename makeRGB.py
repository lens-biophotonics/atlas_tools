#!/usr/bin/env python3


def main():
    import numpy as np
    import tifffile as tiff
    import os
    import cv2
    import logging
    import coloredlogs
    import argparse

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--red', help="red files folder", metavar='PATH')
    parser.add_argument('-g', '--green', help="green files folder", metavar='PATH')
    parser.add_argument('-o', '--output', help="RGB files folder", metavar='PATH')
    parser.add_argument('-x', help="x translation", type=int, default=-3)
    parser.add_argument('-y', help="y translation", type=int, default=-5)
    parser.add_argument('-min_g', help="minimum green value", type=int, default=100)
    parser.add_argument('-max_g', help="maximum green value", type=int, default=3500)
    parser.add_argument('-min_r', help="minimum red value", type=int, default=100)
    parser.add_argument('-max_r', help="maximum red value", type=int, default=900)
    args = parser.parse_args()

    lista1 = sorted(os.listdir(args.green))
    lista2 = sorted(os.listdir(args.red))

    for element in lista1:
        if 'tif' in element:
            break
    prova = tiff.imread(os.path.join(args.green, element))

    color = np.zeros((3, prova.shape[0], prova.shape[1])).astype('uint8')

    for n in range(len(lista1)):
        red = (np.clip(((tiff.imread(os.path.join(args.red, lista2[n])).astype('float') - args.min_r) /
                        (args.max_r - args.min_r)), 0, 1) * 255).astype('uint8')
        green = (np.clip(((tiff.imread(os.path.join(args.green, lista1[n])).astype('float') - args.min_g) /
                          (args.max_g - args.min_g)), 0, 1) * 255).astype('uint8')
        green2 = translate(green, args.x, args.y)
        color[0, ...] = red[...]
        color[1, ...] = green2[...]
        tiff.imwrite(os.path.join(args.output, lista1[n]), np.moveaxis(color, 0, -1), compression='zlib',
                     photometric='rgb', imagej=True)
        if (n % 100) == 0:
            logger.info('processed %d files of %d', n, len(lista1))


def translate(image, x, y):
    import cv2
    import numpy as np
    rows, cols = image.shape[:2]
    translation_matrix = np.float32([[1, 0, x], [0, 1, y]])
    translated_image = cv2.warpAffine(image, translation_matrix, (cols, rows), borderValue=(0, 0, 0))
    return translated_image


if __name__ == "__main__":
    main()
