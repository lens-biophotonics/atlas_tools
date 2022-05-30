#!/usr/bin/env python3


def dog_filter(image, s1xy=18.0, s1z=10.0, s2xy=26.0, s2z=14.0):
    from scipy.signal import fftconvolve
    import logging
    import coloredlogs
    import numpy as np

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    logger.info('preparing DoG kernel...')
    sizexy = int(s2xy) * 2 - 1
    sizez = int(s2z) * 2 - 1
    dog_kernel = np.zeros((sizez, sizexy, sizexy))
    metaxy = (sizexy - 1) / 2
    metaz = (sizez - 1) / 2
    for x in np.arange(sizexy):
        for y in np.arange(sizexy):
            for z in np.arange(sizez):
                dog_kernel[z, y, x] = np.exp(
                    - ((x - metaxy) ** 2 + (y - metaxy) ** 2) / s1xy ** 2 - ((z - metaz) / s1z) ** 2) / \
                                      (s1xy * s1xy * s1z) - np.exp(
                    - ((x - metaxy) ** 2 + (y - metaxy) ** 2) / s2xy ** 2 -
                    ((z - metaz) / s2z) ** 2) / (s2xy * s2xy * s2z)

    logger.info('filtering image...')
    conv = fftconvolve(image, dog_kernel, mode='same')

    return conv


def blob_detector(image, s1xy=18.0, s1z=10.0, s2xy=26.0, s2z=14.0, threshold=300):
    import logging
    import coloredlogs
    from skimage.feature import peak_local_max

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    logger.info('processing image...')
    conv = dog_filter(image, s1xy, s1z, s2xy, s2z)
    peak = peak_local_max(conv, threshold_abs=threshold)

    return peak


def draw_balls(shape, peak, radius):
    import logging
    import coloredlogs
    import numpy as np

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    logger.info('creating ball...')
    axis = np.arange(-radius, radius + 1)
    x, y, z = np.meshgrid(axis, axis, axis)
    ball = np.heaviside((radius ** 2 - x ** 2 - y ** 2 - z ** 2), 1)

    logger.info('drawing balls on image...')
    image = np.zeros(shape)
    for line in peak[:]:
        mx = line[0] - radius
        my = line[1] - radius
        mz = line[2] - radius
        Mx = line[0] + radius + 1
        My = line[1] + radius + 1
        Mz = line[2] + radius + 1
        if (mx > 0) and (my > 0) and (mz > 0) and (Mx < shape[0]) and (My < shape[1]) and (Mz < shape[2]):
            image[mx:Mx, my:My, mz:Mz] += ball

    return image


def compare_points(p1, p2, threshold):
    #p1 is the computed point cloud, p2 the ground truth
    import logging
    import coloredlogs
    import numpy as np
    from scipy.spatial import KDTree

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    if len(p2.shape) == 1:
        p2 = np.tile(p2, (2,1))

    t2 = KDTree(p2)
    tp = []
    fn = []
    fp = []

    for point in p1[:]:
        match = t2.query(point, k=1)
        if match[0] < threshold:
            tp.append(point)
            p2 = np.delete(p2, match[1], 0)
            t2 = KDTree(p2)
        else:
            fp.append(point)

    for point in p2[:]:
        fn.append(point)

    return tp, fp, fn


