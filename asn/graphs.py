import asn
from matplotlib import pyplot as plt
import numpy as np
import operator


def makeHistogram(firstLevelOverall, firstLevelArticles, firstLevelCitations, firstLevelHindex,
                  secondLevelOverall, secondLevelArticles, secondLevelCitations, secondLevelHindex, subject):
    n_groups = 4
    level_1 = (firstLevelOverall, firstLevelArticles,
               firstLevelCitations, firstLevelHindex)
    level_2 = (secondLevelOverall, secondLevelArticles,
               secondLevelCitations, secondLevelHindex)
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
    plt.ylim(0, 100)
    plt.xlabel('indices')
    plt.ylabel('percentage')
    plt.title(subject)
    plt.xticks(index + bar_width/2, ('Overall',
                                     'Articles', 'Citations', 'Hindex'))
    plt.legend()
    plt.tight_layout()
    plt.savefig("./data/images/" + subject + ".png")
    plt.close()


def makeHistogramAllLevel1(results):
    subjects = []
    data = []
    dataDict = {}
    keys = {}
    for subject in results:
        if subject[:2] in keys:
            keys[subject[:2]]['overall'] = keys[subject[:2]
                                                ]['overall'] + results[subject][1]
            keys[subject[:2]]['items'] = keys[subject[:2]]['items'] + 1
        else:
            keys[subject[:2]] = {'overall': results[subject][1], 'items': 1}
    for subject in keys:
        dataDict[subject] = keys[subject]['overall']/keys[subject]['items']
    dataDict = sorted(dataDict.items(), key=operator.itemgetter(1))
    for elem in dataDict:
        data.append(elem[1])
        subjects.append(elem[0])
    n_groups = len(data)
    overall = (data)
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.8
    opacity = 0.8
    rects1 = plt.bar(index, overall, bar_width,
                     alpha=opacity,
                     color='b',
                     label='Overall Level 1')
    plt.ylim(0, 100)
    plt.xlabel('subjects')
    plt.ylabel('percentage')
    plt.title("Overall All Subjects Level 1")
    plt.xticks(index, (subjects))
    plt.legend()
    plt.tight_layout()
    plt.savefig("./data/images/OVERALL_LEVEL_1.png")
    plt.close()


def makeHistogramAllLevel2(results):
    subjects = []
    data = []
    dataDict = {}
    keys = {}
    for subject in results:
        if subject[:2] in keys:
            keys[subject[:2]]['overall'] = keys[subject[:2]
                                                ]['overall'] + results[subject][2]
            keys[subject[:2]]['items'] = keys[subject[:2]]['items'] + 1
        else:
            keys[subject[:2]] = {'overall': results[subject][2], 'items': 1}
    for subject in keys:
        dataDict[subject] = keys[subject]['overall']/keys[subject]['items']
    dataDict = sorted(dataDict.items(), key=operator.itemgetter(1))
    for elem in dataDict:
        data.append(elem[1])
        subjects.append(elem[0])
    n_groups = len(data)
    overall = (data)
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.8
    opacity = 0.8
    rects1 = plt.bar(index, overall, bar_width,
                     alpha=opacity,
                     color='b',
                     label='Overall Level 2')
    plt.ylim(0, 100)
    plt.xlabel('subjects')
    plt.ylabel('percentage')
    plt.title("Overall All Subjects Level 2")
    plt.xticks(index, (subjects))
    plt.legend()
    plt.tight_layout()
    plt.savefig("./data/images/OVERALL_LEVEL_2.png")
    plt.close()
