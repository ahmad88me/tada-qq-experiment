import os
import argparse
from datetime import datetime
import pandas as pd
from tadaqq.clus import Clusterer
from clus.t2dv2 import get_class_property_groups, get_col, cluster_t2dv2_df
from slabelexp.t2dv2 import fetch_t2dv2_data, get_folder_name_from_params
from tadaqq.slabmer import SLabMer
from tadaqq.util import create_dir
from merged.common import print_md_scores

SPARQL_ENDPOINT = "https://en-dbpedia.oeg.fi.upm.es/sparql"


def annotate_t2dv2_single_param_set(endpoint, remove_outliers, err_meth, estimate, err_cutoff, same_class,
                                    candidate_failback, fetch_method):
    err_meth_scores = dict()
    scores = []
    df = fetch_t2dv2_data()
    clusterer = Clusterer(save_memory=False)
    cluster_t2dv2_df(df, clusterer, fetch_method, err_meth, err_cutoff, same_class)
    cp_groups, counts = get_class_property_groups(df)
    slabmer = SLabMer(endpoint)
    slabmer.annotate_clusters(clusterer.groups, remove_outliers, estimate, err_meth,
                              candidate_failback=candidate_failback, k=3)
    score = slabmer.evaluate_labelling(clusterer.groups)
    return score


def annotate_t2dv2(endpoint, remove_outliers, err_meths, estimates, err_cutoffs, same_class, fetch_method,
                   candidate_failback):
    res_path = os.path.join('results', 'merged')
    create_dir(res_path)
    # scores = dict()
    scores = []
    for err_meth in err_meths:
        # scores[err_meth] = dict()
        for estimate in estimates:
            # scores[err_meth][estimate] = []
            folder_name = get_folder_name_from_params(err_meth, estimate, remove_outliers, loose=False)
            for err_cutoff in err_cutoffs:
                score = annotate_t2dv2_single_param_set(endpoint=endpoint, remove_outliers=remove_outliers,
                                                        fetch_method=fetch_method, err_meth=err_meth, estimate=estimate,
                                                        same_class=same_class, err_cutoff=err_cutoff,
                                                        candidate_failback=candidate_failback)
                score['ro'] = remove_outliers
                score['est'] = estimate
                score['err_meth'] = err_meth
                score['same_class'] = same_class
                score['cutoff'] = err_cutoff
                scores.append(score)
    print_md_scores(scores)


def parse_arguments():
    """
        Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='Parameters for the experiment')
    parser.add_argument('-e', '--err-meths', default=["mean_err"], nargs="+",
                        help="Functions to computer errors.")
    parser.add_argument('-o', '--outlier-removal', default="true", choices=["true", "false"],
                        help="Whether to remove outliers or not.")
    parser.add_argument('-s', '--estimate', default=["True"], nargs="+")
    parser.add_argument('-c', '--cutoffs', default=[0.1], nargs="+",
                        help="Error cutoff value.")
    parser.add_argument('-m', '--sameclass', action="store_true")  # False by default
    parser.add_argument('-f', '--failback', action="store_true")  # False by default
    args = parser.parse_args()
    estimates = [e.lower() == "true" for e in args.estimate]
    return args.err_meths, args.outlier_removal == "true", estimates, [float(co) for co in args.cutoffs], \
           args.sameclass, args.failback


if __name__ == '__main__':
    if 't2dv2_dir' not in os.environ:
        print("ERROR: t2dv2_dir no in os.environ")

    data_dir = os.path.join(os.environ['t2dv2_dir'], 'csv')
    meta_dir = os.path.join(os.environ['t2dv2_dir'], 'T2Dv2_typology.csv')
    properties_dir = os.path.join(os.environ['t2dv2_dir'], 'T2Dv2_properties.csv')

    a = datetime.now()
    err_meths, outlier_removal, estimates, cutoffs, sameclass, candidate_failback = parse_arguments()

    # ["mean_err", "mean_sq_err", "mean_sq1_err"]
    annotate_t2dv2(endpoint=SPARQL_ENDPOINT, remove_outliers=outlier_removal, err_meths=err_meths, fetch_method="max",
                   estimates=estimates, err_cutoffs=cutoffs, same_class=sameclass, candidate_failback=candidate_failback)
    b = datetime.now()
    # print("\n\nTime it took (in seconds): %f.1 seconds\n\n" % (b - a).total_seconds())
    print("\n\nTime it took: %.1f minutes\n\n" % ((b - a).total_seconds() / 60.0))

