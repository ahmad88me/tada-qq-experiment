import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd


def draw_per_meth(scores_dict, fname):
    """
    scores_dict: dict
    {
        'mean_sq_err': {
            0.1: {'prec': 1.0, 'rec': 1.0, 'f1': 1.0}}, // cutoff
            0.2: df,
        },
        'mean_err': {}
    }

    """

    rows = []
    for m in scores_dict:
        for c in scores_dict[m]:
            for metric in scores_dict[m][c]:
                row = [m, c, metric, scores_dict[m][c][metric]]
                rows.append(row)

    df_all = pd.DataFrame(rows, columns=['err_meth', 'cutoff', 'metric', 'performance'])

    for metric in ["f1", "prec", "rec"]:

        df = df_all[df_all.metric == metric]

        print("df: ")
        print(df)
        colors = ["#F26B38", "#2F9599", "#A7226E", "#EC2049", "#F7DB4F"]
        # colors = ["#F26B38", "#2F9599"]
        p = sns.color_palette(palette=colors, n_colors=len(colors), desat=None, as_cmap=True)

        ax = sns.scatterplot(x="cutoff", y="performance", data=df,
                             style='err_meth', hue="err_meth", palette=colors[:len(scores_dict)])

        linestyles = ["--", ":", "dashdot", "solid"]
        for idx, m in enumerate(scores_dict):
            sns.lineplot(data=df[df.err_meth == m], x='cutoff', y='performance', dashes=True, ax=ax,
                         linestyle=linestyles[idx], linewidth=2, color=colors[idx%len(colors)])

        # ax.legend(loc=2, fontsize='x-small')
        ax.legend(fontsize='x-small')

        ax.figure.savefig('%s-%s.svg' % (fname, metric), bbox_inches="tight")
        # plt.show()
        ax.figure.clf()


def print_md_scores(scores, do_print=True):
    res = ""
    s = "\n\n| %15s | %9s | %15s | %10s | %15s | %15s | %9s | %5s |" % ("Remove Outlier", "Estimate", "Error Method",
                                                                          "Same class", "Cutoff", "Precision", "Recall",
                                                                          "F1")
    if do_print:
        print(s)
    res += s + "\n"
    s = "|:%s:|:%s:|:%s:|:%s:|:%s:|:%s:|:%s:|:%s:|" % ("-" * 15, "-" * 9, "-" * 15, "-" * 10, "-" * 15, "-" * 15,
                                                         "-" * 9, "-" * 5)
    if do_print:
        print(s)
    res += s + "\n"
    for sc in scores:
        ro, est, err_meth, same_class, cutoff, prec, rec, f1 = sc['ro'], sc['est'], sc['err_meth'], sc['same_class'], \
                                                               sc['cutoff'], sc['prec'], sc['rec'], sc['f1']
        if est:
            est_txt = "estimate"
        else:
            est_txt = "exact"
        ro_txt = str(ro)
        same_class_txt = str(same_class)
        s = "| %15s | %9s | %15s | %10s | %15.2f | %15.2f | %9.2f | %5.2f |" % (ro_txt, est_txt, err_meth,
                                                                                  same_class_txt, cutoff, prec,
                                                                                  rec, f1)
        if do_print:
            print(s)
        res += s + "\n"

    return res
