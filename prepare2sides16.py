#!/usr/bin/python3

# b2f_dist = 2.68
excess_border = 10


def main():
    from niftiutils import convertImage16
    import logging
    import coloredlogs
    import os
    import argparse
    import skimage.external.tifffile as tiff

    logger = logging.getLogger(__name__)
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
    parser.add_argument('-r', '--reverse', help="revert stack direction", action='store_true', default=False)
    parser.add_argument('--b2f', type=float, default=2.68, help="back-to-front distance (in mm)")
    args = parser.parse_args()

    b2f_dist = args.b2f
    back = tiff.TiffFile(args.back)

    logger.info('processing front image...')
    black = int((len(back.pages) - b2f_dist / args.z_pix + excess_border) * (args.z_pix / args.z_final))
    base, front_file = os.path.split(args.front)
    name, ext = os.path.splitext(front_file)

    # check if output folder exists
    if not os.path.exists(args.output):
        os.makedirs(args.output, 0o775)

    fc_path = os.path.join(args.output, name + "16bit.nii.gz")
    convertImage16(args.front, out_path=fc_path, expand=True, bs=black, x_final=args.x_final, y_final=args.y_final,
                   z_final=args.z_final, x_pix=args.x_pix, y_pix=args.y_pix, z_pix=args.z_pix, reverse=not args.reverse)

    logger.info('processing back image...')
    base, back_file = os.path.split(args.back)
    name, ext = os.path.splitext(back_file)
    bc_path = os.path.join(args.output, name + "16bit.nii.gz")
    convertImage16(args.back, out_path=bc_path, x_final=args.x_final, y_final=args.y_final, z_final=args.z_final,
                   x_pix=args.x_pix, y_pix=args.y_pix, z_pix=args.z_pix, reverse=args.reverse)


if __name__ == "__main__":
    main()
