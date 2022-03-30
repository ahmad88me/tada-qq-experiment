

def print_md_scores(scores):
    print("\n\n| %15s | %9s | %15s | %10s | %15s | %15s | %9s | %5s |" % ("Remove Outlier", "Estimate", "Error Method",
                                                                          "Same class", "Cutoff", "Precision", "Recall",
                                                                          "F1"))
    print("|:%s:|:%s:|:%s:|:%s:|:%s:|:%s:|:%s:|:%s:|" % ("-" * 15, "-" * 9, "-" * 15, "-" * 10, "-" * 15, "-" * 15,
                                                         "-" * 9, "-" * 5))
    for sc in scores:
        ro, est, err_meth, same_class, cutoff, prec, rec, f1 = sc['ro'], sc['est'], sc['err_meth'], sc['same_class'], \
                                                       sc['cutoff'], sc['prec'], sc['rec'], sc['f1']
        if est:
            est_txt = "estimate"
        else:
            est_txt = "exact"
        ro_txt = str(ro)
        same_class_txt = str(same_class)
        print("| %15s | %9s | %15s | %10s | %15.2f | %15.2f | %9.2f | %5.2f |" % (ro_txt, est_txt, err_meth,
                                                                                  same_class_txt, cutoff, prec,
                                                                                  rec, f1))

