#!/usr/bin/python3


def conv8bit(in_path, out_path=None):
    import numpy as np
    import nibabel as nib
    import os.path
    import logging

    logger = logging.getLogger(__name__)
    nifti = nib.load(in_path)
    data = nifti.get_fdata()
    logger.info('input image loaded')

    nifti8 = nib.Nifti1Image(data.astype('uint8'), None)
    logger.info('image converted')
    nifti8.header['pixdim'] = nifti.header['pixdim']
    nifti8.header['xyzt_units'] = nifti.header['xyzt_units']

    # 2 is the NIFTI code for unsigned char, see https://nifti.nimh.nih.gov/nifti-1/documentation/nifti1fields/
    nifti8.header['datatype'] = 2
    nifti8.header['bitpix'] = 8

    if out_path is None:
        base, filename = os.path.split(in_path)
        name, ext = os.path.splitext(filename)
        name2, ext2 = os.path.splitext(name)
        if ext2 == '':
            out_path = os.path.join(base, name + "_8bit" + ext)
        else:
            out_path = os.path.join(base, name2 + "_8bit" + ext2 + ext)
    nib.save(nifti8, out_path)
    logger.info('output image saved to %s', out_path)
    return out_path


def conv16bit(in_path, out_path=None):
    import numpy as np
    import nibabel as nib
    import os.path
    import logging

    logger = logging.getLogger(__name__)
    nifti = nib.load(in_path)
    data = nifti.get_fdata()
    logger.info('input image loaded')

    nifti16 = nib.Nifti1Image(data.astype('uint16'), None)
    logger.info('image converted')
    nifti16.header['pixdim'] = nifti.header['pixdim']
    nifti16.header['xyzt_units'] = nifti.header['xyzt_units']

    # 512 is the NIFTI code for unsigned char, see https://nifti.nimh.nih.gov/nifti-1/documentation/nifti1fields/
    nifti16.header['datatype'] = 512
    nifti16.header['bitpix'] = 16

    if out_path is None:
        base, filename = os.path.split(in_path)
        name, ext = os.path.splitext(filename)
        name2, ext2 = os.path.splitext(name)
        if ext2 == '':
            out_path = os.path.join(base, name + "_16bit" + ext)
        else:
            out_path = os.path.join(base, name2 + "_16bit" + ext2 + ext)
    nib.save(nifti16, out_path)
    logger.info('output image saved to %s', out_path)
    return out_path


def convertImage(in_path, out_path, reverse=False, expand=False, bs=100, x_final=0.025, y_final=0.025, z_final=0.025,
                 x_pix=0.0104, y_pix=0.0104, z_pix=0.01, nl=110, gamma=0.3, mp=99.9, top=-1):
    import numpy as np
    import nibabel as nib
    import os
    import logging
    import skimage.external.tifffile as tiff
    from skimage.transform import rescale

    logger = logging.getLogger(__name__)
    in_image = tiff.imread(in_path)
    logger.info('input image loaded')

    temp = rescale(np.swapaxes(in_image, 0, 2), scale=((x_pix / x_final), (y_pix / y_final), (z_pix / z_final)),
                   multichannel=False, anti_aliasing=False, preserve_range=True)
    logger.info('image downscaled')

    temp = temp - nl
    temp = temp.clip(min=0)
    temp = np.power(temp, gamma)
    if top == -1:
        top = np.percentile(temp, mp)
    temp = (temp / top) * 255
    temp = temp.clip(max=255)
    if reverse:
        temp = np.flip(temp, 0)
        temp = np.flip(temp, 2)
    if expand:
        temp = np.concatenate((temp, np.zeros((temp.shape[0], temp.shape[1], bs))), axis=2)

    out_image = temp.astype('uint8')
    logger.info('image processed')

    nifti = nib.Nifti1Image(out_image, None)
    nifti.header['pixdim'][1] = x_final
    nifti.header['pixdim'][2] = y_final
    nifti.header['pixdim'][3] = z_final
    # 2 is the NIFTI code for unsigned char, see https://nifti.nimh.nih.gov/nifti-1/documentation/nifti1fields/
    nifti.header['datatype'] = 2
    nifti.header['bitpix'] = 8
    # 2 is the NIFTI code for millimeters, see https://nifti.nimh.nih.gov/nifti-1/documentation/nifti1fields/
    nifti.header['xyzt_units'] = 2

    folder, file = os.path.split(in_path)
    if out_path == 'NULL':
        filename, ext = os.path.splitext(file)
        out_path = os.path.join(folder, filename + ".nii.gz")

    nib.save(nifti, out_path)
    logger.info('output image saved to %s', out_path)
    return top


def convertImage16(in_path, out_path, reverse=False, expand=False, bs=100, x_final=0.025, y_final=0.025, z_final=0.025,
                   x_pix=0.0104, y_pix=0.0104, z_pix=0.01):
    import numpy as np
    import nibabel as nib
    import os
    import logging
    import skimage.external.tifffile as tiff
    from skimage.transform import rescale

    logger = logging.getLogger(__name__)
    in_image = tiff.imread(in_path)
    logger.info('input image loaded')

    temp = rescale(np.swapaxes(in_image, 0, 2), scale=((x_pix / x_final), (y_pix / y_final), (z_pix / z_final)),
                   multichannel=False, anti_aliasing=False, preserve_range=True)
    logger.info('image downscaled')

    if reverse:
        temp = np.flip(temp, 0)
        temp = np.flip(temp, 2)
    if expand:
        temp = np.concatenate((temp, np.zeros((temp.shape[0], temp.shape[1], bs))), axis=2)

    out_image = temp.astype('uint16')
    logger.info('image processed')

    nifti = nib.Nifti1Image(out_image, None)
    nifti.header['pixdim'][1] = x_final
    nifti.header['pixdim'][2] = y_final
    nifti.header['pixdim'][3] = z_final
    # 512 is the NIFTI code for unsigned short, see https://nifti.nimh.nih.gov/nifti-1/documentation/nifti1fields/
    nifti.header['datatype'] = 512
    nifti.header['bitpix'] = 16
    # 2 is the NIFTI code for millimeters, see https://nifti.nimh.nih.gov/nifti-1/documentation/nifti1fields/
    nifti.header['xyzt_units'] = 2

    folder, file = os.path.split(in_path)
    if out_path == 'NULL':
        filename, ext = os.path.splitext(file)
        out_path = os.path.join(folder, filename + "16bit.nii.gz")

    nib.save(nifti, out_path)
    logger.info('output image saved to %s', out_path)


def merge(f_path, b_path, out_path, ms, t):
    import nibabel as nib
    import numpy as np
    import logging

    logger = logging.getLogger(__name__)

    front = nib.load(f_path)
    f_data = front.get_fdata()
    logger.info('front image loaded')

    back = nib.load(b_path)
    b_data = back.get_fdata()
    logger.info('back image loaded')

    mid = int(float((front.header["dim"][3])) / 2) + ms
    half = (int(float(t) / 2))

    out = np.zeros(f_data.shape).astype('uint8')
    out[..., 0:(mid - half)] = f_data[..., 0:(mid - half)]
    out[..., (mid + half):out.shape[2]] = b_data[..., (mid + half):out.shape[2]]

    slab_front = np.zeros((out.shape[0], out.shape[1], 2 * half))
    slab_front[...] = f_data[..., (mid - half):(mid + half)]
    slab_back = np.zeros((out.shape[0], out.shape[1], 2 * half))
    slab_back[...] = b_data[..., (mid - half):(mid + half)]

    for i in range(2 * half):
        out[..., (mid - half) + i] = (slab_front[..., i] * (((2 * half - 1) - i) / (2 * half - 1))
                                      + slab_back[..., i] * (i / (2 * half - 1))).astype('uint8')

    logger.info('images merged')

    out_nifti = nib.Nifti1Image(out, None)
    out_nifti.header['pixdim'] = front.header['pixdim']
    out_nifti.header['xyzt_units'] = front.header['xyzt_units']
    out_nifti.header['datatype'] = front.header['datatype']
    out_nifti.header['bitpix'] = front.header['bitpix']

    nib.save(out_nifti, out_path)
    logger.info('output image saved to %s', out_path)


def merge16(f_path, b_path, out_path, ms, t):
    import nibabel as nib
    import numpy as np
    import logging

    logger = logging.getLogger(__name__)

    front = nib.load(f_path)
    f_data = front.get_fdata()
    logger.info('front image loaded')

    back = nib.load(b_path)
    b_data = back.get_fdata()
    logger.info('back image loaded')

    mid = int(float((front.header["dim"][3])) / 2) + ms
    half = (int(float(t) / 2))

    out = np.zeros(f_data.shape).astype('uint16')
    out[..., 0:(mid - half)] = f_data[..., 0:(mid - half)]
    out[..., (mid + half):out.shape[2]] = b_data[..., (mid + half):out.shape[2]]

    slab_front = np.zeros((out.shape[0], out.shape[1], 2 * half))
    slab_front[...] = f_data[..., (mid - half):(mid + half)]
    slab_back = np.zeros((out.shape[0], out.shape[1], 2 * half))
    slab_back[...] = b_data[..., (mid - half):(mid + half)]

    for i in range(2 * half):
        out[..., (mid - half) + i] = (slab_front[..., i] * (((2 * half - 1) - i) / (2 * half - 1))
                                      + slab_back[..., i] * (i / (2 * half - 1))).astype('uint16')

    logger.info('images merged')

    out_nifti = nib.Nifti1Image(out, None)
    out_nifti.header['pixdim'] = front.header['pixdim']
    out_nifti.header['xyzt_units'] = front.header['xyzt_units']
    out_nifti.header['datatype'] = front.header['datatype']
    out_nifti.header['bitpix'] = front.header['bitpix']

    nib.save(out_nifti, out_path)
    logger.info('output image saved to %s', out_path)


def tif2nii(in_path, out_path, x_pix=0.025, y_pix=0.025, z_pix=0.025):
    import numpy as np
    import nibabel as nib
    import os
    import logging
    import skimage.external.tifffile as tiff

    logger = logging.getLogger(__name__)
    image = tiff.imread(in_path)
    logger.info('input image loaded')
    out_image = np.swapaxes(image, 0, 2)
    nifti = nib.Nifti1Image(out_image, None)
    nifti.header['pixdim'][1] = x_pix
    nifti.header['pixdim'][2] = y_pix
    nifti.header['pixdim'][3] = z_pix
    # 2 is the NIFTI code for unsigned char, see https://nifti.nimh.nih.gov/nifti-1/documentation/nifti1fields/
    nifti.header['datatype'] = 2
    nifti.header['bitpix'] = 8
    # 2 is the NIFTI code for millimeters, see https://nifti.nimh.nih.gov/nifti-1/documentation/nifti1fields/
    nifti.header['xyzt_units'] = 2

    folder, file = os.path.split(in_path)
    if out_path == 'NULL':
        filename, ext = os.path.splitext(file)
        out_path = os.path.join(folder, filename + ".nii.gz")

    nib.save(nifti, out_path)
    logger.info('output image saved to %s', out_path)


def nii2tif(in_path, out_path):

    import nibabel as nib
    import os
    import logging
    import tifffile as tiff

    logger = logging.getLogger(__name__)
    nifti = nib.load(in_path)
    logger.info('input image loaded')
    image = nifti.get_fdata()
    image = np.swapaxes(image, 0, 1)
    image = np.swapaxes(image, 0, 2)

    folder, file = os.path.split(in_path)
    if out_path == 'NULL':
        filename, ext = os.path.splitext(file)
        out_path = os.path.join(folder, filename + ".tif")

    tiff.imwrite(out_path, image.astype('uint8'))
    logger.info('output image saved to %s', out_path)
