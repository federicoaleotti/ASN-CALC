import asn
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from matplotlib import pyplot as plt
import numpy as np


def sampleGraph():
    data = pd.read_csv('./data/CROSS_DATA.csv')
    citations = data["citations"]
    hindex = data["hindex"]
    plt.scatter(citations, hindex)
    plt.savefig("./data/images/CITATIONS_HINDEX.png")
    plt.show()


def validHistogram(validCalc, validReal):
    d = {0: validCalc, 1: validReal}
    df = pd.DataFrame(data=d)
    df.hist(column='Numero di candidati che rispettano i requisiti')


def makeHistogram(firstLevelOverall, firstLevelArticles, firstLevelCitations, firstLevelHindex,
                  secondLevelOverall, secondLevelArticles, secondLevelCitations, secondLevelHindex, subject):

    # data to plot
    n_groups = 4
    level_1 = (firstLevelOverall, firstLevelArticles, firstLevelCitations, firstLevelHindex)
    level_2 = (secondLevelOverall, secondLevelArticles, secondLevelCitations, secondLevelHindex)

    # create plot
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.35
    opacity = 0.8

    rects1 = plt.bar(index, level_1, bar_width,
                    alpha=opacity,
                    color='b',
                    label='Level 1')

    rects2 = plt.bar(index + bar_width, level_2, bar_width,
                    alpha=opacity,
                    color='g',
                    label='Level 2')

    plt.xlabel('index')
    plt.ylabel('percentage')
    plt.title(subject)
    plt.xticks(index + bar_width, ('Overall', 'Articles', 'Citations', 'Hindex'))
    plt.legend()

    plt.tight_layout()
    plt.savefig("./data/images/" + subject + ".png")
