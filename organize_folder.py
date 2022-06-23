#!/usr/bin/env python3


def main():
    import os
    import logging
    import coloredlogs
    import argparse

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--basepath', help="base path", metavar='PATH')
    args = parser.parse_args()

    base = args.basepath
    if base[-1] == '/':
        base = base[:-1]
    fd = base + '_front_dx'
    fs = base + '_front_sx'
    bd = base + '_back_dx'
    bs = base + '_back_sx'

    if not os.path.exists(base):
        os.makedirs(base, 0o775)
    f = merge_and_create(base, 'front')
    f5 = merge_and_create(f, '561')
    f5d = merge_and_create(f5, 'ds')
    f5z = merge_and_create(f5, 'zip')
    f6 = merge_and_create(f, '638')
    f6d = merge_and_create(f6, 'ds')
    f6z = merge_and_create(f6, 'zip')
    b = merge_and_create(base, 'back')
    b5 = merge_and_create(b, '561')
    b5d = merge_and_create(b5, 'ds')
    b5z = merge_and_create(b5, 'zip')
    b6 = merge_and_create(b, '638')
    b6d = merge_and_create(b6, 'ds')
    b6z = merge_and_create(b6, 'zip')

    move_folders(bs, b5d, b5z, b6d, b6z)
    move_folders(bd, b5d, b5z, b6d, b6z)
    move_folders(fs, f5d, f5z, f6d, f6z)
    move_folders(fd, f5d, f5z, f6d, f6z)

    os.rmdir(bs)
    os.rmdir(bd)
    os.rmdir(fs)
    os.rmdir(fd)


def merge_and_create(base, des):
    import os
    full = os.path.join(base, des)
    if not os.path.exists(full):
        os.makedirs(full, 0o775)
    return full


def move_folders(base, d5d, d5z, d6d, d6z):
    import os
    from shutil import move
    lista = os.listdir(base)
    for file in lista:
        if '_l' in file and 'tiff' in file:
            source = os.path.join(base, file)
            dest = os.path.join(d5d, file)
            move(source, dest)
        if '_l' in file and 'zip' in file:
            source = os.path.join(base, file)
            dest = os.path.join(d5z, file)
            move(source, dest)
        if '_r' in file and 'tiff' in file:
            source = os.path.join(base, file)
            dest = os.path.join(d6d, file)
            move(source, dest)
        if '_r' in file and 'zip' in file:
            source = os.path.join(base, file)
            dest = os.path.join(d6z, file)
            move(source, dest)


if __name__ == "__main__":
    main()
