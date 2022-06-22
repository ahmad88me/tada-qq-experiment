import math
import matplotlib.pylab as plt
import pandas as pd
import seaborn as sns


def float_range(start, end, inc):
    vals = []
    times = math.floor((end - start) / inc)
    for i in range(times):
        vals.append(i*inc + start)
    return vals


def set_num_xticks(ax, ticks):
    """
    Original solution is from https://www.tutorialspoint.com/how-to-decrease-the-density-of-x-ticks-in-seaborn
    :param ax:
    :param ticks: target number of ticks
    :return:
    """
    old_ticks = ax.get_xticks()
    num = len(old_ticks)
    if ticks >= num:
        return
    t = math.floor(num/ticks)
    new_ticks = []
    for i in range(len(old_ticks)):
        if i % t == 0:
            new_ticks.append(old_ticks[i])
    ax.set_xticks(new_ticks)


def generate_clus_diagram(scores, fpath):
    """
    :param scores: dict
    :return: None
    """
    rows = []
    scores_titles = ["Precision", "Recall", "F1"]
    for k in scores:
        for idx, sc in enumerate(scores_titles):
            row = [str(k), scores[k][idx], scores_titles[idx]]
            rows.append(row)
        # row = [k, scores[k][0], scores[k][1], scores[k][2]]
        # rows.append(row)
    df = pd.DataFrame(rows, columns=['Cutoff', 'Score', 'Metric'])
    df['Cutoff'] = df['Cutoff'].astype('category')
    linestyles = ["--", ":", "dashdot"]
    ax = sns.lineplot(x="Cutoff", y="Score", hue="Metric", data=df, linewidth=2, style="Metric")
                     # # palette="colorblind",
                     # # palette="Spectral",
                     # # palette="pastel",
                     # # palette="ch:start=.2,rot=-.3",
                     # # palette="YlOrBr",
                     # # palette="Paired",
                     # # palette="Set2",
                     # # orient="h"
                     #  )

    set_num_xticks(ax, 8)
    ax.legend(loc='lower left', fontsize='x-small')
    ax.figure.savefig('%s.svg' % fpath, bbox_inches="tight")
    # ax.figure.savefig('%s.eps' % fpath, bbox_inches="tight")
    # plt.show()
    # ax.figure.clf()

