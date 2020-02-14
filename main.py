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
                CANDIDATES_IN, calculatedRows, CANDIDATES_OUT, PUBLICATION_DATES)
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
                          ['session', 'level', 'subject', 'id', 'articles', 'citations', 'hindex', 'real_articles', 'real_citations', 'real_hindex', 'threshold_articles', 'threshold_citations', 'threshold_hindex'], 0)
    elif choice == 4:
        results = asn.analizeResults(CROSS_DATA)
        firstLevelOverall = (results[1]['matching']*100) / results[1]['candidates']
        firstLevelArticles = (results[1]['articles']*100) / results[1]['candidates']
        firstLevelCitations = (results[1]['citations']*100) / results[1]['candidates']
        firstLevelHindex = (results[1]['hindex']*100) / results[1]['candidates']
        secondLevelOverall = (results[2]['matching']*100) / results[2]['candidates']
        secondLevelArticles = (results[2]['articles']*100) / results[2]['candidates']
        secondLevelCitations = (results[2]['citations']*100) / results[2]['candidates']
        secondLevelHindex = (results[2]['hindex']*100) / results[2]['candidates']
        print(firstLevelOverall, firstLevelArticles, firstLevelCitations, firstLevelHindex, secondLevelOverall, secondLevelArticles, secondLevelCitations, secondLevelHindex)
        print(results)
        # asn.validHistogram(results[0]['validCalc'], results[0]['validReal'])
