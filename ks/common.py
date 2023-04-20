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
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    if not logger.hasHandlers():
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


logger = get_logger(__name__, level=logging.INFO)
# logger = get_logger(__name__, level=logging.DEBUG)
esparql = easysparqlclass.EasySparql(cache_dir=".cache", logger=logger)

DIST_SUP = "sup"
DIST_PVAL = "pva"


def compute_counts_per_dist(scores_dict, fname):
    """
    This is modified from compute_counts_per_err_meth

    scores_dict: dict
    {
        'estimate': {
            'pval': df,
            'diff': df,
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
    dfs = []
    print("scores dict: ")
    print(scores_dict)
    for e in scores_dict:
        for m in scores_dict[e]:
            df1 = scores_dict[e][m]
            df1['pred'] = [e] * len(df1.index)
            df1['dist'] = [m] * len(df1.index)
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
                         style="dist")
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
            sns.lineplot(data=df[(df.pred == c) & (df.dist == m)], x='nrows', y='score', dashes=True, ax=ax,
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
    ax.figure.clf()


def print_md_scores(scores):
    """
    This is modified from print_md_scores in slabelexp
    :param scores:
    :return:
    """
    print("\n\n| %15s | %9s | %15s | %9s | %9s | %5s |" % ("remove outlier", "estimate", "distance", "Precision",
                                                           "Recall", "F1"))
    print("|:%s:|:%s:|:%s:|:%s:|:%s:|:%s:|" % ("-" * 15, "-" * 9, "-" * 15, "-" * 9, "-" * 9, "-" * 5))
    for sc in scores:
        ro, est, dist, prec, rec, f1 = sc['ro'], sc['est'], sc['dist'], sc['prec'], sc['rec'], sc['f1']
        if est:
            est_txt = "estimate"
        else:
            est_txt = "exact"
        ro_txt = str(ro)
        print("| %15s | %9s | %15s | %9.2f | %9.2f | %5.2f |" % (ro_txt, est_txt, dist, prec, rec, f1))


def generate_summary(scores, fpath=None):
    """
    This is a modified version of generate_summary
    :param scores: a list of scores. A single score is a dict with the following keys
        score = {
        'ro': remove_outliers,
        'est': use_estimate,
        'dist': dist,
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
        'dist': {
            DIST_PVAL: 'pva',
            DIST_SUP: 'sup',
        }
    }
    for s in scores:
        # lab = "%s + %s + %s" % (labels['err_meth'][s['err_meth']], labels['ro'][s['ro']], labels['est'][s['est']])
        lab = "%s + %s + %s" % (labels['dist'][s['dist']], labels['ro'][s['ro']], labels['est'][s['est']], )
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
    ax.set_xticklabels(ax.get_xticklabels(), rotation=-70)
    # ax.set_xticklabels(ax.get_xticklabels(), rotation=-20, size=8)
    # ax.legend(fontsize='x-small')
    ax.legend(loc='lower right')
    #plt.show()
    ax.figure.savefig(fpath, bbox_inches="tight")
    ax.figure.clf()
