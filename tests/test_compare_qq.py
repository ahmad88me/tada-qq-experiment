import unittest
import os
import numpy as np
from tadaqq.qq.qqe import QQE
from tadaqq.slabel import SLabel
from tadaqq.util import uri_to_fname
from slabelexp.t2dv2 import SPARQL_ENDPOINT, MIN_NUM_OBJ


class CompareQQ(unittest.TestCase):

    def test_compare1(self):
        line = "26310680_0_5150772059999313798.tar.gz,http://dbpedia.org/property/isoNumber,3"
        fname, p, col_id = line.split(",")
        col_id = int(col_id)
        class_uri = "http://dbpedia.org/ontology/Currency"
        remove_outliers = True
        err_meth = "mean_sq_err"
        # err_meth = "mean_err"
        data_dir = os.path.join('tests', 'test_files')
        fdir = os.path.join(data_dir, fname)+".csv"
        sl = SLabel(endpoint=SPARQL_ENDPOINT, min_num_objs=MIN_NUM_OBJ, offline_data_dir="local_data")
        preds = sl.annotate_file(fdir=fdir, class_uri=class_uri, cols=[col_id], err_meth=err_meth,
                                 remove_outliers=remove_outliers)
        # preds = sl.annotate_file(fdir=fdir, class_uri=class_uri, remove_outliers=remove_outliers, cols=[col_id],
        #                       err_meth=err_meth, print_diff=True)
        trans_p = uri_to_fname(p)
        res = sl.eval_column(preds[col_id], correct_uris=[trans_p], class_uri=class_uri, col_id=col_id, fdir=fdir,
                             diff_diagram=None)
        self.assertEqual(trans_p, preds[3][0][1].split("/")[-1][:-4])


if __name__ == '__main__':
    unittest.main()

