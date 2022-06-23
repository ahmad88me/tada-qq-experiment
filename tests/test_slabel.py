import unittest
import os
import pandas as pd
from slabelexp.t2dv2 import annotate_t2dv2_single_param_set, SPARQL_ENDPOINT


class SLabelTest(unittest.TestCase):

    def test_slabel(self):
        err_meth_scores = dict()
        use_estimate = True
        err_meth = "mean_err"
        remove_outliers = False
        loose = False
        meta_dir = os.path.join('tests', 'test_files', 't2dv2', 'meta-1.csv')
        data_dir = os.path.join('tests', 'test_files', 't2dv2', 'csv')
        df = pd.read_csv(meta_dir)
        scores_single = annotate_t2dv2_single_param_set(SPARQL_ENDPOINT, df, err_meth_scores, err_meth, use_estimate,
                                                        remove_outliers, draw=False, data_dir=data_dir)
        scores_single = scores_single[0]
        # print(scores_single)
        self.assertEqual(scores_single['prec'], 1.0)
        self.assertEqual(scores_single['rec'], 1.0)


if __name__ == '__main__':
    unittest.main()
