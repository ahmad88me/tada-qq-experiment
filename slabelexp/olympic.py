import os
import logging
from datetime import datetime
from slabelexp import common
from slabelexp.common import compute_scores, print_md_scores

from tadaqq.slabel.util import uri_to_fname
from tadaqq.slabel import SLabel

SHOW_LOGS = False

data_dir = "local_data"

# The minimum number of objects for a numeric property
MIN_NUM_OBJ = 30


def annotate_olympic_games(endpoint, remove_outliers, meta_dir, err_meth, estimate):
    """
    endpoint:
    remove_outliers:
    meta_dir:
    """
    olympic_games_dir = 'olympic_games'
    olympic_games_data_dir = os.path.join(data_dir, olympic_games_dir, 'data')
    f = open(meta_dir)
    eval_data = []
    sl = SLabel(endpoint=endpoint, min_num_objs=MIN_NUM_OBJ)
    for line in f.readlines():
        atts = line.split(',')
        if len(atts) > 1:
            fname = atts[0].strip()
            class_uri = atts[1].strip()
            col_id = int(atts[2])
            uris = atts[3].split(';')
            trans_uris = [uri_to_fname(uri) for uri in uris]
            fdir = os.path.join(olympic_games_data_dir, fname)
            if SHOW_LOGS:
                print("fdir: ")
                print(fdir)
            preds = sl.annotate_file(fdir=fdir, class_uri=class_uri, remove_outliers=remove_outliers,cols=[col_id],
                                     err_meth=err_meth, estimate=estimate, print_diff=SHOW_LOGS)
            for c in preds:
                res = sl.eval_column(preds[c], correct_uris=trans_uris, fdir=fdir, col_id=col_id, print_diff=SHOW_LOGS)
                eval_data.append(res)
                if not res:
                    if SHOW_LOGS:
                        print(preds)

    prec, rec, f1 = compute_scores(eval_data, k=1)
    if SHOW_LOGS:
        print("\nresults: ")
        print(eval_data)
        print("Precision: %.2f\nRecall: %.2f\nF1: %.2f" % (prec, rec, f1))
    return prec, rec, f1


if __name__ == '__main__':
    a = datetime.now()
    common.PRINT_DIFF = SHOW_LOGS
    scores = []
    for ro in [True, False]:
        for est in [True, False]:
            for err_meth in ["mean_err", "mean_sq_err", "mean_sqroot_err"]:
                prec, rec, f1 = annotate_olympic_games(endpoint='https://en-dbpedia.oeg.fi.upm.es/sparql',
                                                       remove_outliers=ro,
                                                       meta_dir="slabelexp/olympic_meta.csv", estimate=est,
                                                       err_meth=err_meth)
                score = {
                    'ro': ro,
                    'est': est,
                    'err_meth': err_meth,
                    'prec': prec,
                    'rec': rec,
                    'f1': f1
                }
                scores.append(score)

    b = datetime.now()
    print_md_scores(scores)
    print("\n\nTime it took: %f.1 seconds\n\n" % (b - a).total_seconds())

