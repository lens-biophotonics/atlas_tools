#!/usr/bin/env python3


def main():
    from niftiutils import convertImage
    import logging
    import coloredlogs
    import os
    import argparse
    from zetastitcher import InputFile
    from scipy.ndimage import gaussian_filter

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-y', '--yellow', help='yellow image path', metavar='PATH')
    parser.add_argument('-r', '--red', help='red image path', metavar='PATH')
    parser.add_argument('-o', '--output', help="output base path", metavar='PATH')
    parser.add_argument('-x-final', type=float, default=0.025, help="final voxel size along x (in mm)")
    parser.add_argument('-y-final', type=float, default=0.025, help="final voxel size along y (in mm)")
    parser.add_argument('-z-final', type=float, default=0.025, help="final voxel size along z (in mm)")
    parser.add_argument('-x-pix', type=float, default=0.0104, help="initial voxel size along x (in mm)")
    parser.add_argument('-y-pix', type=float, default=0.0104, help="initial voxel size along y (in mm)")
    parser.add_argument('-z-pix', type=float, default=0.01, help="initial voxel size along z (in mm)")
    parser.add_argument('-nl', '--noiselevel', type=int, default=110, help="average noise to be subtracted from image",
                        metavar='LEVEL')
    parser.add_argument('-g', '--gamma', type=float, default=0.3, help="gamma factor")
    parser.add_argument('-s', '--sigma', type=float, default=5.0, help="smoothing sigma")
    parser.add_argument('-mp', '--max-percentile', type=float, default=99.9, help="percentage of non-saturated voxels",
                        metavar='PERCENT')
    parser.add_argument('-f', '--flip', help="vertically flip image", action='store_true', default=False)
    args = parser.parse_args()

    logger.info('extracting mask from red image...')
    red = InputFile(args.red)
    rimage = red.whole()
    rimage = gaussian_filter(rimage, args.sigma)
    rimage = (rimage > args.noiselevel)

    logger.info('processing yellow image...')
    # check if output folder exists
    if not os.path.exists(args.output):
        os.makedirs(args.output, 0o775)
    path = os.path.join(args.output, name + ".nii.gz")
    path_nogamma = os.path.join(args.output, name + "_nogamma.nii.gz")

    convertImage(args.yellow, out_path=path, x_final=args.x_final, y_final=args.y_final, z_final=args.z_final,
                 x_pix=args.x_pix, y_pix=args.y_pix, z_pix=args.z_pix, nl=args.noiselevel, gamma=args.gamma,
                 mp=args.max_percentile, flip=args.flip, mask=rimage)
    convertImage(args.yellow, out_path=path_nogamma, x_final=args.x_final, y_final=args.y_final,
                 z_final=args.z_final, x_pix=args.x_pix, y_pix=args.y_pix, z_pix=args.z_pix,
                 nl=args.noiselevel, gamma=1, mp=args.max_percentile, flip=args.flip, mask=rimage)


if __name__ == "__main__":
    main()
