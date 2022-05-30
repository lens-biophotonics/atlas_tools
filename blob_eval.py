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
    parser.add_argument('-t', type=float, default=320.0, help="absolute threshold")
    args = parser.parse_args()

    logger.info('initializing...')
    lista = os.listdir(args.input)
    lista = [x for x in lista if 'tif' in x and 'marker' not in x]
    tp = []
    fp = []
    fn = []
    prec = []
    rec = []
    f1 = []
    for element in lista:
        logger.info('processing file %s', element)
        handle = InputFile(element)
        image = handle.whole()
        detected = blob_detector(image, args.s1xy, args.s1z, args.s2xy, args.s2z, args.t)
        true = np.genfromtxt(os.path.join(args.i, element + '.marker'), delimiter=',', skip_header=1)
        local_tp, local_fp, local_fn = compare_points(detected, true, args.d)
        tp.append(local_tp)
        fp.append(local_fp)
        fn.append(local_fn)
        prec.append(local_tp / (local_tp + local_fp))
        rec.append(local_tp / (local_tp + local_fn))
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
    pd_file = os.path.join(args.output, 'eval.csv')
    logger.info('writing results...')
    df.to_csv(pd_file, index=False)
    sum_file = os.path.join(args.o, 'summary,csv')
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
