import os
import pandas as pd


def get_dirs():
    if 't2dv2_dir' not in os.environ:
        print("ERROR: t2dv2_dir no in os.environ")
    data_dir = os.path.join(os.environ['t2dv2_dir'], 'csv')
    meta_dir = os.path.join(os.environ['t2dv2_dir'], 'T2Dv2_typology.csv')
    properties_dir = os.path.join(os.environ['t2dv2_dir'], 'T2Dv2_properties.csv')
    return data_dir, meta_dir, properties_dir


def fetch_t2dv2_data():
    _, meta_dir, _ = get_dirs()
    df = pd.read_csv(meta_dir)
    df = df[df.property.notnull()]
    df = df[df["concept"].notnull()]
    df = df[df["pconcept"].notnull()]
    df = df[df["loose"] != "yes"]
    return df
