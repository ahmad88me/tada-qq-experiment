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


def tech_max_score_each(results_path):
    """
    Get the max precision, recall, and F1 independently
    :param results_path:
    :return:
    """
    df = pd.read_csv(results_path)
    dfo = df[df.F1 == df['F1'].max()].iloc[0]
    f1 = dfo['F1']
    dfo = df[df.Precision == df['Precision'].max()].iloc[0]
    prec = dfo['Precision']
    dfo = df[df.Recall == df['Recall'].max()].iloc[0]
    rec = dfo['Recall']
    # prec, rec, f1 = df['Precision'], df['Recall'], df['F1']
    return prec, rec, f1

def tech_min_score_each(results_path):
    """
    Get the min precision, recall, and F1 independently
    :param results_path:
    :return:
    """
    df = pd.read_csv(results_path)
    dfo = df[df.F1 == df['F1'].min()].iloc[0]
    f1 = dfo['F1']
    dfo = df[df.Precision == df['Precision'].min()].iloc[0]
    prec = dfo['Precision']
    dfo = df[df.Recall == df['Recall'].min()].iloc[0]
    rec = dfo['Recall']
    # prec, rec, f1 = df['Precision'], df['Recall'], df['F1']
    return prec, rec, f1

def draw_range(results):
    """

    :param results:
    :return:
    """
    df = pd.DataFrame(results, columns=['Technique', 'Precision', 'Recall', 'F1'])
    print(df)
    df_melted = pd.melt(df, id_vars=['Technique'], value_vars=['Precision', 'Recall', 'F1'], var_name="Measure",
                        value_name="Value")
    print(df_melted)
    colors = ["#c72a85", "#ffb40e", "#1f77b4"]
    p = sns.color_palette(colors)
    # ax = sns.boxplot(data=df, x="F1", y="Technique",palette=p)

    #ax = sns.boxplot(data=df_melted, x="Value", y="Technique", hue="Measure", palette=p, whis=100, showfliers=False, dodge=True)

    # ax.legend(loc='lower right')
    # ax = sns.lineplot(data=df_melted, x="Value", y="Technique", hue="Measure", style="Technique", palette=p, linewidth=10)
    ax = sns.lineplot(data=df, x="F1", y="Technique", hue="Technique", palette=p, linewidth=20)

    # techs = list(set(df['Technique']))
    # for t in techs:
    #     ax = sns.lineplot(data=df_melted[df_melted.Technique==t], x="Value", y="Technique", hue="Measure", palette=p, linewidth=10)
    # ax = sns.scatterplot(data=df_melted, x="Value", y="Technique", hue="Measure", style="Measure", palette=p)

    plt.show()
# def draw_range(df):
#     """
#
#     :param df:
#     :return:
#     """
#     df_melted = pd.melt(df, id_vars=['Technique'], value_vars=['Precision', 'Recall', 'F1'], var_name="Measure",
#                         value_name="Value")
#     print(df_melted)
#     colors = ["#c72a85", "#ffb40e", "#1f77b4"]
#     p = sns.color_palette(colors)
#     # ax = sns.boxplot(data=df, x="F1", y="Technique",palette=p)
#     ax = sns.boxplot(data=df_melted, x="Value", y="Technique", hue="Measure", palette=p, whis=100, dodge=True)
#     # ax.legend(loc='lower right')
#     # (
#     #     so.Plot(df_melted, x="Value", y="Technique", color="Measure")
#     #     .add(so.Dot(), so.Agg(), so.Dodge())
#     #     .add(so.Range(), so.Est(errorbar="sd"), so.Dodge())
#     # )
#     plt.show()


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
    fpath = os.path.join('results', 'comparison-optimal.')
    ax.figure.savefig(fpath+"svg", bbox_inches="tight")
    ax.figure.savefig(fpath+"eps", bbox_inches="tight")
    ax.figure.clf()


def workflow():
    techs_names = {
        'ks': 'KS',
        'slabelling': 'QQ',
        'merged-clus': 'mered',
        'merged-slab': 'mered'
        # 'merged-clus': 'm-clus',
        # 'merged-slab': 'm-slab'
    }
    results = []
    results_range = []
    df = pd.DataFrame([], columns=['Technique', 'Precision', 'Recall', 'F1'])
    for tech in techs_names:
        p = os.path.join('results', tech, 'results.csv')
        prec, rec, f1 = tech_max_score(p)
        res = (techs_names[tech], prec, rec, f1)
        results.append(res)


        prec, rec, f1 = tech_max_score_each(p)
        res = (techs_names[tech], prec, rec, f1)
        results_range.append(res)
        prec, rec, f1 = tech_min_score_each(p)
        res = (techs_names[tech], prec, rec, f1)
        results_range.append(res)

        # df_raw = pd.read_csv(p)
        # df_mod = df_raw[['Precision', 'Recall', 'F1']]
        # df_mod = df_mod.assign(Technique=techs_names[tech])
        # df = df.append(df_mod)

    # print(df)
    draw_range(results_range)
    print(results)
    #draw(results)

workflow()
# p = os.path.join('results', 'ks', 'results.csv')
# prec, rec, f1 = tech_max_score(p)
# print(f1)