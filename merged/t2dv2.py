import os
import argparse
from datetime import datetime
import pandas as pd
from tadaqq.clus import Clusterer
from clus.t2dv2 import get_class_property_groups, get_col, cluster_t2dv2_df
from slabelexp.t2dv2 import get_folder_name_from_params
from tadaqq.slabmer import SLabMer
from tadaqq.util import create_dir
from merged.common import print_md_scores, draw_per_meth
from util.t2dv2 import fetch_t2dv2_data

SPARQL_ENDPOINT = "https://en-dbpedia.oeg.fi.upm.es/sparql"


def annotate_t2dv2_single_param_set(endpoint, df, data_dir, remove_outliers, err_meth, estimate, err_cutoff, same_class,
                                    candidate_failback, fetch_method, pref, print_pred=False):
    clusterer = Clusterer(save_memory=False)
    cluster_t2dv2_df(df, data_dir, clusterer, fetch_method, err_meth, err_cutoff, same_class)
    slabmer = SLabMer(endpoint)
    slabmer.annotate_clusters(clusterer.groups, remove_outliers, estimate, err_meth, pref=pref,
                              candidate_failback=candidate_failback, k=3)

    if print_pred:
        print(len(clusterer.groups))
        for g in clusterer.groups:
            print("=====")
            for ele in g:
                # print(ele)
                print("%s -- %s --\t %s" % (ele['property'], ele['candidate'], ele['fname']))

    score = slabmer.evaluate_labelling(clusterer.groups)
    return score


def update_scores_params_dict(d, score, cutoff, err_meth):
    if err_meth not in d:
        d[err_meth] = dict()

    if cutoff not in d[err_meth]:
        d[err_meth][cutoff] = score


def get_fname(remove_outliers, estimate, same_class, candidate_failback):

    if estimate:
        est_txt = 'estimate'
    else:
        est_txt = 'exact'

    if remove_outliers:
        ro_txt = "reo"
    else:
        ro_txt = 'raw'

    if same_class:
        sc_txt = 'sc'
    else:
        sc_txt = 'ca'  # class agnostic

    if candidate_failback:
        cf_txt = 'cf'
    else:
        cf_txt = 'nc'  # no candidate feedback

    fname = 't2dv2_mer_%s_%s_%s_%s' % (est_txt, ro_txt, sc_txt, cf_txt)
    return fname
    # fpath = os.path.join('results', 'merged', fname)
    # return fpath


def annotate_t2dv2(endpoint, data_dir, remove_outliers, err_meths, estimates, err_cutoffs, same_class, fetch_method,
                   candidate_failback, pref):
    """
    Annotate T2Dv2
    :param endpoint:
    :param data_dir:
    :param remove_outliers:
    :param err_meths:
    :param estimates:
    :param err_cutoffs:
    :param same_class:
    :param fetch_method:
    :param candidate_failback:
    :param pref: slab or clus
    :return:
    """
    if pref == SLabMer.SLAB_PREF:
        res_path = os.path.join('results', 'merged-slab')
    elif pref == SLabMer.CLUS_PREF:
        res_path = os.path.join('results', 'merged-clus')
    else:
        print(pref)
        raise Exception("Invalid pref value")

    create_dir(res_path)
    scores = []

    for estimate in estimates:
        scores_per_param = dict()
        for err_meth in err_meths:
            folder_name = get_folder_name_from_params(err_meth, estimate, remove_outliers, loose=False)
            for err_cutoff in err_cutoffs:
                score = annotate_t2dv2_single_param_set(endpoint=endpoint, data_dir=data_dir, df=fetch_t2dv2_data(),
                                                        remove_outliers=remove_outliers, fetch_method=fetch_method,
                                                        err_meth=err_meth, estimate=estimate, same_class=same_class,
                                                        pref=pref, err_cutoff=err_cutoff,
                                                        candidate_failback=candidate_failback)
                score['ro'] = remove_outliers
                score['est'] = estimate
                score['err_meth'] = err_meth
                score['same_class'] = same_class
                score['cutoff'] = err_cutoff
                scores.append(score)
                update_scores_params_dict(scores_per_param, score, err_meth=err_meth, cutoff=err_cutoff)
        fname = get_fname(remove_outliers=remove_outliers, estimate=estimate, same_class=same_class,
                          candidate_failback=candidate_failback)
        fpath = os.path.join(res_path, fname)
        draw_per_meth(scores_per_param, fpath)
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
    parser.add_argument('-p', '--pref', default=["slab"], choices=["slab", "clus"],
                        help="Whether the preference is for the slab predicted or the clus (most voted in the cluster)")

    args = parser.parse_args()
    estimates = [e.lower() == "true" for e in args.estimate]
    if args.pref=="slab":
        pref = SLabMer.SLAB_PREF
    elif args.pref=="clus":
        pref = SLabMer.CLUS_PREF

    return args.err_meths, args.outlier_removal == "true", estimates, [float(co) for co in args.cutoffs], \
           args.sameclass, args.failback, pref


if __name__ == '__main__':
    if 't2dv2_dir' not in os.environ:
        print("ERROR: t2dv2_dir no in os.environ")

    data_dir = os.path.join(os.environ['t2dv2_dir'], 'csv')
    meta_dir = os.path.join(os.environ['t2dv2_dir'], 'T2Dv2_typology.csv')
    properties_dir = os.path.join(os.environ['t2dv2_dir'], 'T2Dv2_properties.csv')

    a = datetime.now()
    err_meths, outlier_removal, estimates, cutoffs, sameclass, candidate_failback, pref = parse_arguments()

    # ["mean_err", "mean_sq_err", "mean_sq1_err"]
    annotate_t2dv2(endpoint=SPARQL_ENDPOINT, data_dir=data_dir, remove_outliers=outlier_removal, err_meths=err_meths,
                   fetch_method="max", estimates=estimates, err_cutoffs=cutoffs, same_class=sameclass,
                   candidate_failback=candidate_failback, pref=pref)
    b = datetime.now()
    # print("\n\nTime it took (in seconds): %f.1 seconds\n\n" % (b - a).total_seconds())
    print("\n\nTime it took: %.1f minutes\n\n" % ((b - a).total_seconds() / 60.0))

