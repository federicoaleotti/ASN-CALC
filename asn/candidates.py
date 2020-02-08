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
                if row[1] != candidatesByName[row[0]]['level'] or row[2] != candidatesByName[row[0]]['session'] or row[3] != candidatesByName[row[0]]['journalDois'] or row[4] != candidatesByName[row[0]]['dois']:
                    candidatesByName[row[0]] = {
                        'name': row[0], 'level': row[1], 'session': row[2], 'journalDois': row[3], 'dois': row[4]}
                    candidates[candidatesIndex] = {
                        'name': row[0], 'level': row[1], 'session': row[2], 'journalDois': row[3], 'dois': row[4]}
                    candidatesIndex = candidatesIndex + 1
            else:
                candidatesByName[row[0]] = {
                    'name': row[0], 'level': row[1], 'session': row[2], 'journalDois': row[3], 'dois': row[4]}
                candidates[candidatesIndex] = {
                    'name': row[0], 'level': row[1], 'session': row[2], 'journalDois': row[3], 'dois': row[4]}
                candidatesIndex = candidatesIndex + 1
    if not os.path.exists('./data/tmp'):
        os.makedirs('./data/tmp')
    open('./data/tmp/BACKUP_CANDIDATES_OUT.csv', 'a').close()
    shutil.copyfile(filename, './data/tmp/BACKUP_CANDIDATES_OUT.csv')
    os.remove(filename)
    try:
        asn.createCSV(candidates, filename, [
                      'name', 'level', 'session', 'journalDois', 'dois'], 0)
    except:
        print('Error while refactoring CANDIDATES_OUT')
        open(filename, 'a').close()
        os.remove('./data/tmp/BACKUP_CANDIDATES_OUT.csv')
    finally:
        os.remove('./data/tmp/BACKUP_CANDIDATES_OUT.csv')


# RIMOZIONE DAL FILE PUBLICATION_DATES DELLE ENTRIES DOPPIE
def cleanPublicationCSV(filename):
    publications = {}
    with open(filename) as document:
        reader = csv.reader(document, delimiter=",")
        next(reader)
        for row in reader:
            if not row[0] in publications:
                publications[row[0]] = row[1]
            else:
                if row[1] != publications[row[0]]:
                    publications[row[0]] = min(row[1], publications[row[0]])
    if not os.path.exists('./data/tmp'):
        os.makedirs('./data/tmp')
    open('./data/tmp/BACKUP_PUBLICATION_DATES.csv', 'a').close()
    shutil.copyfile(filename, './data/tmp/BACKUP_PUBLICATION_DATES.csv')
    os.remove(filename)
    try:
        asn.createPublicationDatesCSV(publications, filename)
    except:
        print('Error while refactoring PUBLICATION_DATES.csv')
        open(filename, 'a').close()
        shutil.copyfile('./data/tmp/BACKUP_PUBLICATION_DATES.csv', filename)
        os.remove('./data/tmp/BACKUP_PUBLICATION_DATES.csv')
    finally:
        os.remove('./data/tmp/BACKUP_PUBLICATION_DATES.csv')


# INVOCAZIONE DELL'API CROSSREF PER FARSI RESTITUIRE I DATI RELATIVI AD UN DOI
# VIENE VERIFICATO CHE IL DOI SIA COLLEGATO AD UN ARTICOLO PUBBLICATO SU UN JOURNAL E VIENE RESTITUITA LA LISTA DEGLI AUTORI
def checkDoiJournalArticle(doi):
    isJournal = False
    author = []
    publicationDate = 0
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
        publicationDate = min(printDate, onlineDate)
        return isJournal, author, publicationDate
    except KeyboardInterrupt:
        exit()
    except:
        print('DOI NOT FOUND: ', doi)
        return isJournal, author, publicationDate


# ELABORAZIONE DEL TSV DEI CANDIDATI MEDIANTE INVOCAZIONE AI SERVIZI CROSSREF
def formatData(filename, calculatedRows, candidatesCSV, publicationDatesCSV):
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
                publicationDates = {}
                for doi in doisArray:
                    check, author, publicationDate = checkDoiJournalArticle(
                        doi)
                    if check:
                        journalDois.append(doi)
                    if publicationDate != 0 and publicationDate != 9999:
                        publicationDates[doi] = publicationDate
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
                if len(publicationDates) > 0:
                    asn.createPublicationDatesCSV(
                        publicationDates, publicationDatesCSV)
            candidates = {}
            print('END ROW ' + str(doneRows))
            doneRows = doneRows + 1
            calculatedRows = calculatedRows + 1
    cleanCandidatesCSV(candidatesCSV)
    cleanPublicationCSV(publicationDatesCSV)


# VERIFICA DELLO STATO DI AVANZAMENTO DELL'ANALISI DEL TSV CORRISPONDENTE AL NUMERO DI RIGHE MEMORIZZATE NEL FILE CSV
def checkProcess(filename):
    with open(filename) as document:
        reader = csv.reader(document, dialect='excel-tab')
        next(reader)
        calculatedRows = 0
        for _ in reader:
            calculatedRows = calculatedRows + 1
    return calculatedRows
