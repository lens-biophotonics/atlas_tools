#!/usr/bin/env python3


def main():
    import logging
    import coloredlogs
    import argparse
    import tifffile as tiff
    from skimage import measure
    from skimage.util import map_array
    import os

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help="input image path", metavar='PATH')
    #parser.add_argument('-o', '--output', help="output image path", metavar='PATH')
    parser.add_argument('-t', '--threshold', help="intensity threshold", type=int, default=200)
    parser.add_argument('-vmin', help="minimum volume (in voxels)", type=int, default=300)
    parser.add_argument('-vmax', help="maximum volume (in voxels)", type=int, default=2000)

    args = parser.parse_args()

    logger.info('loading input image...')
    image = tiff.imread(args.input)

    logger.info('processing image...')
    blob = (image > args.threshold).astype('uint8')
    labels = measure.label(blob, background=0)
    reg = measure.regionprops_table(labels, properties=('label','area',))
    condition = (reg['area'] > args.vmin) & (reg['area'] < args.vmax)
    inlab = reg['label']
    outlab = inlab * condition
    filterlab = map_array(labels, inlab, outlab)

    a = os.path.splitext(args.input)
    output = a[0] + '_filter.tif'
    logger.info('writing output image...')
    tiff.imwrite(output, filterlab.astype('uint8'))


if __name__ == "__main__":
    main()
