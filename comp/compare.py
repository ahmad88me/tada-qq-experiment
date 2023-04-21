"""
This is to compare the best semantic labelling techniques with their scores
"""
import seaborn as sns
import pandas as pd
import os
import matplotlib.pyplot as plt
import itertools


def tech_max_score(results_path):
    df = pd.read_csv(results_path)
    df = df[df.F1 == df['F1'].max()].iloc[0]
    print(df)
    prec, rec, f1 = df['Precision'], df['Recall'], df['F1']
    return prec, rec, f1

def draw(results):
    #df = pd.DataFrame([[]], columns=['Technique', 'Measure' ,'Value'])
    transformed_results = []
    for res in results:
        line = [res[0], 'Precision', res[1]]
        transformed_results.append(line)
        line = [res[0], 'Recall', res[2]]
        transformed_results.append(line)
        line = [res[0], 'F1', res[3]]
        transformed_results.append(line)

    df = pd.DataFrame(transformed_results, columns=['Technique', 'Measure' ,'Value'])


    colors = ["#c72a85", "#ffb40e", "#1f77b4"]
    p = sns.color_palette(colors)
    ax = sns.barplot(x="Technique", y="Value", hue="Measure", data=df, palette=p, ci=None)

    # # # Set your custom color palette
    # # p = sns.color_palette(colors)
    # # df = pd.DataFrame(rows, columns=['settings', 'metric', 'value'])
    # # ax = sns.barplot(x="settings", y="value", hue="metric", data=df, palette=p, ci=None)
    #
    # # To add Hatch
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
    #
    # num_locations = len(df.Measure.unique())
    # hatches = itertools.cycle(['/', '//', '+', '-', 'x', '\\', '*', 'o', 'O', '.'])
    # hatches = itertools.cycle(["--", "\\\\", "+"])
    # for i, bar in enumerate(ax.patches):
    #     if i % num_locations == 0:
    #         hatch = next(hatches)
    #     bar.set_hatch(hatch)
    #     bar.set_edgecolor([1, 1, 1])

    ax.set(xlabel=None, ylabel=None)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)

    # ax.set_xticklabels(ax.get_xticklabels(), rotation=-20, size=8)
    # ax.legend(fontsize='x-small')
    ax.legend(loc='lower right')
    plt.show()
    fpath = os.path.join('results', 'comparison.')
    ax.figure.savefig(fpath+"svg", bbox_inches="tight")
    ax.figure.savefig(fpath+"eps", bbox_inches="tight")
    ax.figure.clf()


def workflow():
    techs_names = {
        'ks': 'KS',
        'slabelling': 'QQ',
        'merged-clus': 'merged',
        'merged-slab': 'merged'
    }
    results = []
    for tech in techs_names:
        p = os.path.join('results', tech, 'results.csv')
        prec, rec, f1 = tech_max_score(p)
        res = (techs_names[tech], prec, rec, f1)
        results.append(res)
    print(results)
    draw(results)

workflow()
# p = os.path.join('results', 'ks', 'results.csv')
# prec, rec, f1 = tech_max_score(p)
# print(f1)