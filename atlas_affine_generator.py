#!/usr/bin/env python3

def main():
    import logging
    import coloredlogs
    from zetastitcher import InputFile
    import numpy as np
    import argparse
    import nibabel as nib

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--image', help="image to be registered", metavar='PATH')
    parser.add_argument('-r', '--reference', help="reference atlas image", metavar='PATH')
    parser.add_argument('-o', '--output', help="output file", metavar='PATH')
    args = parser.parse_args()

    image = nib.load(args.image)
    i_shape = image.shape
    logger.info("image shape is %d x %d x %d", i_shape[0], i_shape[1], i_shape[2])
    i_pixdim = image.header['pixdim']
    i_data = image.get_fdata()
    i_data[i_data > 10] = 10
    i_data *= 25
    i_cov = moments_cov(i_data)
    ix = i_shape[0] * i_pixdim[1]
    iy = i_shape[1] * i_pixdim[2]
    iz = i_shape[2] * i_pixdim[3]

    ref = nib.load(args.reference)
    r_shape = ref.shape
    logger.info("reference shape is %d x %d x %d", r_shape[0], r_shape[1], r_shape[2])
    r_pixdim = ref.header['pixdim']
    r_data = ref.get_fdata()
    r_data[r_data > 10] = 10
    r_data *= 25
    r_cov = moments_cov(r_data)
    rx = r_shape[0] * r_pixdim[1]
    ry = r_shape[1] * r_pixdim[2]
    rz = r_shape[2] * r_pixdim[3]

    i_eigval, i_eigvec = np.linalg.eig(i_cov)
    idx = i_eigval.argsort()[::-1]
    i_eigval = i_eigval[idx]
    i_eigvec = i_eigvec[:, idx]
    i_eigvec = i_eigvec[:, [1, 0, 2]]

    r_eigval, r_eigvec = np.linalg.eig(r_cov)
    idx = r_eigval.argsort()[::-1]
    r_eigval = r_eigval[idx]

    scalevec = i_eigval/r_eigval
    scale = np.sqrt(scalevec.mean())

    sinus = i_eigvec[0, 1] * np.sign(i_eigvec[0, 0])
    cosinus = np.abs(i_eigvec[0, 0])

    a11 = scale * cosinus
    a12 = scale * sinus
    a13 = 0
    a21 = -a12
    a22 = a11
    a23 = 0
    a31 = 0
    a32 = 0
    a33 = scale
    a41 = (ix / 2) * (1 - cosinus) - (iy / 2) * sinus
    a42 = (iy / 2) * (1 - cosinus) + (ix / 2) * sinus
    a43 = 1

    file = open(args.output, "w")
    file.write("#Insight Transform File V1.0\n")
    file.write("#Transform 0\n")
    file.write("Transform: AffineTransform_double_3_3\n")
    file.write("Parameters: %0.2f %0.2f %0.2f %0.2f %0.2f %0.2f %0.2f %0.2f %0.2f %0.2f %0.2f %0.2f\n"
               % (a11, a12, a13, a21, a22, a23, a31, a32, a33, a41, a42, a43))
    file.write("FixedParameters: 0.00 0.00 0.00\n")
    file.close()


def raw_moment(image, xp, yp, zp):
    import numpy as np
    x, y, z = image.shape
    x_ind, y_ind, z_ind = np.mgrid[:x, :y, :z]
    return (image * z_ind**zp * y_ind**yp * x_ind**xp).sum()


def moments_cov(image):
    import numpy as np
    image_sum = image.sum()
    m100 = raw_moment(image, 1, 0, 0)
    m010 = raw_moment(image, 0, 1, 0)
    m001 = raw_moment(image, 0, 0, 1)
    x_c = m100/image_sum
    y_c = m010/image_sum
    z_c = m001/image_sum
    u200 = (raw_moment(image, 2, 0, 0) - x_c * m100)/image_sum
    u020 = (raw_moment(image, 0, 2, 0) - y_c * m010)/image_sum
    u002 = (raw_moment(image, 0, 0, 2) - z_c * m001)/image_sum
    u110 = (raw_moment(image, 1, 1, 0) - x_c * m010)/image_sum
    u101 = (raw_moment(image, 1, 0, 1) - x_c * m001)/image_sum
    u011 = (raw_moment(image, 0, 1, 1) - y_c * m001)/image_sum
    cov = np.array([[u200, u110, u101], [u110, u020, u011], [u101, u011, u002]])
    return cov


if __name__ == "__main__":
    main()