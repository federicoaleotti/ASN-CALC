import csv
import requests
import asn
import os
import shutil
import ast
from crossref.restful import Works
from multiprocessing import Pool


# RIMOZIONE DAL FILE CANDIDATES_OUT DEI CANDIDATI DOPPI (SESSIONI O LIVELLI DIVERSI NON VENGONO CONSIDERATE COME DOPPI)
def cleanCandidatesCSV(filename):
    candidates = {}
    candidatesByName = {}
    with open(filename) as document:
        reader = csv.reader(document, delimiter=",")
        next(reader)
        candidatesIndex = 0
        for row in reader:
            if row[3] in candidatesByName:
                if row[0] != candidatesByName[row[3]]['session'] or row[1] != candidatesByName[row[3]]['level']:
                    candidatesByName[row[3]] = {
                        'session': row[0], 'level': row[1], 'subject': row[2], 'id': row[3], 'journal_dois': row[4], 'dois': row[5], 'real_articles': row[6], 'real_citations': row[7], 'real_hindex': row[8], 'threshold_articles': row[9], 'threshold_citations': row[10], 'threshold_hindex': row[11]}
                    candidates[candidatesIndex] = {
                        'session': row[0], 'level': row[1], 'subject': row[2], 'id': row[3], 'journal_dois': row[4], 'dois': row[5], 'real_articles': row[6], 'real_citations': row[7], 'real_hindex': row[8], 'threshold_articles': row[9], 'threshold_citations': row[10], 'threshold_hindex': row[11]}
                    candidatesIndex = candidatesIndex + 1
            else:
                candidatesByName[row[3]] = {
                    'session': row[0], 'level': row[1], 'subject': row[2], 'id': row[3], 'journal_dois': row[4], 'dois': row[5], 'real_articles': row[6], 'real_citations': row[7], 'real_hindex': row[8], 'threshold_articles': row[9], 'threshold_citations': row[10], 'threshold_hindex': row[11]}
                candidates[candidatesIndex] = {
                    'session': row[0], 'level': row[1], 'subject': row[2], 'id': row[3], 'journal_dois': row[4], 'dois': row[5], 'real_articles': row[6], 'real_citations': row[7], 'real_hindex': row[8], 'threshold_articles': row[9], 'threshold_citations': row[10], 'threshold_hindex': row[11]}
                candidatesIndex = candidatesIndex + 1
    if not os.path.exists('./data/tmp'):
        os.makedirs('./data/tmp')
    open('./data/tmp/BACKUP_CANDIDATES_OUT.csv', 'a').close()
    shutil.copyfile(filename, './data/tmp/BACKUP_CANDIDATES_OUT.csv')
    os.remove(filename)
    try:
        asn.createCSV(candidates, filename, ['session', 'level', 'subject', 'id', 'journal_dois', 'dois', 'real_articles',
                                             'real_citations', 'real_hindex', 'threshold_articles', 'threshold_citations', 'threshold_hindex'], 0)
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
    isJournal = ""
    publicationDate = 0
    printDate = 9999
    onlineDate = 9999
    works = Works()
    try:
        data = works.doi(doi)
        if 'type' in data:
            if data['type'] == 'journal-article' or data['type'] == 'book':
                isJournal = doi
        if 'published-print' in data:
            printDate = data['published-print']['date-parts'][0][0]
        if 'published-online' in data:
            onlineDate = data['published-online']['date-parts'][0][0]
        publicationDate = min(printDate, onlineDate)
        return isJournal, publicationDate, doi
    except KeyboardInterrupt:
        exit()
    except:
        print('DOI NOT FOUND: ', doi)
        return isJournal, publicationDate, doi


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
                session = row[0]
                level = row[1]
                subject = row[2]
                candidateId = row[4]
                dois = row[6]
                realData = {
                    "articles": row[8],
                    "citations": row[9],
                    "hindex": row[10]
                }
                threshold = {
                    "articles": row[13],
                    "citations": row[14],
                    "hindex": row[15]
                }
                journalDois = []
                doisArray = ast.literal_eval(dois)
                doisArray = set(doisArray)  # ELIMINA RIPETIZIONI
                publicationDates = {}
                dois = []
                results = []
                with Pool(processes=4) as pool:
                    results = pool.map(checkDoiJournalArticle, doisArray)
                for elem in results:
                    journal = elem[0]
                    publicationDate = elem[1]
                    doi = elem[2]
                    dois.append(doi)
                    if journal != "":
                        journalDois.append(journal)
                    if publicationDate != 0 and publicationDate != 9999:
                        publicationDates[doi] = publicationDate
                if len(journalDois) > 0 or len(doisArray) > 0:
                    candidates[candidateIndex] = {
                        'session': session, 'level': level, 'subject': subject, 'id': candidateId, 'journal_dois': journalDois, 'dois': dois, 'real_articles': realData['articles'], 'real_citations': realData['citations'], 'real_hindex': realData['hindex'], 'threshold_articles': threshold['articles'], 'threshold_citations': threshold['citations'], 'threshold_hindex': threshold['hindex']}
                    candidateIndex = candidateIndex + 1
                    asn.createCSV(candidates, candidatesCSV,
                                  ['session', 'level', 'subject', 'id', 'journal_dois', 'dois', 'real_articles', 'real_citations', 'real_hindex', 'threshold_articles', 'threshold_citations', 'threshold_hindex'], calculatedRows)  # SCRITTURA SUL CSV DEI CANDIDATI
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
