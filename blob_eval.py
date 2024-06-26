#!/usr/bin/env python3


def main():
    from zetastitcher import InputFile
    import logging
    import coloredlogs
    import pandas as pd
    import argparse
    import numpy as np
    import os
    from blob_utils import blob_detector, compare_points

    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(funcName)s] - %(asctime)s - %(message)s', level=logging.INFO)
    coloredlogs.install(level='DEBUG', logger=logger)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='input folder', metavar='PATH')
    parser.add_argument('-o', '--output', help='output base path', metavar='PATH')
    parser.add_argument('-s1xy', type=float, default=13.0, help="smaller xy sigma")
    parser.add_argument('-s1z', type=float, default=7.0, help="smaller z sigma")
    parser.add_argument('-s2xy', type=float, default=26.0, help="larger xy sigma")
    parser.add_argument('-s2z', type=float, default=14.0, help="larger z sigma")
    parser.add_argument('-t', type=float, default=310.0, help="absolute threshold")
    parser.add_argument('-d', type=float, default=5.0, help="threshold distance")
    args = parser.parse_args()

    logger.info('initializing...')
    lista = os.listdir(args.input)
    lista = [x for x in lista if 'tif' in x and 'csv' not in x]
    tp = []
    fp = []
    fn = []
    prec = []
    rec = []
    f1 = []
    for element in lista:
        logger.info('processing file %s', element)
        handle = InputFile(os.path.join(args.input,element))
        image = handle.whole()
        detected = blob_detector(image, args.s1xy, args.s1z, args.s2xy, args.s2z, args.t)
        name, ext = os.path.splitext(element)
        true = np.genfromtxt(os.path.join(args.input, name + '.csv'), delimiter=',', skip_header=1)
        if len(true) == 0:
            local_tp = 0
            local_fp = len(detected)
            local_fn = 0
        else:
            if len(true.shape) > 1:
                true = true[:, 5:8]
                true[:, [0, 2]] = true[:, [2, 0]]
            else:
                true = true[5:8]
                true = np.flip(true)
            ltp, lfp, lfn = compare_points(detected, true, args.d)
            local_tp = len(ltp)
            local_fp = len(lfp)
            local_fn = len(lfn)
        tp.append(local_tp)
        fp.append(local_fp)
        fn.append(local_fn)
        try:
            prec.append(local_tp / (local_tp + local_fp))
        except:
            prec.append(0)
        try:
            rec.append(local_tp / (local_tp + local_fn))
        except:
            rec.append(0)
        f1.append(2 * local_tp / (2 * local_tp + local_fp + local_fn))

    total_tp = np.sum(tp)
    total_fp = np.sum(fp)
    total_fn = np.sum(fn)
    macro_prec = total_tp / (total_tp + total_fp)
    macro_rec = total_tp / (total_tp + total_fn)
    macro_f1 = 2 * macro_rec * macro_prec / (macro_prec + macro_rec)

    df = pd.DataFrame(zip(lista, tp, fp, fn, prec, rec, f1), columns=['filename', 'true positives', 'false positives',
                                                                      'false negatives', 'precision', 'recall',
                                                                      'f1-score'])
    if not os.path.exists(args.output):
        os.makedirs(args.output, 0o775)
    pd_file = os.path.join(args.output, 'eval.csv')
    logger.info('writing results...')
    df.to_csv(pd_file, index=False)
    sum_file = os.path.join(args.output, 'summary.csv')
    file = open(sum_file, "w")
    file.write("Number of subvolumes: %d\n" % (len(lista)))
    file.write("Total true positives: %d\n" % total_tp)
    file.write("Total false positives: %d\n" % total_fp)
    file.write("Total false negatives: %d\n" % total_fn)
    file.write("Macro-averaged precision: %02f\n" % macro_prec)
    file.write("Macro-averaged recall: %02f\n" % macro_rec)
    file.write("Micro-averaged f1-score: %02f\n" % macro_f1)
    file.write("Micro-averaged precision: %02f\n" % np.mean(prec))
    file.write("Micro-averaged recall: %02f\n" % np.mean(rec))
    file.write("Micro-averaged f1-score: %02f\n" % np.mean(f1))
    file.close()


if __name__ == "__main__":
    main()
