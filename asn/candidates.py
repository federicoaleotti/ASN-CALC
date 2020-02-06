import csv
import requests
import asn
import os
import shutil
from crossref.restful import Works


# RIMOZIONE DAL FILE CANDIDATES_OUT DEI CANDIDATI DOPPI (SESSIONI O LIVELLI DIVERSI NON VENGONO CONSIDERATE COME DOPPI)
def cleanCandidatesCSV(filename):
    candidates = {}
    candidatesByName = {}
    with open(filename) as document:
        reader = csv.reader(document, delimiter=",")
        next(reader)
        candidatesIndex = 0
        for row in reader:
            if row[0] in candidatesByName:
                if row[1] != candidatesByName[row[0]]['level'] or row[2] != candidatesByName[row[0]]['session'] or row[3] != candidatesByName[row[0]]['dois']:
                    candidatesByName[row[0]] = {
                        'name': row[0], 'level': row[1], 'session': row[2], 'dois': row[3]}
                    candidates[candidatesIndex] = {
                        'name': row[0], 'level': row[1], 'session': row[2], 'dois': row[3]}
                    candidatesIndex = candidatesIndex + 1
            else:
                candidatesByName[row[0]] = {
                    'name': row[0], 'level': row[1], 'session': row[2], 'dois': row[3]}
                candidates[candidatesIndex] = {
                    'name': row[0], 'level': row[1], 'session': row[2], 'dois': row[3]}
                candidatesIndex = candidatesIndex + 1
    if not os.path.exists('./data/tmp'):
        os.makedirs('./data/tmp')
    open('./data/tmp/BACKUP_CANDIDATES_OUT.csv', 'a').close()
    shutil.copyfile(filename, './data/tmp/BACKUP_CANDIDATES_OUT.csv')
    os.remove(filename)
    try:
        asn.createCSV(candidates, filename, [
                      'name', 'level', 'session', 'dois'], 0)
    except:
        print('Error while refactoring CANDIDATES_OUT')
        open(filename, 'a').close()
        os.remove('./data/tmp/BACKUP_CANDIDATES_OUT.csv')
    finally:
        os.remove('./data/tmp/BACKUP_CANDIDATES_OUT.csv')


# INVOCAZIONE DELL'API CROSSREF PER FARSI RESTITUIRE I DATI RELATIVI AD UN DOI
# VIENE VERIFICATO CHE IL DOI SIA COLLEGATO AD UN ARTICOLO PUBBLICATO SU UN JOURNAL E VIENE RESTITUITA LA LISTA DEGLI AUTORI
def checkDoiJournalArticle(doi):
    isJournal = False
    author = []
    pubblicationDate = 0
    printDate = 9999
    onlineDate = 9999 
    works = Works()
    try:
        data = works.doi(doi)
        if 'type' in data:
            if data['type'] == 'journal-article':
                isJournal = True
        if 'author' in data:
            author = data['author']
        if 'published-print' in data:
            printDate = data['published-print']['date-parts'][0][0]
        if 'published-online' in data:
            onlineDate = data['published-online']['date-parts'][0][0]
        pubblicationDate = min(printDate, onlineDate)
        return isJournal, author, pubblicationDate
    except KeyboardInterrupt:
        exit()
    except:
        print('DOI NOT FOUND: ', doi)
        return isJournal, author, pubblicationDate


# ELABORAZIONE DEL TSV DEI CANDIDATI MEDIANTE INVOCAZIONE AI SERVIZI CROSSREF
def formatData(filename, calculatedRows, candidatesCSV, pubblicationDatesCSV):
    candidates = {}
    with open(filename) as document:
        reader = csv.reader(document, dialect='excel-tab')
        next(reader)
        # VENGONO SALTATE LE RIGHE FINO A RAGGIUNGERE L'ULTIMA RIGA ELABORATA NELLA PRECEDENTE RUN
        for _ in range(calculatedRows):
            next(reader)
        candidateIndex = 0
        doneRows = calculatedRows + 1
        for row in reader:
            if len(row) >= 3:
                level = row[0]
                session = row[1]
                journalDois = []
                doisArray = row[2].split(", ")
                doisArray = set(doisArray)  # ELIMINA RIPETIZIONI
                authors = {}
                authorsIndex = 0
                pubblicationDates = {}
                for doi in doisArray:
                    check, author, pubblicationDate = checkDoiJournalArticle(doi)
                    if check:
                        journalDois.append(doi)
                    if pubblicationDate != 0 and pubblicationDate != 9999:
                        pubblicationDates[doi] = pubblicationDate
                    authors[authorsIndex] = author
                    authorsIndex = authorsIndex + 1
                authorsOccurrency = {}
                for work in authors:  # RICERCA DEL NOME DELL'AUTORE
                    if authors[work] is not None:
                        for author in authors[work]:
                            key = ''
                            if 'given' in author:
                                name = author['given'][:1].upper()
                            else:
                                name = ''
                            if 'family' in author:
                                surname = author['family'].upper()
                            else:
                                surname = ''
                            if surname != '' and name != '':
                                key = name + ' ' + surname
                            if key != '':
                                if key in authorsOccurrency:
                                    authorsOccurrency[key] = authorsOccurrency[key] + 1
                                else:
                                    authorsOccurrency[key] = 1
                candidateName = ''
                candidateOccurrency = 0
                for author in authorsOccurrency:
                    if authorsOccurrency[author] > candidateOccurrency:
                        candidateName = author
                        candidateOccurrency = authorsOccurrency[author]
                if len(journalDois) > 0 or len(doisArray) > 0:
                    candidates[candidateIndex] = {
                        'name': candidateName, 'level': level, 'session': session, 'journalDois': journalDois, 'dois': row[2]}
                    candidateIndex = candidateIndex + 1
                    asn.createCSV(candidates, candidatesCSV,
                                  ['name', 'level', 'session', 'journalDois', 'dois'], calculatedRows)  # SCRITTURA SUL CSV DEI CANDIDATI
                if len(pubblicationDates) > 0:
                    asn.createPubblicationDatesCSV(pubblicationDates, pubblicationDatesCSV)
            candidates = {}
            print('END ROW ' + str(doneRows))
            doneRows = doneRows + 1
            calculatedRows = calculatedRows + 1
    cleanCandidatesCSV(candidatesCSV)


# VERIFICA DELLO STATO DI AVANZAMENTO DELL'ANALISI DEL TSV CORRISPONDENTE AL NUMERO DI RIGHE MEMORIZZATE NEL FILE CSV
def checkProcess(filename):
    with open(filename) as document:
        reader = csv.reader(document, dialect='excel-tab')
        next(reader)
        calculatedRows = 0
        for _ in reader:
            calculatedRows = calculatedRows + 1
    return calculatedRows
