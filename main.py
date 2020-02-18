import asn
import signal
import sys
import os
import csv
import configurations
from multiprocessing import Pool, freeze_support

CANDIDATES_IN = configurations.CANDIDATES_IN
CANDIDATES_OUT = configurations.CANDIDATES_OUT
COCI_DATA = configurations.COCI_DATA
CITATIONS_OUT = configurations.CITATIONS_OUT
CROSS_DATA = configurations.CROSS_DATA
REAL_DATA = configurations.REAL_DATA
PUBLICATION_DATES = configurations.PUBLICATION_DATES
SUBJECTS = configurations.SUBJECTS

if __name__ == '__main__':
    freeze_support()
    choice = asn.mainMenu()
    if choice == 1:
        if asn.checkFileIsPresent(CANDIDATES_IN):
            calculatedRows = 0
            print('GENERATING CANDIDATES')
            if asn.checkFileIsPresent(CANDIDATES_OUT):
                calculatedRows = asn.checkProcess(CANDIDATES_OUT)
                print('RESUMING FROM ROW ' + str(calculatedRows))
            asn.formatData(
                CANDIDATES_IN, calculatedRows, CANDIDATES_OUT, PUBLICATION_DATES, CITATIONS_OUT)
        else:
            print(CANDIDATES_IN, ' NOT FOUND')
    elif choice == 2:
        if asn.checkFileIsPresent(COCI_DATA):
            print('GENERATING CITATIONS')
            if asn.checkFileIsPresent(CITATIONS_OUT):
                os.remove(CITATIONS_OUT)
            asn.analizeCociData(COCI_DATA, CITATIONS_OUT, CANDIDATES_OUT)
        else:
            print(COCI_DATA, ' NOT FOUND')
    elif choice == 3:
        fileFound = asn.checkFileIsPresent(CANDIDATES_OUT) and asn.checkFileIsPresent(
            CITATIONS_OUT) and asn.checkFileIsPresent(PUBLICATION_DATES)
        if not fileFound:
            print(CANDIDATES_OUT, ' OR ', CITATIONS_OUT,
                  ' OR ', PUBLICATION_DATES, ' NOT FOUND')
        else:
            ('CALCULATING INDEXES')
            if asn.checkFileIsPresent(CROSS_DATA):
                os.remove(CROSS_DATA)
            candidates = asn.createDict(CANDIDATES_OUT)
            citations = asn.createSimpleDict(CITATIONS_OUT)
            publicationDates = asn.createSimpleDict(PUBLICATION_DATES)
            crossData = asn.crossData(candidates, citations, publicationDates)
            candidates = {}
            citations = {}
            asn.createCSV(crossData, CROSS_DATA,
                          ['name', 'session', 'level', 'subject', 'id', 'articles', 'citations', 'hindex', 'real_articles', 'real_citations', 'real_hindex', 'threshold_articles', 'threshold_citations', 'threshold_hindex'], 0)
    elif choice == 4:
        results = asn.analizeResults(CROSS_DATA)
        subjectsFinal = []
        doAll = True
        resultsAll = {
            1: {
                'overall': 0,
                'articles': 0,
                'citations': 0,
                'hindex': 0,
            },
            2: {
                'overall': 0,
                'articles': 0,
                'citations': 0,
                'hindex': 0,
            }
        }
        if asn.checkFileIsPresent('./data/output/output.txt'):
            open('./data/output/output.txt', 'w').close()
        if len(SUBJECTS) > 0:
            subjectsFinal = SUBJECTS
        else:
            subjectsFinal = asn.getAllSubjects(CROSS_DATA)
        for subject in subjectsFinal:
            output = open('./data/output/output.txt', 'a')
            output.write('SUBJECT: ' + subject + '\n')
            firstLevelOverall = (
                results[subject][1]['matching']*100) / results[subject][1]['candidates']
            firstLevelArticles = (
                results[subject][1]['articles']*100) / results[subject][1]['candidates']
            firstLevelCitations = (
                results[subject][1]['citations']*100) / results[subject][1]['candidates']
            firstLevelHindex = (
                results[subject][1]['hindex']*100) / results[subject][1]['candidates']
            output.write('LEVEL 1\n')
            output.write('OVERALL: ' + str(firstLevelOverall) + ' ARTICLES: ' + str(firstLevelArticles) +
                         ' CITATIONS: ' + str(firstLevelCitations) + ' HINDEX: ' + str(firstLevelHindex) + '\n')
            resultsAll[1]['overall'] = resultsAll[1]['overall'] + \
                firstLevelOverall
            resultsAll[1]['articles'] = resultsAll[1]['articles'] + \
                firstLevelArticles
            resultsAll[1]['citations'] = resultsAll[1]['citations'] + \
                firstLevelCitations
            resultsAll[1]['hindex'] = resultsAll[1]['hindex'] + \
                firstLevelHindex
            secondLevelOverall = (
                results[subject][2]['matching']*100) / results[subject][2]['candidates']
            secondLevelArticles = (
                results[subject][2]['articles']*100) / results[subject][2]['candidates']
            secondLevelCitations = (
                results[subject][2]['citations']*100) / results[subject][2]['candidates']
            secondLevelHindex = (
                results[subject][2]['hindex']*100) / results[subject][2]['candidates']
            output.write('LEVEL 2\n')
            output.write('OVERALL: ' + str(secondLevelOverall) + ' ARTICLES: ' + str(secondLevelArticles) +
                         ' CITATIONS: ' + str(secondLevelCitations) + ' HINDEX: ' + str(secondLevelHindex) + '\n\n')
            resultsAll[2]['overall'] = resultsAll[2]['overall'] + \
                secondLevelOverall
            resultsAll[2]['articles'] = resultsAll[2]['articles'] + \
                secondLevelArticles
            resultsAll[2]['citations'] = resultsAll[2]['citations'] + \
                secondLevelCitations
            resultsAll[2]['hindex'] = resultsAll[2]['hindex'] + \
                secondLevelHindex
            asn.makeHistogram(firstLevelOverall, firstLevelArticles, firstLevelCitations, firstLevelHindex,
                              secondLevelOverall, secondLevelArticles, secondLevelCitations, secondLevelHindex, subject)
        if len(subjectsFinal) > 1:
            output = open('./data/output/output.txt', 'a')
            output.write('GLOBAL\n')
            output.write('LEVEL 1\n')
            output.write('OVERALL: ' + str(resultsAll[1]['overall'] / len(subjectsFinal)) + ' ARTICLES: ' + str(resultsAll[1]['articles'] / len(subjectsFinal)) +
                         ' CITATIONS: ' + str(resultsAll[1]['citations'] / len(subjectsFinal)) + ' HINDEX: ' + str(resultsAll[1]['hindex'] / len(subjectsFinal)) + '\n')
            output.write('LEVEL 2\n')
            output.write('OVERALL: ' + str(resultsAll[2]['overall'] / len(subjectsFinal)) + ' ARTICLES: ' + str(resultsAll[2]['articles'] / len(subjectsFinal)) +
                         ' CITATIONS: ' + str(resultsAll[2]['citations'] / len(subjectsFinal)) + ' HINDEX: ' + str(resultsAll[2]['hindex'] / len(subjectsFinal)) + '\n')
