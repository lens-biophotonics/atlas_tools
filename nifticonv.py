#!/usr/bin/python3

import argparse
import logging
from niftiutils import convertImage


def main():

    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('in_path')
    parser.add_argument('-o', '--output', help="output file path", metavar='PATH', default='NULL')
    parser.add_argument('-r', '--reverse', help="reverse along z and x and expand with black volume along z",
                        action='store_true')
    parser.add_argument('-bs', '--black-slices', type=int, default=100, help="number of black slices to be added",
                        metavar='SLICES')
    parser.add_argument('-x-scale', type=float, default=2, help="downscaling factor along x")
    parser.add_argument('-y-scale', type=float, default=2, help="downscaling factor along y")
    parser.add_argument('-z-scale', type=float, default=2, help="downscaling factor along z")
    parser.add_argument('-x-pix', type=float, default=0.0104, help="initial voxel size along x (in mm)")
    parser.add_argument('-y-pix', type=float, default=0.0104, help="initial voxel size along y (in mm)")
    parser.add_argument('-z-pix', type=float, default=0.01, help="initial voxel size along z (in mm)")
    parser.add_argument('-nl', '--noise-level', type=int, default=110, help="average noise to be subtracted from image",
                        metavar='LEVEL')
    parser.add_argument('-g', '--gamma', type=float, default=0.3, help="gamma factor")
    parser.add_argument('-mp', '--max-percentile', type=float, default=99.9, help="percentage of non-saturated voxels",
                        metavar='PERCENT')
    args = parser.parse_args()

    convertImage(args.in_path, out_path=args.output, reverse=args.reverse, bs=args.black_slices, x_scale=args.x_scale,
                 y_scale=args.y_scale, z_scale=args.z_scale, x_pix=args.x_pix, y_pix=args.y_pix, z_pix=args.z_pix,
                 nl=args.noise_level, gamma=args.gamma, mp=args.max_percentile)
    logger.info('done')


if __name__ == "__main__":
    main()
