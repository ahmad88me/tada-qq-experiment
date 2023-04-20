import unittest
import os
import pandas as pd
from ks.t2dv2 import SPARQL_ENDPOINT, annotate_t2dv2_single_param_set
from ks.common import DIST_SUP, DIST_PVAL

class KSLabelTest(unittest.TestCase):

    def test_kslabel_diff(self):
        dist_scores = dict()
        use_estimate = True
        dist = DIST_SUP
        remove_outliers = False
        loose = False
        meta_dir = os.path.join('tests', 'test_files', 't2dv2', 'meta-ks-diff.csv')
        data_dir = os.path.join('tests', 'test_files', 't2dv2', 'csv')
        df = pd.read_csv(meta_dir)
        scores_single = annotate_t2dv2_single_param_set(SPARQL_ENDPOINT, df, dist_scores=dist_scores, dist=dist,
                                                        use_estimate=use_estimate,
                                                        remove_outliers=remove_outliers, draw=False, data_dir=data_dir)
        scores_single = scores_single[0]
        print(scores_single)
        self.assertEqual(scores_single['prec'], 1.0)
        self.assertEqual(scores_single['rec'], 1.0)

    def test_kslabel_pval(self):
        dist_scores = dict()
        use_estimate = False
        dist = DIST_PVAL
        remove_outliers = False
        loose = False
        meta_dir = os.path.join('tests', 'test_files', 't2dv2', 'meta-ks-pval.csv')
        data_dir = os.path.join('tests', 'test_files', 't2dv2', 'csv')
        df = pd.read_csv(meta_dir)
        scores_single = annotate_t2dv2_single_param_set(SPARQL_ENDPOINT, df, dist_scores=dist_scores, dist=dist,
                                                        use_estimate=use_estimate,
                                                        remove_outliers=remove_outliers, draw=False, data_dir=data_dir)
        scores_single = scores_single[0]
        print(scores_single)
        self.assertEqual(scores_single['prec'], 1.0)
        self.assertEqual(scores_single['rec'], 1.0)


if __name__ == '__main__':
    unittest.main()
