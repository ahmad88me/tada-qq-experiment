import unittest
import os
import pandas as pd
from merged.t2dv2 import annotate_t2dv2_single_param_set, SPARQL_ENDPOINT, SLabMer


class SLabMerTest(unittest.TestCase):

    def test_slabmer(self):
        use_estimate = True
        err_meth = "mean_err"
        remove_outliers = False
        meta_dir = os.path.join('tests', 'test_files', 't2dv2', 'meta-2.csv')
        data_dir = os.path.join('tests', 'test_files', 't2dv2', 'csv')
        df = pd.read_csv(meta_dir)
        scores_single, _ = annotate_t2dv2_single_param_set(SPARQL_ENDPOINT, df, remove_outliers=remove_outliers,
                                                        err_meth=err_meth, estimate=use_estimate, same_class=False,
                                                        candidate_failback=True, fetch_method="max", data_dir=data_dir,
                                                        err_cutoff=0.3, pref=SLabMer.SLAB_PREF)
        self.assertEqual(scores_single['prec'], 1.0)
        self.assertEqual(scores_single['rec'], 1.0)


if __name__ == '__main__':
    unittest.main()
