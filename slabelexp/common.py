import logging
import pandas as pd
from easysparql import easysparqlclass
import seaborn as sns
import matplotlib.pyplot as plt
from pandas.api.types import CategoricalDtype
from tadaqq.util import compute_scores

PRINT_DIFF = True


def get_logger(name, level=logging.INFO):
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(name)-12s>>  %(message)s')
    # formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


logger = get_logger(__name__, level=logging.INFO)
# logger = get_logger(__name__, level=logging.DEBUG)
esparql = easysparqlclass.EasySparql(cache_dir=".cache", logger=logger)


# def compute_scores(eval_data, k=1):
#     """
#     """
#     corr = 0
#     incorr = 0
#     notf = 0
#     for d in eval_data:
#         if d == -1:
#             notf += 1
#         elif d <= k:
#             corr += 1
#         elif d < 1:
#             err_msg = "Error: compute_scores> Invalid k <%s>" % str(d)
#             print(err_msg)
#             raise Exception(err_msg)
#         else:
#             incorr += 1
#     if corr == 0:
#         prec = 0
#         rec = 0
#         f1 = 0
#     else:
#         prec = corr / (corr+incorr)
#         rec = corr / (corr+notf)
#         f1 = 2*prec*rec / (prec+rec)
#     # print("#corr: %d\t#incorr: %d\t#notf: %d" % (corr, incorr, notf))
#     return prec, rec, f1
#     # print("Precision: %.2f\nRecall: %.2f\nF1: %.2f" % (prec, rec, f1))


def get_num_rows(fdir):
    df = pd.read_csv(fdir)
    return len(df.index)


def compute_scores_per_key(eval_pp, fname=None, print_scores=False):
    """
    eval_pp: dict

    For example (property as a key)
    {
        "generic property": [1,... ] (k values),

    }
    """
    lines = []
    print("\n\n| %15s | %15s | %15s | %5s |" % ("Key", "Precision", "Recall", "F1"))
    print("|:%s:|:%s:|:%s:|:%s:|" % ("-"*15,"-"*15,"-"*15,"-"*5,))
    for p in eval_pp:
        prec, rec, f1 = compute_scores(eval_pp[p])
        lines.append([p, 'prec', prec])
        lines.append([p, 'rec', rec])
        lines.append([p, 'f1', f1])
        # if PRINT_DIFF:
        #     print("%s: \n\t%f1.2\t%f1.2\t%f1.2" % (p, prec, rec, f1))
        if print_scores:
            print("| %15s | %15.2f | %15.2f | %5.2f| " % (p, prec, rec, f1))

    if fname:
        generate_diagram(lines, fname)


def generate_diagram(acc, draw_fname):
    """
    :param acc: acc
    :param draw_file_base: base of the diagram
    :return: None
    """
    data = pd.DataFrame(acc, columns=['Property Concept', 'Metric', 'Value'])
    ax = sns.barplot(x="Value", y="Property Concept",
                     hue="Metric",
                     data=data, linewidth=1.0,
                     # palette="colorblind",
                     palette="Spectral",
                     # palette="pastel",
                     # palette="ch:start=.2,rot=-.3",
                     # palette="YlOrBr",
                     # palette="Paired",
                     # palette="Set2",
                     orient="h")
    # ax.legend_.remove()
    # ax.legend(bbox_to_anchor=(1.01, 1), borderaxespad=0)
    ax.legend(bbox_to_anchor=(1.0, -0.1), borderaxespad=0)
    # ax.set_xlim(0, 1.0)
    # ax.set_ylim(0, 0.7)
    # Horizontal
    ticks = ax.get_yticks()
    new_ticks = [t for t in ticks]
    texts = ax.get_yticklabels()
    # print(ax.get_yticklabels())
    labels = [t.get_text() for t in texts]
    ax.set_yticks(new_ticks)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set(xlabel=None, ylabel=None)
    # print(ax.get_yticklabels())
    plt.setp(ax.lines, color='k')
    ax.figure.savefig('%s.svg' % draw_fname, bbox_inches="tight")
    # ax.figure.clf()
    ax.figure.savefig('%s.eps' % draw_fname, bbox_inches="tight")
    ax.figure.clf()


def compute_counts(files_k, fname):
    bins = [20, 30, 40, 50, 70, 100, 150, 200]
    bins_score = dict()
    for f in files_k:
        corr = 1
        if files_k[f][0] != 1:
            corr = 0
        nrows = files_k[f][1]
        added = False
        for b in bins:
            if nrows < b:
                bs = str(b)
                if bs not in bins_score:
                    bins_score[bs] = {
                        'corr': 0,
                        'notf': 0,
                        'incorr': 0
                    }
                if files_k[f][0] == 1:
                    bins_score[bs]['corr'] += 1
                elif files_k[f][0] == -1:
                    bins_score[bs]['notf'] += 1
                elif files_k[f][0] > 1:
                    bins_score[bs]['incorr'] += 1
                else:
                    raise Exception("Invalid k")
                added = True
        if not added:
            bs = "%d<" % max(bins)
            if bs not in bins_score:
                bins_score[bs] = {
                    'corr': 0,
                    'notf': 0,
                    'incorr': 0
                }
            if files_k[f][0] == 1:
                bins_score[bs]['corr'] += 1
            elif files_k[f][0] == -1:
                bins_score[bs]['notf'] += 1
            elif files_k[f][0] > 1:
                bins_score[bs]['incorr'] += 1
            else:
                raise Exception("Invalid k")

    rows = []
    for bname in bins_score:
        if bins_score[bname]['corr'] == 0:
            acc = 0
            prec = 0
            recall = 0
            f1 = 0
        else:
            acc = bins_score[bname]['corr'] / (bins_score[bname]['corr'] + bins_score[bname]['incorr'] + bins_score[bname]['notf'])
            prec = bins_score[bname]['corr'] / (bins_score[bname]['corr'] + bins_score[bname]['incorr'])
            recall = bins_score[bname]['corr'] / (bins_score[bname]['corr'] + bins_score[bname]['notf'])
            f1 = 2 * prec * recall / (prec+recall)
        tot = bins_score[bname]['corr'] + bins_score[bname]['incorr'] + bins_score[bname]['notf']
        rows.append([bname, acc, 'accuracy', tot])
        rows.append([bname, prec, 'precision', tot])
        rows.append([bname, recall, 'recall', tot])
        rows.append([bname, f1, 'f1', tot])

    #     rows.append([bname, acc, prec, recall, len(bins_score[bname])])
    # df = pd.DataFrame(rows, columns=['nrows', 'accuracy', 'precision', 'recall', 'ncols'])
    df = pd.DataFrame(rows, columns=['nrows', 'score', 'metric',  'ncols'])

    cats = [str(b) for b in bins] + ["%d<" % max(bins)]
    x_pos = dict()
    for idx, c in enumerate(cats):
        x_pos[c] = idx
    cat_type = CategoricalDtype(categories=cats, ordered=True)
    df['nrows'] = df['nrows'].astype(cat_type)

    cats = ['precision', 'recall', 'accuracy', 'f1']
    cat_type = CategoricalDtype(categories=cats)
    df['metric'] = df['metric'].astype(cat_type)
    # print(df.dtypes)
    # print(df)

    # p = sns.color_palette("flare", as_cmap=True)
    # p = sns.color_palette("mako", as_cmap=True)
    # p = sns.dark_palette("#69d", reverse=False, as_cmap=True)

    ax = sns.scatterplot(x="nrows", y="score", data=df, size="ncols", hue="metric",
                         #palette=p,
                         sizes=(40, 100))
    # legend_labels, leg_oth = ax.get_legend_handles_labels()
    # ax = sns.scatterplot(x="nrows", y="precision", data=df, size="ncols", hue="ncols",
    #                      palette=p, sizes=(40, 100), ax=ax)
    # ax = sns.scatterplot(x="nrows", y="recall", data=df, size="ncols", hue="ncols",
    #                      palette=p, sizes=(40, 100), ax=ax)

    # sns.lineplot(data=df, x='nrows', y='accuracy', dashes=True, ax=ax, linestyle="--", linewidth=1, palette=p)
    # sns.lineplot(data=df, x='nrows', y='score', dashes=True, ax=ax, linestyle="--", linewidth=1, hue="metric")
    linestyles = ["--", ":", "dashdot", "solid"]
    for idx, c in enumerate(cats):
        sns.lineplot(data=df[df.metric == c], x='nrows', y='score', dashes=True, ax=ax, linestyle=linestyles[idx], linewidth=1)

    # sns.move_legend(ax, "lower center", bbox_to_anchor=(.5, 0.5), ncol=2, title=None, frameon=False)
    # ax.set(ylim=(0, 1))
    ax.legend(loc=2, fontsize='x-small')

    # ax.legend(bbox_to_anchor=(0.1, 1.0), borderaxespad=0)
    # ax.legend(legend_labels, leg_oth, title="Number of columns")

    # Draw number of files/columns
    # for idx, row in df.iterrows():
    #     nr = row['nrows']
    #     nr = x_pos[nr]
    #     plt.text(nr, row['accuracy'], row['ncols'])

    ax.figure.savefig('%s.svg' % fname, bbox_inches="tight")
    # plt.show()
    # ax.figure.clf()
    ax.figure.savefig('%s.eps' % fname, bbox_inches="tight")
    # plt.show()
    ax.figure.clf()
    return df


def compute_counts_per_err_meth(scores_dict, fname):
    """
    scores_dict: dict
    {
        'estimate': {
            'mean_sq_err': df,
            'mean_err': df,
        },
        'exact': {}
    }

    sample df:
                nrows  score     metric  ncols
            0  200<      0   accuracy      1
            1  200<      0  precision      1
            2  200<      0     recall      1
            3  200<      0         f1      1
            4   200      0   accuracy      1
            5   200      0  precision      1
            6   200      0     recall      1
            7   200      0         f1      1
    """
    # df = pd.DataFrame()
    dfs = []
    print("scores dict: ")
    print(scores_dict)
    for e in scores_dict:
        for m in scores_dict[e]:
            df1 = scores_dict[e][m]
            df1['pred'] = [e] * len(df1.index)
            df1['method'] = [m] * len(df1.index)
            print("==============")
            print(e)
            print(m)
            print(df1)
            print("\n")
            dfs.append(df1)
    print("len dfs: %d" % len(dfs))
    df = pd.concat(dfs, ignore_index=True)
    df = df[df.metric == "f1"]

    print("df: ")
    print(df)
    # p = sns.color_palette("flare", as_cmap=True)
    # p = sns.color_palette("mako", as_cmap=True)
    # p = sns.dark_palette("#69d", reverse=False, as_cmap=True)
    # p = "mako"
    # p = sns.color_palette(palette="mako", n_colors=2, desat=None, as_cmap=False)
    colors = ["#F26B38", "#2F9599"]
    p = sns.color_palette(palette=colors, n_colors=2, desat=None, as_cmap=True)

    ax = sns.scatterplot(x="nrows", y="score", data=df, hue="pred",
                         # size="ncols",
                         palette=p,
                         style="method")
                         # sizes=(40, 100))
    # legend_labels, leg_oth = ax.get_legend_handles_labels()
    # ax = sns.scatterplot(x="nrows", y="precision", data=df, size="ncols", hue="ncols",
    #                      palette=p, sizes=(40, 100), ax=ax)
    # ax = sns.scatterplot(x="nrows", y="recall", data=df, size="ncols", hue="ncols",
    #                      palette=p, sizes=(40, 100), ax=ax)


    # With Pred
    cats = ['estimate', 'exact']
    cat_type = CategoricalDtype(categories=cats)
    df['pred'] = df['pred'].astype(cat_type)
    # sns.lineplot(data=df, x='nrows', y='accuracy', dashes=True, ax=ax, linestyle="--", linewidth=1, palette=p)
    # sns.lineplot(data=df, x='nrows', y='score', dashes=True, ax=ax, linestyle="--", linewidth=1, hue="metric")
    linestyles = ["--",  ":", "dashdot", "solid"]
    # [".33", ".66"]

    for idx, c in enumerate(scores_dict):
        # print("cat: %s" % c)
        for m in scores_dict[e]:
            sns.lineplot(data=df[(df.pred == c) & (df.method == m)], x='nrows', y='score', dashes=True, ax=ax,
                         linestyle=linestyles[idx],
                         color=colors[idx],
                         #palette=p,
                         linewidth=2)

    # for idx, c in enumerate(cats):
    #     print("cat: %s" % c)
    #     sns.lineplot(data=df[df.pred == c], x='nrows', y='score', dashes=True, ax=ax, linestyle=linestyles[idx], linewidth=1)
    #     break

    # sns.move_legend(ax, "lower center", bbox_to_anchor=(.5, 0.5), ncol=2, title=None, frameon=False)
    # ax.set(ylim=(0, 1))
    ax.legend(loc=2, fontsize='x-small')

    # ax.legend(bbox_to_anchor=(0.1, 1.0), borderaxespad=0)
    # ax.legend(legend_labels, leg_oth, title="Number of columns")

    # Draw number of files/columns
    # for idx, row in df.iterrows():
    #     nr = row['nrows']
    #     nr = x_pos[nr]
    #     plt.text(nr, row['accuracy'], row['ncols'])

    ax.figure.savefig('%s.svg' % fname, bbox_inches="tight")
    # plt.show()
    # ax.figure.clf()
    ax.figure.savefig('%s.eps' % fname, bbox_inches="tight")
    # plt.show()
    ax.figure.clf()

# OLD
# def print_md_scores(scores):
#     print("\n\n| %15s | %9s | %15s | %9s | %9s | %5s |" % ("remove outlier", "estimate", "error method", "Precision",
#                                                            "Recall", "F1"))
#     print("|:%s:|:%s:|:%s:|:%s:|:%s:|:%s:|" % ("-" * 15, "-" * 9, "-" * 15, "-" * 9, "-" * 9, "-" * 5))
#     for sc in scores:
#         ro, est, err_meth, prec, rec, f1 = sc['ro'], sc['est'], sc['err_meth'], sc['prec'], sc['rec'], sc['f1']
#         if est:
#             est_txt = "estimate"
#         else:
#             est_txt = "exact"
#         ro_txt = str(ro)
#         print("| %15s | %9s | %15s | %9.2f | %9.2f | %5.2f |" % (ro_txt, est_txt, err_meth, prec, rec, f1))

# NEW
def print_md_scores(scores, do_print=True):
    res = ""
    s = "\n\n| %15s | %9s | %15s | %9s | %9s | %5s |" % ("remove outlier", "estimate", "error method", "Precision",
                                                           "Recall", "F1")
    res += "\n"+s
    if do_print:
        print(s)

    s = "|:%s:|:%s:|:%s:|:%s:|:%s:|:%s:|" % ("-" * 15, "-" * 9, "-" * 15, "-" * 9, "-" * 9, "-" * 5)
    res += "\n"+s
    if do_print:
        print(s)

    for sc in scores:
        ro, est, err_meth, prec, rec, f1 = sc['ro'], sc['est'], sc['err_meth'], sc['prec'], sc['rec'], sc['f1']
        if est:
            est_txt = "estimate"
        else:
            est_txt = "exact"
        ro_txt = str(ro)
        s = "| %15s | %9s | %15s | %9.2f | %9.2f | %5.2f |" % (ro_txt, est_txt, err_meth, prec, rec, f1)
        res += "\n" + s
        if do_print:
            print(s)
    return res

def scores_for_spreadsheet(scores, sep=","):
    lines = []
    line = sep.join(["Remove Outlier", "Estimate", "Error Method", "Precision", "Recall", "F1"])
    lines.append(line)
    for sc in scores:
        ro, est, err_meth, prec, rec, f1 = sc['ro'], sc['est'], sc['err_meth'], sc['prec'], sc['rec'], sc['f1']
        if est:
            est_txt = "estimate"
        else:
            est_txt = "exact"
        ro_txt = str(ro)
        line = sep.join([ro_txt, est_txt, err_meth, "%.2f" % prec, "%.2f" % rec, "%.2f" % f1])
        lines.append(line)
    return "\n".join(lines)



def generate_summary(scores, fpath=None):
    """
    :param scores: a list of scores. A single score is a dict with the following keys
        score = {
        'ro': remove_outliers,
        'est': use_estimate,
        'err_meth': err_meth,
        'prec': prec,
        'rec': rec,
        'f1': f1
    }
    :param fpath:
    :return:
    """
    rows = []
    labels = {
        'ro': {True: 'ro', False: 'ra'},
        'est': {True: 'est', False: 'ext'},
        'err_meth': {
            'mean_err': 'mean err',
            'mean_sqroot_err': 'mean sqr',
            'mean_sq_err': 'mean sq'
        }
    }
    for s in scores:
        # lab = "%s + %s + %s" % (labels['err_meth'][s['err_meth']], labels['ro'][s['ro']], labels['est'][s['est']])
        lab = "%s + %s" % (labels['err_meth'][s['err_meth']], labels['est'][s['est']])
        r = [lab, 'Precision', s['prec']]
        rows.append(r)

        r = [lab, 'Recall', s['rec']]
        rows.append(r)

        r = [lab, 'F1', s['f1']]
        rows.append(r)

        # r = [labels['ro'][s['ro']], labels['est'][s['est']], s['err_meth'], 'Precision', s['prec']]
        # rows.append(r)
        # r = [labels['ro'][s['ro']], labels['est'][s['est']], s['err_meth'], 'Recall', s['rec']]
        # rows.append(r)
        # r = [labels['ro'][s['ro']], labels['est'][s['est']], s['err_meth'], 'F1', s['f1']]
        # rows.append(r)

    # colors = ["255,180,14", "44,160,131", "31,119,180"]
    # colors = ["#2ca083", "#ffb40e", "#1f77b4"]
    # colors = ["#b32979", "#ffb40e", "#1f77b4"]
    colors = ["#c72a85", "#ffb40e", "#1f77b4"]




    # Set your custom color palette
    p = sns.color_palette(colors)
    df = pd.DataFrame(rows, columns=['settings', 'metric', 'value'])
    ax = sns.barplot(x="settings", y="value", hue="metric", data=df, palette=p, ci=None)

    # To add Hatch
    # # Hatch idea:https://stackoverflow.com/questions/35467188/is-it-possible-to-add-hatches-to-each-individual-bar-in-seaborn-barplot
    # # Define some hatches
    # hatches = ['o', '-', 'x', '\\', '*', 'o']
    # # hatches += ['-', '+', 'x', '\\', '*', 'o']
    # # hatches += ['-', '+', 'x', '\\', '*', 'o']
    # # hatches += ['-', '+', 'x', '\\', '*', 'o']
    # # hatches += ['-', '+', 'x', '\\', '*', 'o']
    # # hatches += ['-', '+', 'x', '\\', '*', 'o']
    # # hatches += ['-', '+', 'x', '\\', '*', 'o']
    #
    # # Loop over the bars
    # for i, bar in enumerate(ax.patches):
    #     # Set a different hatch for each bar
    #     bar.set_hatch(hatches[i % 3])
    #     # ax['bars'][i].set(hatch="/", fill=False)

    # num_locations = len(mdf.Location.unique())
    # hatches = itertools.cycle(['/', '//', '+', '-', 'x', '\\', '*', 'o', 'O', '.'])
    # for i, bar in enumerate(ax.patches):
    #     if i % num_locations == 0:
    #         hatch = next(hatches)
    #     bar.set_hatch(hatch)

    ax.set(xlabel=None, ylabel=None)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=-15)
    # ax.set_xticklabels(ax.get_xticklabels(), rotation=-20, size=8)
    # ax.legend(fontsize='x-small')
    ax.legend(loc='lower left')
    # plt.show()
    ax.figure.savefig(fpath, bbox_inches="tight")
    ax.figure.clf()
