import asn
import signal
import sys
import os
import csv

CANDIDATES_CSV = './data/CANDIDATES_OUT.csv'
CITATIONS_CSV = './data/CITATIONS_OUT.csv'
CROSS_DATA_CSV = './data/CROSS_DATA.csv'


choice, path1, path2 = asn.menu()

if choice == 1:
    if asn.checkFileIsPresent(path1):
        calculatedRows = 0
        print('GENERATING CANDIDATES')
        if asn.checkFileIsPresent(CANDIDATES_CSV):
            calculatedRows = asn.checkProcess(CANDIDATES_CSV)
            print('RESUMING FROM ROW ' + str(calculatedRows))
        asn.formatData(
            path1, calculatedRows, CANDIDATES_CSV)
    else:
        print(path1, ' NOT FOUND')
elif choice == 2:
    if asn.checkFileIsPresent(path1):
        print('GENERATING CITATIONS')
        if asn.checkFileIsPresent(CITATIONS_CSV):
            os.remove(CITATIONS_CSV)
        asn.analizeCociData(path1, CITATIONS_CSV, CANDIDATES_CSV)
    else:
        print(path1, ' NOT FOUND')
elif choice == 3:
    fileFound = asn.checkFileIsPresent(path1) and asn.checkFileIsPresent(path2)
    if not fileFound:
        print(path1, ' OR ', path2, ' NOT FOUND')
    else:
        ('CALCULATING INDEXES')
        if asn.checkFileIsPresent(CROSS_DATA_CSV):
            os.remove(CROSS_DATA_CSV)
        candidates = asn.createDict(path1)
        citations = asn.createSimpleDict(path2)
        crossData = asn.crossData(candidates, citations)
        candidates = {}
        citations = {}
        asn.createCSV(crossData, CROSS_DATA_CSV,
                      ['name', 'articles', 'citations', 'hindex'], 0)
        asn.sampleGraph()
