import asn
import signal
import sys
import os
import csv

CALCULATED_ROWS = 0
DOI_SUBJECTS_CSV = './data/DOI_SUBJECTS.csv'
CANDIDATES_CSV = './data/CANDIDATES_OUT.csv'
CITATIONS_CSV = './data/CITATIONS_OUT.csv'
CROSS_DATA_CSV = './data/CROSS_DATA.csv'


choice, path1, path2, path3, subjectsString = asn.menu()

if choice == 1:
    if asn.checkFileIsPresent(path1):
        print('GENERATING CANDIDATES')
        if asn.checkFileIsPresent(CANDIDATES_CSV):
            CALCULATED_ROWS = asn.checkProcess(CANDIDATES_CSV)
            print('RESUMING FROM ROW ' + str(CALCULATED_ROWS))
        asn.formatData(
            path1, CALCULATED_ROWS, CANDIDATES_CSV, DOI_SUBJECTS_CSV)
        # ELIMINARE LE RIPETIZIONI DEI CANDIDATI ???
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
    subjects = []
    if subjectsString != '':
        subjects = subjectsString.split(',')
    fileFound = asn.checkFileIsPresent(path1) and asn.checkFileIsPresent(path2)
    if not fileFound:
        print(path1, ' OR ', path2, ' NOT FOUND')
    else:
        ('CALCULATING INDEXES AND GENERATING GRAPHS')
        if asn.checkFileIsPresent(CROSS_DATA_CSV):
            os.remove(CROSS_DATA_CSV)
        candidates = asn.createDict(path1)
        citations = asn.createSimpleDict(path2)
        crossData = asn.crossData(candidates, citations, subjects, path3)
        candidates = {}
        citations = {}
        asn.createCSV(crossData, CROSS_DATA_CSV,
                      ['name', 'articles', 'citations', 'hindex'], 0)
        asn.sampleGraph()
