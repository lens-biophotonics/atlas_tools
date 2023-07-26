#!/usr/bin/env python3


def main():
    import logging
    import coloredlogs
    import argparse
    import tifffile as tiff
    import numpy as np
    from skimage.morphology import skeletonize
    from skimage.filters import gaussian

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help="input image path", metavar='PATH')
    parser.add_argument('-o', '--output', help="output image path", metavar='PATH')
    parser.add_argument('-sxymin', '--sigmaxymin', help="minimum sigma in xy", type=float, default=4)
    parser.add_argument('-szmin', '--sigmazmin', help="minimum sigma in z", type=float, default=0.5)
    parser.add_argument('-sxymax', '--sigmaxymax', help="maximum sigma in xy", type=float, default=20.1)
    parser.add_argument('-szmax', '--sigmazmax', help="maximum sigma in z", type=float, default=4.51)
    parser.add_argument('-sxys', '--sigmaxystep', help="sigma step in xy", type=float, default=4)
    parser.add_argument('-szs', '--sigmazstep', help="sigma step in z", type=float, default=1)
    parser.add_argument('-s', '--skeleton', help='extract skeleton',  action='store_true', default=False)

    args = parser.parse_args()

    logger.info('loading input image...')
    data = tiff.imread(args.input)
    data = data.astype('float')

    sigmaxy = np.arange(args.sigmaxymin, args.sigmaxymax, args.sigmaxystep)
    sigmaz = np.arange(args.sigmazmin, args.sigmazmax, args.sigmazstep)
    sigmas = np.stack((sigmaz, sigmaxy, sigmaxy), axis=1)

    temp = vesselness(data, sigmas)

    temp = gaussian(temp, sigma=2)
    temp = temp**0.5
    perc = np.percentile(temp, 80)
    temp = (temp>perc).astype('float')

    if args.skeleton:
        sk = skeletonize(temp)
        tiff.imwrite(args.output, (sk * 255).astype('uint8'))
    else:
        tiff.imwrite(args.output, temp.astype('uint8'))


def vesselness(data, sigmas):
    from scipy.ndimage import gaussian_filter1d
    import numpy as np
    i = 1

    for row in sigmas:
        h11 = gaussian_filter1d(data, row[0], axis=0, order=2)
        h22 = gaussian_filter1d(data, row[1], axis=1, order=2)
        h33 = gaussian_filter1d(data, row[2], axis=2, order=2)
        h1 = gaussian_filter1d(data, row[0], axis=0, order=1)
        h2 = gaussian_filter1d(data, row[0], axis=0, order=1)
        h12 = gaussian_filter1d(h1, row[1], axis=1, order=1)
        h13 = gaussian_filter1d(h1, row[2], axis=2, order=1)
        h23 = gaussian_filter1d(h2, row[2], axis=2, order=1)

        eigv1, eigv2, eigv3 = eigenvalues(h11, h22, h33, h12, h13, h23)
        with np.errstate(divide='ignore', invalid='ignore'):
            ra = np.abs(eigv2) / np.abs(eigv3)
            rb = np.abs(eigv1) / np.sqrt(np.abs(eigv2 * eigv3))
            s = np.sqrt(eigv1 ** 2 + eigv2 ** 2 + eigv3 ** 2)
        ra = np.nan_to_num(ra)
        rb = np.nan_to_num(rb)
        s = np.nan_to_num(s)

        alfa = 0.5
        beta = 0.5
        c = 0.5 * np.max(s)

        temp = np.where(np.logical_or((eigv2 > 0), (eigv3 > 0)), 0,
                     (1 - np.exp(-(ra ** 2) / (2 * alfa ** 2))) * np.exp(-(rb ** 2) / (2 * beta ** 2)) * (
                                 1 - np.exp(-(s ** 2) / (2 * c ** 2))))

        if i == 1:
            v = temp
        else:
            v = np.maximum(v, temp)

        i += 1

    return(v)


def eigenvalues(a11, a22, a33, a12, a13, a23):
    import numpy as np

    with np.errstate(divide='ignore', invalid='ignore'):
        p1 = a12 ** 2 + a13 ** 2 + a23 ** 2
        q = a11 + a22 + a33  # trace of the matrix
        p2 = (a11 - q) ** 2 + (a22 - q) ** 2 + (a33 - q) ** 2 + 2 * p1
        p = np.sqrt(p2 / 6)
        r = (1 / (2 * p ** 3)) * (
                (a11 - q) * ((a22 - q) * (a33 - q) - a23 ** 2) - a12 * (a12 * (a33 - q) - a13 * a23) + a13 * (
                    a12 * a23 - a13 * (a22 - q)))
        r = np.nan_to_num(r)
        r = np.clip(r, -1, 1)
        phi = np.arccos(r) / 3

    eig1 = q + 2 * p * np.cos(phi)
    eig3 = q + 2 * p * np.cos(phi + (2 * np.pi / 3))
    eig2 = 3 * q - eig1 - eig3

    eig1 = np.nan_to_num(eig1)
    eig2 = np.nan_to_num(eig2)
    eig3 = np.nan_to_num(eig3)

    eig1, eig2 = np.where(np.abs(eig1) < np.abs(eig2), eig1, eig2), np.where(np.abs(eig1) < np.abs(eig2), eig2, eig1)
    eig2, eig3 = np.where(np.abs(eig2) < np.abs(eig3), eig2, eig3), np.where(np.abs(eig2) < np.abs(eig3), eig3, eig2)
    eig1, eig2 = np.where(np.abs(eig1) < np.abs(eig2), eig1, eig2), np.where(np.abs(eig1) < np.abs(eig2), eig2, eig1)

    return eig1, eig2, eig3


if __name__ == "__main__":
    main()
