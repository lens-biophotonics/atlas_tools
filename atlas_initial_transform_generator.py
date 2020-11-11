#!/usr/bin/python3

# this script works referred to the Allen atlas reference (expanded in y) at 25 micron resolution
AX = 11.4  # x size (in mm) of Allen atlas reference
AY = 15.0  # y size (in mm) of Allen atlas reference
AZ = 8.0   # z size (in mm) of Allen atlas reference
AD = 8.5  # maximum distance (in mm) between hippocampi in Allen atlas reference


def main():
    import argparse
    import nibabel as nib
    import numpy as np

    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help='output file path', metavar='PATH')
    parser.add_argument('-d', '--distance', help='maximum distance between hippocampi (in mm)', type=float)
    parser.add_argument('-a', '--angle', help='inclination angle', type=float)
    parser.add_argument('-i', '--image', help='input image path', metavar='PATH')
    args = parser.parse_args()

    image = nib.load(args.image)
    shape = image.shape
    pixdim = image.header['pixdim']
    ix = shape[0] * pixdim[1]
    iy = shape[1] * pixdim[2]
    iz = shape[2] * pixdim[3]

    scale = args.distance/AD
    a11 = scale * np.cos(np.deg2rad(args.angle))
    a12 = -np.sin(np.deg2rad(args.angle))
    a13 = 0
    a21 = -a12
    a22 = a11
    a23 = 0
    a31 = 0
    a32 = 0
    a33 = scale
    a41 = scale * (ix - AX) / 2
    a42 = scale * (iy - AY) / 2
    a43 = scale * (iz - AZ) / 2

    file = open(args.output, "w")
    file.write("#Insight Transform File V1.0\n")
    file.write("#Transform 0\n")
    file.write("Transform: AffineTransform_double_3_3\n")
    file.write("Parameters: %0.2f %0.2f %0.2f %0.2f %0.2f %0.2f %0.2f %0.2f %0.2f %0.2f %0.2f %0.2f\n"
               % (a11, a12, a13, a21, a22, a23, a31, a32, a33, a41, a42, a43))
    file.write("FixedParameters: %0.2f %0.2f %0.2f\n" % (AX/2, AY/2, AZ/2))
    file.close()


if __name__ == "__main__":
    main()
