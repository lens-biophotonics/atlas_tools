#!/usr/bin/python3

b2f_dist = 2.68
excess_border = 10


def main():
    from niftiutils import convertImage
    import logging
    import coloredlogs
    import os
    import argparse
    import skimage.external.tifffile as tiff

    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--front', help='front side path', metavar='PATH')
    parser.add_argument('-b', '--back', help='back side path', metavar='PATH')
    parser.add_argument('-o', '--output', help="output base path", metavar='PATH')
    parser.add_argument('-x-final', type=float, default=0.025, help="final voxel size along x (in mm)")
    parser.add_argument('-y-final', type=float, default=0.025, help="final voxel size along y (in mm)")
    parser.add_argument('-z-final', type=float, default=0.025, help="final voxel size along z (in mm)")
    parser.add_argument('-x-pix', type=float, default=0.0104, help="initial voxel size along x (in mm)")
    parser.add_argument('-y-pix', type=float, default=0.0104, help="initial voxel size along y (in mm)")
    parser.add_argument('-z-pix', type=float, default=0.01, help="initial voxel size along z (in mm)")
    parser.add_argument('-nl', '--noise-level', type=int, default=110, help="average noise to be subtracted from image",
                        metavar='LEVEL')
    parser.add_argument('-g', '--gamma', type=float, default=0.3, help="gamma factor")
    parser.add_argument('-mp', '--max-percentile', type=float, default=99.9, help="percentage of non-saturated voxels",
                        metavar='PERCENT')
    args = parser.parse_args()

    front = tiff.TiffFile(args.front)
    back = tiff.TiffFile(args.back)

    logger.info('processing front image...')
    black = int((len(back.pages) - b2f_dist/args.z_pix + excess_border)*(args.z_pix/args.z_final))
    base, front_file = os.path.split(args.front)
    name, ext = os.path.splitext(front_file)

    # check if output folder exists
    if not os.path.exists(args.output):
        os.makedirs(args.output, 0o775)

    fc_path = os.path.join(args.output, name + ".nii.gz")
    fc_path_nogamma = os.path.join(args.output, name + "_nogamma.nii.gz")
    convertImage(args.front, out_path=fc_path, reverse=True, bs=black, x_final=args.x_final, y_final=args.y_final,
                 z_final=args.z_final, x_pix=args.x_pix, y_pix=args.y_pix, z_pix=args.z_pix, nl=args.noise_level,
                 gamma=args.gamma, mp=args.max_percentile)
    convertImage(args.front, out_path=fc_path_nogamma, reverse=True, bs=black, x_final=args.x_final,
                 y_final=args.y_final, z_final=args.z_final, x_pix=args.x_pix, y_pix=args.y_pix, z_pix=args.z_pix,
                 nl=args.noise_level, gamma=1, mp=args.max_percentile)

    logger.info('processing back image...')
    base, back_file = os.path.split(args.back)
    name, ext = os.path.splitext(back_file)
    bc_path = os.path.join(args.output, name + ".nii.gz")
    bc_path_nogamma = os.path.join(args.output, name + "_nogamma.nii.gz")
    convertImage(args.back, out_path=bc_path, x_final=args.x_final, y_final=args.y_final, z_final=args.z_final,
                 x_pix=args.x_pix, y_pix=args.y_pix, z_pix=args.z_pix, nl=args.noise_level, gamma=args.gamma,
                 mp=args.max_percentile)
    convertImage(args.back, out_path=bc_path_nogamma, x_final=args.x_final, y_final=args.y_final, z_final=args.z_final,
                 x_pix=args.x_pix, y_pix=args.y_pix, z_pix=args.z_pix, nl=args.noise_level, gamma=1,
                 mp=args.max_percentile)

    logger.info('writing initial transform file...')
    shift = len(front.pages)*args.z_pix-b2f_dist
    path = os.path.join(args.output, "init.txt")
    file = open(path, "w")
    file.write("#Insight Transform File V1.0\n")
    file.write("#Transform 0\n")
    file.write("Transform: AffineTransform_double_3_3\n")
    file.write("Parameters: 1 0 0 0 1 0 0 0 1 0 0 -%0.2f\n" % shift)
    file.write("FixedParameters: 0 0 0\n")
    file.close()


if __name__ == "__main__":
    main()
