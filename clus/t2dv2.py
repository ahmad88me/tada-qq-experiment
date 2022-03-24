import argparse
import os
from collections import Counter
from datetime import datetime
import pandas as pd
from slabelexp.common import is_numeric_dtype
from tadaqq.slabel.util import uri_to_fname

try:
    from clus import common
except:
    import common

SHOW_LOGS = False

if 't2dv2_dir' not in os.environ:
    print("ERROR: t2dv2_dir no in os.environ")

SPARQL_ENDPOINT = "https://en-dbpedia.oeg.fi.upm.es/sparql"
data_dir = os.path.join(os.environ['t2dv2_dir'], 'csv')
meta_dir = os.path.join(os.environ['t2dv2_dir'], 'T2Dv2_typology.csv')


def get_col(fname, colid):
    fpath = os.path.join(data_dir, fname)
    df = pd.read_csv(fpath, thousands=',')
    col = df[df.columns[int(colid)]]

    if not is_numeric_dtype(col):
        col = col.str.replace(',', '').astype(float, errors='ignore')
    col = pd.to_numeric(col, errors='coerce')
    col = col[~col.isnull()]

    return col


def get_class_property_groups(df):
    d = dict()
    counts = []
    for idx, row in df.iterrows():
        c = row["concept"]
        ps = row["property"].split(';')
        prev_identified = None
        v = "%s/%s" % (c, uri_to_fname(ps[0]).replace('-', ':'))
        for p in ps:
            k = c + " " + p
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
        counts.append(v)
    return d, Counter(counts)


def clustering_workflow(fetch_method, err_meth, err_cutoff):
    df = pd.read_csv(meta_dir)
    df = df[df.property.notnull()]
    df = df[df["concept"].notnull()]
    df = df[df["pconcept"].notnull()]
    df = df[df["loose"] != "yes"]
    cp_groups, counts = get_class_property_groups(df)
    groups = []
    for idx, row_and_i in enumerate(df.iterrows()):
        i, row = row_and_i
        # if idx >= 15:
        #     break
        col = get_col(fname=row['filename']+".csv", colid=row['columnid'])
        ele = {
            'col_id': row['columnid'],
            'fname': row['filename'],
            'col': col,
            'num': len(col),
            'concept': row['concept'],
            'property': row['property'].split(';')[0]
        }

        common.column_group_matching(groups, ele, fetch_method, err_meth, err_cutoff)

    for idx, g in enumerate(groups):
        if SHOW_LOGS:
            print("\n\nGroup %d" % idx)
            print("===========")
        for ele in g:
            k = ele['concept']+" "+ele['property']
            ele['gs_clus'] = cp_groups[k]
            if SHOW_LOGS:
                print("%s\t%s" % (ele['fname'], ele['gs_clus']))

    return common.evaluate(groups, counts)


def workflow(fetch_method, err_meth, err_cutoffs):
    scores = dict()
    for co in err_cutoffs:
        scores[co] = clustering_workflow(fetch_method=fetch_method, err_meth=err_meth, err_cutoff=co)
    if len(err_cutoffs) > 1:
        common.generate_clus_diagram(scores)


def parse_arguments():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='Parameters for the experiment')

    parser.add_argument('-e', '--err-meths', default=["mean_err"], nargs="+",
                        help="Functions to computer errors.")
    parser.add_argument('-c', '--cutoffs', default=[0.1], nargs="+",
                        help="Error cutoff value.")
    args = parser.parse_args()
    return args.err_meths, [float(co) for co in args.cutoffs]


if __name__ == '__main__':
    a = datetime.now()
    err_meths, cutoffs = parse_arguments()
    for err_m in err_meths:
        workflow(fetch_method="max", err_meth=err_m, err_cutoffs=cutoffs)
    # ["mean_err", "mean_sq_err", "mean_sq1_err"]
    b = datetime.now()
    print("Time it took")
    print((b-a).total_seconds())
    print((b-a).total_seconds()/60.0)

