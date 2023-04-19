
from ks.kslabel import KSLabel, DIST_PVAL, DIST_DIFF




def annotate_t2dv2_single_column(row, sl, files_k, eval_per_prop, eval_per_sub_kind, err_meth, use_estimate,
                                 remove_outliers, folder_name, eval_data, data_dir, diffs=None):
    """
    Annotate a single column
    :param row:
    :param sl: KSLabel instance
    :param files_k:
    :param eval_per_prop:
    :param eval_per_sub_kind:
    :param err_meth:
    :param use_estimate:
    :param remove_outliers:
    :param folder_name:
    :param eval_data:
    :param data_dir:
    :param diffs:
    :return:
    """
    class_uri = 'http://dbpedia.org/ontology/' + row['concept']
    col_id = int(row['columnid'])
    uris = row['property'].split(';')
    trans_uris = [uri_to_fname(uri) for uri in uris]
    csv_fname = row['filename'] + ".csv"
    fdir = os.path.join(data_dir, csv_fname)
    # print("TEST class URI: %s" % class_uri)
    preds = sl.annotate_file(fdir=fdir, class_uri=class_uri, remove_outliers=remove_outliers, cols=[col_id],
                             err_meth=err_meth, estimate=use_estimate)

    pconcept = row['pconcept']
    sub_kind = row['sub_kind']
    if sub_kind in [None, np.nan, np.NaN]:
        sub_kind = row['kind']
    if pconcept in [None, np.nan, np.NaN]:
        print("is none")
        print(row)
    if pconcept not in eval_per_prop:
        eval_per_prop[pconcept] = []
    if sub_kind not in eval_per_sub_kind:
        eval_per_sub_kind[sub_kind] = []
    nrows = get_num_rows(fdir)
    diff_name = "%s-%s-%s" % (uri_to_fname(class_uri), uri_to_fname(uris[0]), fdir.split(os.sep)[-1])
    diff_folder_path = os.path.join("ks", "diffs", folder_name)
    if not os.path.exists(diff_folder_path):
        os.mkdir(diff_folder_path)
    for c in preds:
        diff_path = os.path.join(diff_folder_path, diff_name)
        if not diffs:
            diff_path = None
        res = sl.eval_column(preds[c], correct_uris=trans_uris, class_uri=class_uri, col_id=col_id,
                             fdir=fdir, diff_diagram=diff_path)
        files_k[fdir.split(os.sep)[-1] + "-" + str(c)] = (res, nrows)
        eval_data.append(res)
        eval_per_prop[pconcept].append(res)
        eval_per_sub_kind[sub_kind].append(res)




def annotate_t2dv2_single_param_set(endpoint, df, data_dir, remove_outliers, estimate, same_class,
                                    fetch_method, dist, print_pred=False):

def annotate_t2dv2_single_param_set(endpoint, df, err_meth_scores, err_meth, use_estimate, remove_outliers,
                                    data_dir, diffs=None, draw=False, return_files_k=False):
    sl = SLabel(endpoint=endpoint, min_num_objs=MIN_NUM_OBJ)
    eval_data = []
    scores = []
    folder_name, est_txt, remove_outliers_txt = get_folder_name_from_params(err_meth, use_estimate, remove_outliers)
    files_k = dict()
    eval_per_prop = dict()
    eval_per_sub_kind = dict()
    for idx, row in df.iterrows():
        annotate_t2dv2_single_column(row, sl, files_k, eval_per_prop, eval_per_sub_kind, err_meth, use_estimate,
                                     remove_outliers, folder_name, eval_data, data_dir=data_dir, diffs=diffs)
    # print("\n\n\nfiles_k: ")
    # print(files_k)
    # print("\n\n\n")
    # print(eval_data)
    prec, rec, f1 = compute_scores(eval_data, k=1)
    score = {
        'ro': remove_outliers,
        'est': use_estimate,
        'err_meth': err_meth,
        'prec': prec,
        'rec': rec,
        'f1': f1
    }
    scores.append(score)
    folder_new_name = os.path.join('results', 'slabelling', folder_name)
    # print("\n\n================\n %s + %s + %s\n================\n" % (est_txt, err_meth, remove_outliers_txt))
    if draw:
        compute_scores_per_key(eval_per_prop, folder_new_name)
        if SHOW_LOGS:
            print("\n\n================\n %s + %s + %s" % (est_txt, err_meth, remove_outliers_txt))
        sub_folder_name = "sub_kind-%s" % (folder_name)
        compute_scores_per_key(eval_per_sub_kind, os.path.join('results', 'slabelling', sub_folder_name),
                               print_scores=True)
        folder_new_datapoint_name = os.path.join('results', 'slabelling', "datapoints-%s" % (folder_name))
        scores_df = compute_counts(files_k, folder_new_datapoint_name)

        if est_txt not in err_meth_scores:
            err_meth_scores[est_txt] = dict()

        err_meth_scores[est_txt][err_meth] = scores_df
    if return_files_k:
        return scores, files_k
    return scores
