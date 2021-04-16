#!/usr/bin/python3


def main():
    import logging
    import coloredlogs
    import pandas as pd
    import argparse

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--front', help="front .csv file", metavar='PATH')
    parser.add_argument('-b', '--back', help="back .csv file", metavar='PATH')
    parser.add_argument('-o', '--output', help="output .csv file", metavar='PATH')
    parser.add_argument('-t', type=float, help="z height of transition (in mm)")

    args = parser.parse_args()

    logger.info('reading front point cloud...')
    front = pd.read_csv(args.front)
    front = front[['x', 'y', 'z']]

    logger.info('reading back point cloud...')
    back = pd.read_csv(args.back)
    back = back[['x', 'y', 'z']]

    logger.info('fusing point clouds...')
    front_2 = front[front['z'] <= args.t]
    back_2 = back[back['z'] > args.t]
    wb = pd.concat([front_2, back_2])
    wb.to_csv(args.output, index=False)
    logger.info('point cloud saved to %s', args.output)


if __name__ == "__main__":
    main()
