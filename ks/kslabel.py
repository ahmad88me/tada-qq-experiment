"""
This file is based on the code of oeg-upm/tada-qq/tadaaa/slabel/slabel.
"""
import os
import logging
from easysparql import easysparqlclass
from tadaqq import util
from tadaqq.qq.qqe import QQE
from tadaqq.util import get_data
from tadaqq.slabel import SLabel
from scipy.stats import ks_2samp

import numpy as np

from ks.common import DIST_SUP, DIST_PVAL

import pcake


def get_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


class KSLabel(SLabel):

    def annotate_column(self, col, dist, class_uri=None, properties_dirs=None, remove_outliers=False, estimate=True):
        """
        Annotate a single column
        :param col: list of objects
        :param dist: the distance measure (e.g., KS statistic or pvalue).
        :param class_uri:
        :param properties_dirs:
        :param remove_outliers:
        :param estimate:
        :return: list of pairs.
            [(err, prop_f), (err, prop_f)]
        """

        if estimate:
            mode = "asymp"
        else:
            mode = "exact"

        if properties_dirs is None:
            if not class_uri:
                err_msg = "You should either pass the class uri or the properties_dirs"
                self.logger.error(err_msg)
                print(err_msg)
                raise Exception(err_msg)
            else:
                class_dir = os.path.join(self.offline_data_dir, util.uri_to_fname(class_uri))
                properties_files = [f for f in os.listdir(class_dir) if os.path.isfile(os.path.join(class_dir, f))]
                properties_dirs = [os.path.join(class_dir, pf) for pf in properties_files]

        errs = []

        for prop_f in properties_dirs:
            objects = get_data(prop_f)
            if remove_outliers:
                objects = remove_outliers_func(objects)
            res = ks_2samp(col, objects, mode=mode)
            if dist == DIST_SUP:
                err = res.statistic
            elif dist == DIST_PVAL:
                err = 1.0 - res.pvalue
            else:
                raise Exception("Invalid dist: %s" % dist)

            item = (err, prop_f)
            errs.append(item)

        errs.sort()
        return errs

    def annotate_file(self, fdir, class_uri, remove_outliers, dist, cols=[], estimate=True, print_diff=False):
        """
        :param fdir: of the csv file to be annotated
        :param class_uri:
        :param remove_outliers: True/False
        :param cols: list of int - the ids of the numeric columns. If nothing is passed, the function will detect
        numeric columns
        :param dist:
        :param estimate: bool
        :return: dict
        {
            'colid1': errs1,
            'colid2': errs1,
        }

        errs => list of pairs
            a pair is composed of <distance or error val, fname>
        """
        self.collect_numeric_data(class_uri=class_uri)
        if not cols:
            num_cols = self.get_numeric_columns(fdir)
        else:
            num_cols = util.get_columns_data(fdir, cols)
        class_dir = os.path.join(self.offline_data_dir, util.uri_to_fname(class_uri))
        properties_files = [f for f in os.listdir(class_dir) if os.path.isfile(os.path.join(class_dir, f))]
        properties_dirs = [os.path.join(class_dir, pf) for pf in properties_files]
        preds = dict()
        if print_diff:
            print("\n\n=================")
            print(class_uri)
            print(fdir)
        self.logger.debug("\n\n=================")
        self.logger.debug(class_uri)
        self.logger.debug(fdir)
        for colobj in num_cols:
            colid, coldata = colobj
            if print_diff:
                print('Column: ' + str(colid))
                print("annotate_column")
            self.logger.debug('Column: ' + str(colid))
            self.logger.debug("annotate_column")
            errs = self.annotate_column(col=coldata, properties_dirs=properties_dirs, remove_outliers=remove_outliers,
                                   dist=dist, estimate=estimate)
            preds[colid] = errs
        return preds


# This function is copied from the
def remove_outliers_func(sample):
    """
    Remove outliers from the sample.

    sample: list
        data

    Return: list
        data without the outliers
    """
    column = sample
    if len(column) < 1:
        return []
    clean_column = []
    q1 = np.percentile(column, 25)
    q3 = np.percentile(column, 75)
    # k = 1.5
    k = 2
    lower_bound = q1 - k * (q3 - q1)
    upper_bound = q3 + k * (q3 - q1)
    for c in column:
        if c >= lower_bound and c <= upper_bound:
            clean_column.append(c)
    return clean_column
