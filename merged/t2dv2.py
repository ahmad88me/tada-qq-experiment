import os
import argparse
from datetime import datetime
import pandas as pd
from clus.common import Clusterer
from clus.t2dv2 import get_class_property_groups, get_col, cluster_t2dv2_df
from slabelexp.t2dv2 import fetch_t2dv2_data
from merged.slabmer import SLabMer

SPARQL_ENDPOINT = "https://en-dbpedia.oeg.fi.upm.es/sparql"


def annotate_t2dv2_single_param_set(endpoint, remove_outliers, err_meth, estimate, err_cutoff, same_class, fetch_method):
    err_meth_scores = dict()
    scores = []
    df = fetch_t2dv2_data()
    clusterer = Clusterer(save_memory=False)
    cluster_t2dv2_df(df, clusterer, fetch_method, err_meth, err_cutoff, same_class)
    cp_groups, counts = get_class_property_groups(df)
    slabmer = SLabMer(endpoint)
    slabmer.annotate_clusters(clusterer.groups, remove_outliers, estimate, err_meth, k=3)
    slabmer.evaluate_labelling(cp_groups, clusterer.groups)


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
    args = parser.parse_args()
    estimates = [e.lower() == "true" for e in args.estimate]
    return args.err_meths, args.outlier_removal == "true", args.loose, estimates, args.cutoffs, args.sameclass


if __name__ == '__main__':
    if 't2dv2_dir' not in os.environ:
        print("ERROR: t2dv2_dir no in os.environ")

    data_dir = os.path.join(os.environ['t2dv2_dir'], 'csv')
    meta_dir = os.path.join(os.environ['t2dv2_dir'], 'T2Dv2_typology.csv')
    properties_dir = os.path.join(os.environ['t2dv2_dir'], 'T2Dv2_properties.csv')

    a = datetime.now()
    err_meths, outlier_removal, estimate, cutoffs, sameclass = parse_arguments()

    # ["mean_err", "mean_sq_err", "mean_sq1_err"]
    annotate_t2dv2(endpoint=SPARQL_ENDPOINT, remove_outliers=outlier_removal, err_meths=err_meths, fetch_method="max",
                   estimate=estimate, cutoffs=cutoffs, same_class=sameclass)
    b = datetime.now()
    # print("\n\nTime it took (in seconds): %f.1 seconds\n\n" % (b - a).total_seconds())
    print("\n\nTime it took: %.1f minutes\n\n" % ((b - a).total_seconds() / 60.0))

