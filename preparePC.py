#!/usr/bin/python3


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
    parser.add_argument('-y', '--yml', help="front stitch.yml file", metavar='PATH')
    parser.add_argument('-xy-pix', type=float, default=0.00065, help="initial voxel size along x and y (in mm)")
    parser.add_argument('-z-pix', type=float, default=0.002, help="initial voxel size along z (in mm)")

    args = parser.parse_args()

    logger.info('processing front point cloud...')
    front = pd.read_csv(args.front)
    front = front[['x', 'y', 'z']]

    vfv = VirtualFusedVolume(args.yml)
    shape = vfv.shape

    front['x'] = (shape[2] - front['x']) * args.xy_pix
    front['y'] = front['y'] * args.xy_pix
    front['z'] = (shape[0] - front['z']) * args.z_pix

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

    back['x'] = back['x'] * args.xy_pix
    back['y'] = back['y'] * args.xy_pix
    back['z'] = back['z'] * args.z_pix

    base, front_file = os.path.split(args.front)
    name, ext = os.path.splitext(front_file)
    out_path = os.path.join(args.output, name + "_ants.csv")
    front.to_csv(out_path, index=False)
    logger.info('point cloud saved to %s', out_path)
