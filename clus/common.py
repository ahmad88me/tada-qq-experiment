import pandas as pd
import seaborn as sns


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
    ax = sns.lineplot(x="Cutoff", y="Score",
                     hue="Metric",
                     data=df, linewidth=2, style="Metric",
                     # palette="colorblind",
                     # palette="Spectral",
                     # palette="pastel",
                     # palette="ch:start=.2,rot=-.3",
                     # palette="YlOrBr",
                     # palette="Paired",
                     # palette="Set2",
                     # orient="h"
                      )

    ax.legend(loc=2, fontsize='x-small')
    ax.figure.savefig('%s.svg' % fpath, bbox_inches="tight")
    # plt.show()
    # ax.figure.clf()

