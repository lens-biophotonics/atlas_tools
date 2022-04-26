#!/usr/bin/env python3


def main():
    import logging
    import coloredlogs
    import os
    import argparse
    import numpy as np

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help="input folder", metavar='PATH')
    parser.add_argument('-o', '--output', help="output folder", metavar='PATH')

    args = parser.parse_args()

    lista = os.listdir(args.input)
    for name in lista:
        if '.npy' in name:
            path = os.path.join(args.input, name)
            a = np.load(path)
            logger.info('opened file %s', path)
            b = np.zeros(a.shape)
            for i in range(a.shape[0]):
                b[i, 0:3] = a[i, 0:3]
                b[i, 3] = 5
                b[i, 4] = 1
                b[i, 5] = 0
            nome, ext = os.path.splitext(name)
            outname = nome + ".marker"
            np.savetxt(outname, b, header='x, y, z, radius, shape, name, comment', fmt='%5.2f', delimiter=',')
            logger.info('marker file saved to %s', outname)


if __name__ == "__main__":
    main()
