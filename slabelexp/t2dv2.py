from datetime import datetime
import os
import argparse

import numpy as np
from slabelexp import common
from slabelexp.common import compute_scores_per_key,generate_summary, scores_for_spreadsheet
from slabelexp.common import get_num_rows, compute_counts, compute_counts_per_err_meth, print_md_scores
import pandas as pd
from tadaqq.slabel import SLabel
from tadaqq.util import uri_to_fname, compute_scores
from util.t2dv2 import get_dirs, fetch_t2dv2_data


SPARQL_ENDPOINT = "https://en-dbpedia.oeg.fi.upm.es/sparql"
# The minimum number of objects for a numeric property
MIN_NUM_OBJ = 30
SHOW_LOGS = False


err_meth_fname_dict = {
    "mean_err": "t2dv2-mean-err",
    "mean_sq_err": "t2dv2-mean-sq-err",
    # "mean_sq1_err": "t2dv2-mean-sq1-err",
    "mean_sqroot_err": "t2dv2-mean-sqroot-err"
}


def get_folder_name_from_params(err_meth, use_estimate, remove_outliers):
    if err_meth not in err_meth_fname_dict:
        raise Exception("unknown err method")
    folder_name = err_meth_fname_dict[err_meth]

    if use_estimate:
        folder_name += "-estimate"
        est_txt = "estimate"
    else:
        folder_name += "-exact"
        est_txt = "exact"
    if not remove_outliers:
        folder_name += "-raw"
        remove_outliers_txt = "raw"
    else:
        remove_outliers_txt = "remove-outliers"
    return folder_name, est_txt, remove_outliers_txt


def annotate_t2dv2_single_column(row, sl, files_k, eval_per_prop, eval_per_sub_kind, err_meth, use_estimate,
                                 remove_outliers, folder_name, eval_data, data_dir, diffs=None):
    """
    Annotate a single column
    :param row:
    :param sl:
    :param files_k:
    :param eval_per_prop:
    :param eval_per_sub_kind:
    :param err_meth:
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
    # print("TEST class URI: %s" % class_uri)
    preds = sl.annotate_file(fdir=fdir, class_uri=class_uri, remove_outliers=remove_outliers, cols=[col_id],
                             err_meth=err_meth, estimate=use_estimate)

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
    diff_folder_path = os.path.join("slabelexp", "diffs", folder_name)
    if not os.path.exists(diff_folder_path):
        os.mkdir(diff_folder_path)
    for c in preds:
        diff_path = os.path.join(diff_folder_path, diff_name)
        if not diffs:
            diff_path = None
        res = sl.eval_column(preds[c], correct_uris=trans_uris, class_uri=class_uri, col_id=col_id,
                             fdir=fdir, diff_diagram=diff_path)
        files_k[fdir.split(os.sep)[-1] + "-" + str(c)] = (res, nrows)
        eval_data.append(res)
        eval_per_prop[pconcept].append(res)
        eval_per_sub_kind[sub_kind].append(res)


def annotate_t2dv2_single_param_set(endpoint, df, err_meth_scores, err_meth, use_estimate, remove_outliers,
                                    data_dir, diffs=None, draw=False, return_files_k=False):
    sl = SLabel(endpoint=endpoint, min_num_objs=MIN_NUM_OBJ)
    eval_data = []
    scores = []
    folder_name, est_txt, remove_outliers_txt = get_folder_name_from_params(err_meth, use_estimate, remove_outliers)
    files_k = dict()
    eval_per_prop = dict()
    eval_per_sub_kind = dict()
    for idx, row in df.iterrows():
        annotate_t2dv2_single_column(row, sl, files_k, eval_per_prop, eval_per_sub_kind, err_meth, use_estimate,
                                     remove_outliers, folder_name, eval_data, data_dir=data_dir, diffs=diffs)
    # print("\n\n\nfiles_k: ")
    # print(files_k)
    # print("\n\n\n")
    # print(eval_data)
    prec, rec, f1 = compute_scores(eval_data, k=1)
    score = {
        'ro': remove_outliers,
        'est': use_estimate,
        'err_meth': err_meth,
        'prec': prec,
        'rec': rec,
        'f1': f1
    }
    scores.append(score)
    folder_new_name = os.path.join('results', 'slabelling', folder_name)
    # print("\n\n================\n %s + %s + %s\n================\n" % (est_txt, err_meth, remove_outliers_txt))
    if draw:
        compute_scores_per_key(eval_per_prop, folder_new_name)
        if SHOW_LOGS:
            print("\n\n================\n %s + %s + %s" % (est_txt, err_meth, remove_outliers_txt))
        sub_folder_name = "sub_kind-%s" % (folder_name)
        compute_scores_per_key(eval_per_sub_kind, os.path.join('results', 'slabelling', sub_folder_name),
                               print_scores=True)
        folder_new_datapoint_name = os.path.join('results', 'slabelling', "datapoints-%s" % (folder_name))
        scores_df = compute_counts(files_k, folder_new_datapoint_name)

        if est_txt not in err_meth_scores:
            err_meth_scores[est_txt] = dict()

        err_meth_scores[est_txt][err_meth] = scores_df
    if return_files_k:
        return scores, files_k
    return scores


def check_mislabel_files(scores_per_file):
    """
    :param scores_per_file:
    :return:
    """
    # print(scores_per_file)
    # print("==========\n\n")
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


def annotate_t2dv2(endpoint, remove_outliers, err_meths, data_dir, estimate=[True], diffs=False,
                   draw=False, summary=False, check_mislabel=False, append_to_readme=False):
    """
    endpoint:
    remove_outliers: bool
    filename,concept,k,column,property,columnid,kind,sub_kind
    """

    def get_settings_key(ro, est, err_meth):
        s = ""
        if ro:
            s += "ro"
        else:
            s += "ra"
        if est:
            s += "-est-"
        else:
            s += "-ext-"
        s += err_meth
        return s

    err_meth_scores = dict()
    scores = []
    df = fetch_t2dv2_data()
    # df = df.iloc[:10] # only the first 10
    # print(df)
    files_scores_per_settings = dict()
    for ro in remove_outliers:
        for use_estimate in estimate:
            for err_meth in err_meths:
                scores_single, files_scores = annotate_t2dv2_single_param_set(endpoint, df, err_meth_scores, err_meth, use_estimate,
                                                                ro, data_dir, diffs=diffs, draw=draw, return_files_k=True)
                scores += scores_single
                if check_mislabel:
                    files_scores_per_settings[get_settings_key(ro, use_estimate, err_meth)] = files_scores

    print("err meth scores:")
    print(err_meth_scores)

    if check_mislabel:
        print("Going to check mislabel")
        check_mislabel_files(files_scores_per_settings)
    else:
        print("No mislabel")


    fname = "t2dv2-err-methods"
    if not remove_outliers:
        fname += "-raw"

    res_path = os.path.join('results', 'slabelling')

    new_fname = os.path.join(res_path, fname)
    if draw:
        compute_counts_per_err_meth(err_meth_scores, new_fname)
    if summary:
        generate_summary(scores, os.path.join(res_path, 'summary.svg'))

    if append_to_readme:
        res = print_md_scores(scores, do_print=False)
        readme_path = os.path.join(res_path, "README.md")
        with open(readme_path, "a") as f:
            f.write(res)
        res = scores_for_spreadsheet(scores, sep=",")
        csv_path = os.path.join(res_path, "results.csv")
        with open(csv_path, "a") as f:
            f.write(res)
    # print(final_scores_txt)


def parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='Parameters for the experiment')
    parser.add_argument('-e', '--err-meths', default=["mean_err"], nargs="+",
                        help="Functions to computer errors.")
    parser.add_argument('-o', '--outlier-removal', default=["true"], nargs="+",
                        help="Whether to remove outliers or not.")
    parser.add_argument('-d', '--diff', action='store_true', help="Store the diffs")
    parser.add_argument('-s', '--estimate', default=["True"], nargs="+")
    parser.add_argument('-w', '--draw', action='store_true', help="Whether to generate diagrams")
    parser.add_argument('-u', '--summary', action="store_true", help="Whether to generate a summary diagram")
    parser.add_argument('-m', '--mislabel', action="store_true", help="Whether to print mislabeled files")
    parser.add_argument('-a', '--append-to-readme', action="store_true")
    args = parser.parse_args()
    out_rems = [ro.lower() == "true" for ro in args.outlier_removal]
    parser.print_help()
    # raise Exception("")
    estimates = [e.lower() == "true" for e in args.estimate]
    return args.err_meths, out_rems, estimates, args.diff, args.draw, args.summary, args.mislabel, args.append_to_readme


if __name__ == '__main__':

    # if 't2dv2_dir' not in os.environ:
    #     print("ERROR: t2dv2_dir no in os.environ")

    # data_dir = os.path.join(os.environ['t2dv2_dir'], 'csv')
    # meta_dir = os.path.join(os.environ['t2dv2_dir'], 'T2Dv2_typology.csv')
    # properties_dir = os.path.join(os.environ['t2dv2_dir'], 'T2Dv2_properties.csv')
    data_dir, meta_dir, properties_dir = get_dirs()

    common.PRINT_DIFF = SHOW_LOGS
    a = datetime.now()
    err_meths, outlier_removal, estimate, diffs, to_draw, summary, mislab, append_to_readme = parse_arguments()
    # if mislab:
    #     print("mislabel is true")
    # else:
    #     print("mislabel is false")
    # ["mean_err", "mean_sq_err", "mean_sq1_err"]
    annotate_t2dv2(endpoint=SPARQL_ENDPOINT, remove_outliers=outlier_removal, err_meths=err_meths,
                   estimate=estimate, diffs=diffs, data_dir=data_dir, draw=to_draw, summary=summary,
                   check_mislabel=mislab, append_to_readme=append_to_readme)
    b = datetime.now()
    # print("\n\nTime it took (in seconds): %f.1 seconds\n\n" % (b - a).total_seconds())
    print("\n\nTime it took: %.1f minutes\n\n" % ((b - a).total_seconds() / 60.0))
