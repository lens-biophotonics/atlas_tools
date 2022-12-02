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
    parser.add_argument('-s', '--singleside', help="only one side present (no front + back)", action='store_true',
                        default=False)
    parser.add_argument('-i', '--singleillumination', help="only one illumination present (no left + right)",
                        action='store_true', default=False)
    parser.add_argument('-c', '--singlechannel', help="only one channel", action='store_true', default=False)
    parser.add_argument('-r', '--rightchannel', help="name of the right channel", default='638')
    parser.add_argument('-l', '--leftchannel', help="name of the left channel", default='561')
    args = parser.parse_args()

    l = args.leftchannel
    r = args.rightchannel

    base = args.basepath
    if base[-1] == '/':
        base = base[:-1]
    if not os.path.exists(base):
        os.makedirs(base, 0o775)

    if args.singleside:
        side = ['dummy']
    else:
        side = ['_front', '_back']

    if args.singlechannel:
        ch = [['dummy'], ['dummy']]
    else:
        ch = [[l, '_l'], [r, '_r']]

# 1st iteration: sides (front, back). a1 is base when no double side is enabled, and base_front or base_back else
    for s in side:
        if s == 'dummy':
            d1 = base
            s1 = base
        else:
            d1 = merge_and_create(base, s)
            s1 = base + '_' + s

# 2nd iteration: source is duplicated in case of multiple illuminations
        if args.singleillumination:
            ill = s1
        else:
            ill = [s1 + '_sx', s1 + '_dx']

# 3rd iteration: channels (561, 638, etc.). a2 is a1 for single channel datasets, and a1_channel for multichannel
        for i in ill:
            for c in ch:
                if c == 'dummy':
                    d2 = d1
                else:
                    d2 = merge_and_create(d1, c[0])

                d2d = merge_and_create(d2, 'ds')
                d2z = merge_and_create(d2, 'zip')

                move_folder(i, d2d, d2z, c)
            os.rmdir(i)


def merge_and_create(base, des):
    import os
    full = os.path.join(base, des)
    if not os.path.exists(full):
        os.makedirs(full, 0o775)
    return full


def move_folder(source, destd, destz, ch):
    import os
    from shutil import move
    lista = os.listdir(source)
    if ch[1] == 'dummy':
        for file in lista:
            if 'tiff' in file:
                start = os.path.join(source, file)
                stop = os.path.join(destd, file)
                move(start, stop)
            if 'zip' in file:
                start = os.path.join(source, file)
                stop = os.path.join(destz, file)
                move(start, stop)
    else:
        for file in lista:
            if ch[1] in file and 'tiff' in file:
                start = os.path.join(source, file)
                stop = os.path.join(destd, file)
                move(start, stop)
            if ch[1] in file and 'zip' in file:
                start = os.path.join(source, file)
                stop = os.path.join(destz, file)
                move(start, stop)


if __name__ == "__main__":
    main()
