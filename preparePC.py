#!/usr/bin/env python3


def main():
    import logging
    import coloredlogs
    import pandas as pd
    import os
    import argparse
    from zetastitcher import VirtualFusedVolume

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--front', help="front .csv file", metavar='PATH')
    parser.add_argument('-b', '--back', help="back .csv file", metavar='PATH')
    parser.add_argument('-o', '--output', help="output base path", metavar='PATH')
    parser.add_argument('-fy', '--front_yml', help="front stitch.yml file", metavar='PATH')
    parser.add_argument('-by', '--back_yml', help="back stitch.yml file", metavar='PATH')
    parser.add_argument('-r', '--reverse', type=bool, default=False, help="reverse front?")
    parser.add_argument('-xy-pix', type=float, default=0.00065, help="voxel size along xy (in mm)")
    parser.add_argument('-z-pix', type=float, default=0.002, help="voxel size along z (in mm)")
    parser.add_argument('-xy-pc', type=float, default=0.001, help="xy point cloud units (in mm)")
    parser.add_argument('-z-pc', type=float, default=0.001, help="z point cloud units (in mm)")

    args = parser.parse_args()

    logger.info('processing front point cloud...')
    front = pd.read_csv(args.front)
    front = front[['x', 'y', 'z']]

    if args.reverse:
        front['x'] *= args.xy_pc
        front['y'] *= args.xy_pc
        front['z'] *= args.z_pc
    else:
        fvfv = VirtualFusedVolume(args.front_yml)
        fshape = fvfv.shape
        front['x'] = (fshape[2] * args.xy_pix) - (front['x'] * args.xy_pc)
        front['y'] *= args.xy_pc
        front['z'] = (fshape[0] * args.z_pix) - (front['z'] * args.z_pc)

    if not os.path.exists(args.output):
        os.makedirs(args.output, 0o775)

    base, front_file = os.path.split(args.front)
    name, ext = os.path.splitext(front_file)
    out_path = os.path.join(args.output, name + "_ants.csv")
    front.to_csv(out_path, index=False)
    logger.info('point cloud saved to %s', out_path)

    logger.info('processing back point cloud...')
    back = pd.read_csv(args.back)
    back = back[['x', 'y', 'z']]

    if args.reverse:
        bvfv = VirtualFusedVolume(args.back_yml)
        bshape = bvfv.shape
        back['x'] = (bshape[2] * args.xy_pix) - (back['x'] * args.xy_pc)
        back['y'] *= args.xy_pc
        back['z'] = (bshape[0] * args.z_pix) - (back['z'] * args.z_pc)
    else:
        back['x'] *= args.xy_pc
        back['y'] *= args.xy_pc
        back['z'] *= args.z_pc

    base, back_file = os.path.split(args.back)
    name, ext = os.path.splitext(back_file)
    out_path = os.path.join(args.output, name + "_ants.csv")
    back.to_csv(out_path, index=False)
    logger.info('point cloud saved to %s', out_path)


if __name__ == "__main__":
    main()
