from datetime import datetime
import os
import argparse

import numpy as np
from slabelexp import common
from slabelexp.common import compute_scores_per_key
from slabelexp.common import get_num_rows, compute_counts
from ks.common import print_md_scores, compute_counts_per_dist, generate_summary
import pandas as pd
from tadaqq.slabel import SLabel
from tadaqq.util import uri_to_fname, compute_scores
from util.t2dv2 import get_dirs, fetch_t2dv2_data

from ks.kslabel import DIST_DIFF, DIST_PVAL, KSLabel


SPARQL_ENDPOINT = "https://en-dbpedia.oeg.fi.upm.es/sparql"
# The minimum number of objects for a numeric property
MIN_NUM_OBJ = 30
SHOW_LOGS = True


# err_meth_fname_dict = {
#     "mean_err": "t2dv2-mean-err",
#     "mean_sq_err": "t2dv2-mean-sq-err",
#     # "mean_sq1_err": "t2dv2-mean-sq1-err",
#     "mean_sqroot_err": "t2dv2-mean-sqroot-err"
# }


def get_folder_name_from_params(dist, use_estimate, remove_outliers):
    """

    :param dist:
    :param use_estimate:
    :param remove_outliers:
    :return:
    """
    if dist not in [DIST_PVAL, DIST_DIFF]:
        raise Exception("unknown distance method: %s" % dist)
    folder_name = "t2dv2-"+dist

    if use_estimate:
        folder_name += "-estimate"
        est_txt = "estimate"
    else:
        folder_name += "-exact"
        est_txt = "exact"

    if remove_outliers:
        folder_name += "-reo"
        remove_outliers_txt = "reo"
    else:
        folder_name += "-raw"
        remove_outliers_txt = "raw"
    return folder_name, est_txt, remove_outliers_txt


def annotate_t2dv2_single_column(row, ksl, files_k, eval_per_prop, eval_per_sub_kind, dist, use_estimate,
                                 remove_outliers, folder_name, eval_data, data_dir, diffs=None):
    """
    Annotate a single column
    :param row:
    :param ksl:
    :param files_k:
    :param eval_per_prop:
    :param eval_per_sub_kind:
    :param dist:
    :param use_estimate:
    :param remove_outliers:
    :param folder_name:
    :param eval_data:
    :param data_dir:
    :param diffs:
    :return:
    """
    class_uri = 'http://dbpedia.org/ontology/' + row['concept']
    col_id = int(row['columnid'])
    uris = row['property'].split(';')
    trans_uris = [uri_to_fname(uri) for uri in uris]
    csv_fname = row['filename'] + ".csv"
    fdir = os.path.join(data_dir, csv_fname)
    preds = ksl.annotate_file(fdir=fdir, class_uri=class_uri, remove_outliers=remove_outliers, cols=[col_id],
                              dist=dist, estimate=use_estimate)

    pconcept = row['pconcept']
    sub_kind = row['sub_kind']
    if sub_kind in [None, np.nan, np.NaN]:
        sub_kind = row['kind']
    if pconcept in [None, np.nan, np.NaN]:
        print("is none")
        print(row)
    if pconcept not in eval_per_prop:
        eval_per_prop[pconcept] = []
    if sub_kind not in eval_per_sub_kind:
        eval_per_sub_kind[sub_kind] = []
    nrows = get_num_rows(fdir)
    diff_name = "%s-%s-%s" % (uri_to_fname(class_uri), uri_to_fname(uris[0]), fdir.split(os.sep)[-1])
    diff_folder_path = os.path.join("ks", "diffs", folder_name)
    if not os.path.exists(diff_folder_path) and diffs:
        os.mkdir(diff_folder_path)
    for c in preds:
        diff_path = os.path.join(diff_folder_path, diff_name)
        if not diffs:
            diff_path = None
        res = ksl.eval_column(preds[c], correct_uris=trans_uris, class_uri=class_uri, col_id=col_id,
                              fdir=fdir, diff_diagram=diff_path)
        files_k[fdir.split(os.sep)[-1] + "-" + str(c)] = (res, nrows)
        eval_data.append(res)
        eval_per_prop[pconcept].append(res)
        eval_per_sub_kind[sub_kind].append(res)


def annotate_t2dv2_single_param_set(endpoint, df, dist_scores, dist, use_estimate, remove_outliers,
                                    data_dir, diffs=None, draw=False, return_files_k=False):
    ksl = KSLabel(endpoint=endpoint, min_num_objs=MIN_NUM_OBJ)
    eval_data = []
    scores = []
    folder_name, est_txt, remove_outliers_txt = get_folder_name_from_params(dist, use_estimate, remove_outliers)
    files_k = dict()
    eval_per_prop = dict()
    eval_per_sub_kind = dict()
    for idx, row in df.iterrows():
        annotate_t2dv2_single_column(row, ksl, files_k, eval_per_prop, eval_per_sub_kind, dist, use_estimate,
                                     remove_outliers, folder_name, eval_data, data_dir=data_dir, diffs=diffs)

        ## TEST
        if idx > 10:
            print("NOW STOPING for testing")
            break

    if SHOW_LOGS:
        print("\n\n=========================\n\t\teval data\n=========================")
        print(eval_data)

    prec, rec, f1 = compute_scores(eval_data, k=1)
    score = {
        'ro': remove_outliers,
        'est': use_estimate,
        'dist': dist,
        'prec': prec,
        'rec': rec,
        'f1': f1
    }
    scores.append(score)
    folder_new_name = os.path.join('results', 'ks', folder_name)
    if draw:
        compute_scores_per_key(eval_per_prop, folder_new_name)
        if SHOW_LOGS:
            print("\n\n================\n %s + %s + %s" % (est_txt, dist, remove_outliers_txt))
        sub_folder_name = "sub_kind-%s" % (folder_name)
        compute_scores_per_key(eval_per_sub_kind, os.path.join('results', 'ks', sub_folder_name), print_scores=True)
        folder_new_datapoint_name = os.path.join('results', 'ks', "datapoints-%s" % (folder_name))
        scores_df = compute_counts(files_k, folder_new_datapoint_name)

        if est_txt not in dist_scores:
            dist_scores[est_txt] = dict()

        dist_scores[est_txt][dist] = scores_df
    if return_files_k:
        return scores, files_k
    return scores


def check_mislabel_files(scores_per_file):
    """
    :param scores_per_file:
    :return:
    """

    d = dict()
    for sett in scores_per_file:
        d[sett] = []
        for fname_col in scores_per_file[sett]:
            tr = (fname_col, scores_per_file[sett][fname_col])
            d[sett].append(tr)

    print(d)
    print("--------^^^^^^^^^^^^^^^-------------")

    for i, sett1 in enumerate(d):
        for j, sett2 in enumerate(d):
            if i >= j:
                continue
            diffs1 = list(set(d[sett1]) - set(d[sett2]))
            print(diffs1)
            if len(diffs1) == 0:
                print("skip")
                print(sett1)
                print(sett2)
                continue
            diffs2 = list(set(d[sett2]) - set(d[sett1]))
            diffs1.sort()
            diffs2.sort()
            print("\n\n\nOptions: %s\t%s\n==========\n" % (sett1, sett2))
            for d_idx in range(len(diffs1)):
                print(diffs1[d_idx])
                print(diffs2[d_idx])
                print("-----------\n")


def annotate_t2dv2(endpoint, remove_outliers, data_dir, dists, estimate=[True], diffs=False,
                   draw=False, summary=False, check_mislabel=False):
    """
    :param endpoint:
    :param remove_outliers:
    :param data_dir:
    :param dists:
    :param estimate:
    :param diffs:
    :param draw:
    :param summary:
    :param check_mislabel:
    :return:
    """


    def get_settings_key(ro, est, dist):
        s = ""
        if ro:
            s += "ro"
        else:
            s += "ra"
        if est:
            s += "-est-"
        else:
            s += "-ext-"
        s += dist
        return s

    dist_scores = dict()
    scores = []
    df = fetch_t2dv2_data()
    # df = df.iloc[:10] # only the first 10
    # print(df)
    files_scores_per_settings = dict()
    for ro in remove_outliers:
        for use_estimate in estimate:
            for dist in dists:
                scores_single, files_scores = annotate_t2dv2_single_param_set(endpoint, df, dist_scores, dist,
                                                                              use_estimate=use_estimate,
                                                                              remove_outliers=ro, data_dir=data_dir,
                                                                              diffs=diffs,
                                                                              draw=draw, return_files_k=True)
                scores += scores_single
                if check_mislabel:
                    files_scores_per_settings[get_settings_key(ro, use_estimate, dist)] = files_scores

    print("dist scores:")
    print(dist_scores)

    if check_mislabel:
        print("Going to check mislabel")
        check_mislabel_files(files_scores_per_settings)
    else:
        print("No mislabel")

    print_md_scores(scores)

    fname = "t2dv2-dist"
    if not remove_outliers:
        fname += "-raw"
    new_fname = os.path.join('results', 'ks', fname)
    if draw:
        compute_counts_per_dist(dist_scores, new_fname)
    if summary:
        generate_summary(scores, os.path.join('results', 'ks', 'summary.svg'))
    # print(final_scores_txt)


def parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='Parameters for the experiment')
    parser.add_argument('-o', '--outlier-removal', default=["true"], nargs="+",
                        help="Whether to remove outliers or not.")
    parser.add_argument('-d', '--diff', action='store_true', help="Store the diffs")
    parser.add_argument('-s', '--estimate', default=["true"], nargs="+", help="Whether to show estimates or not.")
    parser.add_argument('-w', '--draw', action='store_true', help="Whether to generate diagrams")
    parser.add_argument('-u', '--summary', action="store_true", help="Whether to generate a summary diagram")
    parser.add_argument('--dists', nargs="+", help="The distance measure to use (PVAL or DIFF)")
    parser.add_argument('-m', '--mislabel', action="store_true", help="Whether to print mislabeled files")
    parser.print_help()
    args = parser.parse_args()

    out_rems = [ro.lower() == "true" for ro in args.outlier_removal]
    estimates = [e.lower() == "true" for e in args.estimate]
    for d in args.dists:
        if d not in [DIST_PVAL, DIST_DIFF]:
            raise Exception("Unknown distance measure: %s" % d)
    return out_rems, estimates, args.diff, args.draw, args.summary, args.mislabel, args.dists


if __name__ == '__main__':
    data_dir, meta_dir, properties_dir = get_dirs()

    common.PRINT_DIFF = SHOW_LOGS
    a = datetime.now()
    outlier_removal, estimate, diffs, to_draw, summary, mislab, dists = parse_arguments()
    annotate_t2dv2(endpoint=SPARQL_ENDPOINT, remove_outliers=outlier_removal,
                   estimate=estimate, diffs=diffs, data_dir=data_dir, draw=to_draw, summary=summary,
                   check_mislabel=mislab, dists=dists)
    b = datetime.now()
    print("\n\nTime it took: %.1f minutes\n\n" % ((b - a).total_seconds() / 60.0))


