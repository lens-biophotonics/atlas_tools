#!/usr/bin/python3


def main():
    from niftiutils import tif2nii
    import logging
    import coloredlogs
    import argparse

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input tiff image path', metavar='PATH')
    parser.add_argument('-o', '--output', help="output nifti image path", metavar='PATH')
    parser.add_argument('-x-pix', type=float, default=0.025, help="initial voxel size along x (in mm)")
    parser.add_argument('-y-pix', type=float, default=0.025, help="initial voxel size along y (in mm)")
    parser.add_argument('-z-pix', type=float, default=0.025, help="initial voxel size along z (in mm)")
    args = parser.parse_args()

    tif2nii(args.input, args.output, args.x_pix, args.y_pix, args.z_pix)


if __name__ == "__main__":
    main()
