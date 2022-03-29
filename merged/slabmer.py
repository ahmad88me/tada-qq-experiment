from tadaqq.slabel import SLabel
from collections import Counter
from tadaqq.util import uri_to_fname
from slabelexp.common import compute_scores

class SLabMer:

    def __init__(self, endpoint):
        self.sl = SLabel(endpoint)

    def annotate_cluster(self, group, remove_outliers, estimate, err_meth, k=3):
        """
        Store the predicted properties and assign a single candidate for each element in the given group
        :param group:
        :param remove_outliers:
        :param estimate:
        :param err_meth:
        :param k:
        :return:
        """
        pred_classes = []
        for ele in group:
            pred = self.sl.annotate_column(ele['col'], class_uri=ele['class_uri'], remove_outliers=remove_outliers,
                                           estimate=estimate, err_meth=err_meth)
            pred = pred[:k]
            ele['preds'] = [perr[1] for perr in pred]
            for p in pred:
                pred_classes.append(p)
        c = Counter(pred_classes)
        freqs = c.most_common()

        for ele in group:
            for prop_uri, fre in freqs:
                if prop_uri in ele['preds']:
                    ele['candidate'] = prop_uri
                    break

    def annotate_clusters(self, groups, remove_outliers, estimate, err_meth, k=3):
        for g in groups:
            self.annotate_cluster(g, remove_outliers, estimate, err_meth, k)

    def evaluate_labelling(self, cp_groups, groups):
        """
        :param groups: list of groups. Each group is an ele


        :param cp_groups: dict
        {
            "<concept> <property>": "<concept>/<property_fname>",
        },
        :return:
        """
        eval_data = []
        for group in groups:
            for ele in group:
                corr_trans_uris = [uri_to_fname(p) for p in ele['properties']]
                res = self.sl.eval_column((0.0, ele['candidate']), correct_uris=corr_trans_uris)
                eval_data.append(res)

        prec, rec, f1 = compute_scores(eval_data, k=1)
        return prec, rec, f1


