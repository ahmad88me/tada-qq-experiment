import argparse
import os
from collections import Counter
from datetime import datetime
import pandas as pd
from tadaqq.util import uri_to_fname
from pandas.api.types import is_numeric_dtype
from tadaqq.clus import Clusterer, PMap
from tadaqq.util import get_columns_data

try:
    from clus import common
except:
    import common

SHOW_LOGS = False
SPARQL_ENDPOINT = "https://en-dbpedia.oeg.fi.upm.es/sparql"

# if 't2dv2_dir' not in os.environ:
#     print("ERROR: t2dv2_dir no in os.environ")
#
# data_dir = os.path.join(os.environ['t2dv2_dir'], 'csv')
# meta_dir = os.path.join(os.environ['t2dv2_dir'], 'T2Dv2_typology.csv')


def get_col(data_dir, fname, colid):
    fpath = os.path.join(data_dir, fname)
    cols = get_columns_data(fpath, [colid])
    return cols[0][1]


def get_class_property_groups(df):
    """
    :param df:
    :return: d, Counter
        d: {
            "<concept> <property>": "<concept>/<property_fname>",
        },
        Counter: number of rows for each concept/property combination
            of "<concept>/<property_fname>"
    """
    d = dict()
    counts = []
    for idx, row in df.iterrows():
        c = row["concept"]
        ps = row["property"].split(';')
        prev_identified = None
        v = "%s/%s" % (c, uri_to_fname(ps[0]).replace('-', ':'))
        # Find previously identified/computed value.
        # if c == "Mountain":
        #     print(ps)

        for p in ps:
            k = c + " " + p
            # if c == "Mountain":
            #     print("k: %s" % k)
            if k in d:
                prev_identified = d[k]
                break
            d[k] = v

        if prev_identified:
            # print("picking a prev-identified\t%s\t%d" % (prev_identified, idx))
            v = prev_identified
            for p in ps:
                k = c + " " + p
                d[k] = prev_identified
                # if c == "Mountain":
                #     print("pre identified k: %s" % k)

        counts.append(v)

        # if c == "Mountain":
        #     print("v: %s" % v)

    return d, Counter(counts)


def cluster_t2dv2_df(df, data_dir, clusterer, fetch_method, err_meth, err_cutoff, same_class):
    pmaps = dict()
    # pmap = PMap()
    for idx, row_and_i in enumerate(df.iterrows()):
        i, row = row_and_i
        if row['concept'] not in pmaps:
            pmaps[row['concept']] = PMap()

        pmaps[row['concept']].add(row['property'].split(';'))
        # print("\n\tproperties: ")
        # print(row['property'].split(';'))
        # if idx >= 15:
        #     break
        col = get_col(data_dir=data_dir, fname=row['filename']+".csv", colid=row['columnid'])
        ele = {
            'class_uri': 'http://dbpedia.org/ontology/' + row['concept'],
            'col_id': row['columnid'],
            'fname': row['filename'],
            'col': col,
            'num': len(col),
            'concept': row['concept'],
            'property': pmaps[row['concept']].get(row['property'].split(';')[0]),
            'properties': row['property'].split(';')
        }
        clusterer.column_group_matching(ele, fetch_method, err_meth, err_cutoff, same_class)


def clustering_workflow(data_dir, fetch_method, err_meth, err_cutoff, same_class):
    df = pd.read_csv(meta_dir)
    df = df[df.property.notnull()]
    df = df[df["concept"].notnull()]
    df = df[df["pconcept"].notnull()]
    df = df[df["loose"] != "yes"]
    cp_groups, counts = get_class_property_groups(df)
    clusterer = Clusterer(save_memory=False)
    cluster_t2dv2_df(df, data_dir, clusterer, fetch_method, err_meth, err_cutoff, same_class)

    for idx, g in enumerate(clusterer.groups):
        if SHOW_LOGS:
            print("\n\nGroup %d" % idx)
            print("===========")
        for ele in g:
            k = ele['concept']+" "+ele['property']
            ele['gs_clus'] = cp_groups[k]
            if SHOW_LOGS:
                print("%s\t%s" % (ele['fname'], ele['gs_clus']))

    return clusterer.evaluate(counts), clusterer


def workflow(data_dir, fetch_method, err_meth, err_cutoffs, same_class, draw_clus=None):
    scores = dict()
    for co in err_cutoffs:
        scores[co], clusterer = clustering_workflow(data_dir, fetch_method=fetch_method, err_meth=err_meth, err_cutoff=co,
                                         same_class=same_class)
        if draw_clus:
            from merged.single import draw_clusters
            draw_clusters(clusterer)
    if len(err_cutoffs) > 1:
        fpath = os.path.join('results', 'clustering', 't2dv2')
        if same_class:
            fpath += "_sameclass"
        common.generate_clus_diagram(scores, fpath)


def parse_arguments():
    """
    Parse command line arguments
    """
    global SHOW_LOGS
    parser = argparse.ArgumentParser(description='Parameters for the experiment')

    parser.add_argument('-e', '--err-meths', default=["mean_err"], nargs="+", help="Functions to computer errors.")
    parser.add_argument('-c', '--cutoffs', default=[0.1], nargs="+", help="Error cutoff value.")
    parser.add_argument('-m', '--sameclass', action="store_true")  # False by default
    parser.add_argument('-r', '--range', nargs=2, default=[], help="Enter the cut-off range")
    parser.add_argument('-i', '--inc', default=0.2, help="Enter the range increment")
    parser.add_argument('-d', '--debug', action="store_true", help="Whether to show the logs or not")
    args = parser.parse_args()
    if args.debug:
        SHOW_LOGS = True

    cutoffs = [float(co) for co in args.cutoffs]
    if len(args.range) > 1:
        cutoffs = [round(v, 2) for v in common.float_range(float(args.range[0]), float(args.range[1]), float(args.inc))]

    if SHOW_LOGS:
        print("same class: ")
        print(args.sameclass)
        print("cutoffs: ")
        print(cutoffs)
    return args.err_meths, cutoffs, args.sameclass


if __name__ == '__main__':
    a = datetime.now()
    if 't2dv2_dir' not in os.environ:
        print("ERROR: t2dv2_dir no in os.environ")

    data_dir = os.path.join(os.environ['t2dv2_dir'], 'csv')
    meta_dir = os.path.join(os.environ['t2dv2_dir'], 'T2Dv2_typology.csv')

    err_meths, cutoffs, same_class = parse_arguments()
    for err_m in err_meths:
        workflow(data_dir, fetch_method="max", err_meth=err_m, err_cutoffs=cutoffs, same_class=same_class, draw_clus=len(cutoffs)==1)
    # ["mean_err", "mean_sq_err", "mean_sq1_err"]
    b = datetime.now()
    print("Time it took")
    print((b-a).total_seconds())
    print((b-a).total_seconds()/60.0)

