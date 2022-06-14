"""
This script is meant to be used for the analysis. The idea is to run it for specific parameters and see why
it behaves in certain ways.
"""

import os
import argparse
from datetime import datetime
import random
import pandas as pd
from tadaqq.clus import Clusterer
from clus.t2dv2 import get_class_property_groups, get_col, cluster_t2dv2_df
from slabelexp.t2dv2 import get_folder_name_from_params
from tadaqq.slabmer import SLabMer
from tadaqq.util import create_dir
from merged.common import print_md_scores, draw_per_meth
from util.t2dv2 import fetch_t2dv2_data, get_dirs
from merged.t2dv2 import annotate_t2dv2_single_param_set, SPARQL_ENDPOINT, update_scores_params_dict
import seaborn as sns
import matplotlib.pyplot as plt


def parse_arguments():
    """
        Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='Parameters for the experiment')
    parser.add_argument('-e', '--err-meths', default=["mean_err"], nargs="+", help="Functions to computer errors.")
    parser.add_argument('-o', '--outlier-removal', default="true", choices=["true", "false"],
                        help="Whether to remove outliers or not.")
    parser.add_argument('-s', '--estimate', default=["True"], nargs="+")
    parser.add_argument('-c', '--cutoffs', default=[0.1], nargs="+", help="Error cutoff value.")
    parser.add_argument('-m', '--sameclass', action="store_true")  # False by default
    parser.add_argument('-f', '--failback', action="store_true")  # False by default
    parser.add_argument('-p', '--pref', choices=["slab", "clus"], required=True,
                        help="Whether the preference is for the slab predicted or the clus (most voted in the cluster)")
    parser.add_argument('-d', '--draw', action="store_true")

    args = parser.parse_args()
    estimates = [e.lower() == "true" for e in args.estimate]
    if args.pref == "slab":
        pref = SLabMer.SLAB_PREF
    elif args.pref == "clus":
        pref = SLabMer.CLUS_PREF

    return args.err_meths, args.outlier_removal == "true", estimates, [float(co) for co in args.cutoffs], \
           args.sameclass, args.failback, pref, args.draw


def draw_clusters(clusterer):
    print(len(clusterer.groups))
    cirs = []
    rows = []
    num_y = 2
    for idx, g in enumerate(clusterer.groups):
        print("\n===== %d ======" % idx)
        circle2 = plt.Circle((idx+0.5, (idx % num_y) + 0.5), 0.6, color='grey', zorder=0, fill=True)
        cirs.append(circle2)
        num_ele = len(g)
        for i, ele in enumerate(g):
            new_x = random.uniform(idx, idx+1)
            percen = (i+1) / (num_ele+1)
            yshift = random.uniform(percen-0.1, percen+0.1)
            # yshift = i/(num_ele
            # new_y = random.uniform(idx % num_y, (idx % num_y) + 1)
            new_y = (idx % num_y) + yshift
            r = [new_x, new_y, ele['property'].split('/')[-1].split('#')[-1]]
            rows.append(r)
            print("%s -- \t %s" % (ele['property'], ele['fname']))
    df = pd.DataFrame(rows, columns=['x', 'y', 'prop'])
    fig, ax = plt.subplots()
    for c in cirs:
        ax.add_patch(c)

    sns.scatterplot(x='x', y='y', hue='prop', style='prop', palette="hls", data=df, s=100)
    # circle2 = plt.Circle((0, 5), 0.5, color='b', fill=False)
    # ax.add_patch(circle2)
    # plt.legend(bbox_to_anchor=(1.0, 1),ncol=3, loc='upper left', borderaxespad=0)
    plt.legend(bbox_to_anchor=(0, 0), ncol=8, loc='upper left', borderaxespad=0)
    ax.plot()
    # fig.savefig('analysis.svg')
    plt.show()


def main(err_meths, outlier_removal, estimates, cutoffs, sameclass, candidate_failback, pref, draw):
    scores = []
    for estimate in estimates:
        scores_per_param = dict()
        for err_meth in err_meths:
            # folder_name = get_folder_name_from_params(err_meth, estimate, remove_outliers, loose=False)
            for err_cutoff in cutoffs:

                score, clusterer = annotate_t2dv2_single_param_set(endpoint=SPARQL_ENDPOINT, data_dir=data_dir,
                                                                   df=fetch_t2dv2_data(),
                                                                   remove_outliers=outlier_removal, fetch_method="max",
                                                                   err_meth=err_meth, estimate=estimate,
                                                                   same_class=sameclass, pref=pref,
                                                                   err_cutoff=err_cutoff, print_pred=True,
                                                                   candidate_failback=candidate_failback)
                score['ro'] = outlier_removal
                score['est'] = estimate
                score['err_meth'] = err_meth
                score['same_class'] = sameclass
                score['cutoff'] = err_cutoff
                scores.append(score)
                update_scores_params_dict(scores_per_param, score, err_meth=err_meth, cutoff=err_cutoff)
                print(score)
                print("\n\n")
                draw_clusters(clusterer)

    print(scores)


if __name__ == '__main__':
    if 't2dv2_dir' not in os.environ:
        print("ERROR: t2dv2_dir no in os.environ")

    data_dir, _, _ = get_dirs()

    a = datetime.now()
    err_meths, outlier_removal, estimates, cutoffs, sameclass, candidate_failback, pref, draw = parse_arguments()
    main(err_meths, outlier_removal, estimates, cutoffs, sameclass, candidate_failback, pref, draw)
    b = datetime.now()
    print("\n\nTime it took: %.1f minutes\n\n" % ((b - a).total_seconds() / 60.0))
