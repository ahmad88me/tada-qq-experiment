from tadaqq.slabel import SLabel
from collections import Counter


class SLabMer:

    def __init__(self, endpoint):
        self.sl = SLabel(endpoint)

    def annotate_cluster(self, group, remove_outliers, estimate, err_meth, k=3):

        pred_classes = []
        for ele in group:
            pred = self.sl.annotate_column(ele['col'], class_uri=ele['class_uri'], remove_outliers=remove_outliers,
                                           estimate=estimate, err_meth=err_meth)
            pred = pred[:k]
            ele['preds'] = pred
            for p in pred:
                pred_classes.append(p)
        c = Counter(pred_classes)
        freqs = c.most_common()

        for ele in group:
            for prop_uri, fre in freqs:
                if prop_uri in ele['pred']:
                    ele['candidate'] = prop_uri
                    break

    def annotate_clusters(self, groups, remove_outliers, estimate, err_meth, k=3):
        for g in groups:
            self.annotate_cluster(g, remove_outliers, estimate, err_meth, k)





