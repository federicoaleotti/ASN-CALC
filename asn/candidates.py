import csv
import requests
import asn
import os
import shutil
import ast
from crossref.restful import Works
from multiprocessing import Pool
import xmltodict
import json
from functools import partial
from datetime import datetime
import configurations


SESSIONS_MAP = configurations.SESSIONS_MAP
TIME_GAPS = configurations.TIME_GAPS


# RIMOZIONE DAL FILE CANDIDATES_OUT DEI CANDIDATI DOPPI (SESSIONI O LIVELLI DIVERSI NON VENGONO CONSIDERATE COME DOPPI)
def cleanCandidatesCSV(filename):
    candidates = {}
    candidatesByName = {}
    with open(filename, encoding='utf-8') as document:
        reader = csv.reader(document, delimiter=",")
        next(reader)
        candidatesIndex = 0
        for row in reader:
            if row[4] in candidatesByName:
                if row[1] != candidatesByName[row[4]]['session'] or row[2] != candidatesByName[row[4]]['level']:
                    candidates[candidatesIndex] = {
                        'name': row[0], 'session': row[1], 'level': row[2], 'subject': row[3], 'id': row[4], 'journal_dois': row[5], 'dois': row[6], 'real_articles': row[7], 'real_citations': row[8], 'real_hindex': row[9], 'threshold_articles': row[10], 'threshold_citations': row[11], 'threshold_hindex': row[12]}
                    candidatesIndex = candidatesIndex + 1
            else:
                candidatesByName[row[4]] = {
                    'name': row[0], 'session': row[1], 'level': row[2], 'subject': row[3], 'id': row[4], 'journal_dois': row[5], 'dois': row[6], 'real_articles': row[7], 'real_citations': row[8], 'real_hindex': row[9], 'threshold_articles': row[10], 'threshold_citations': row[11], 'threshold_hindex': row[12]}
                candidates[candidatesIndex] = {
                    'name': row[0], 'session': row[1], 'level': row[2], 'subject': row[3], 'id': row[4], 'journal_dois': row[5], 'dois': row[6], 'real_articles': row[7], 'real_citations': row[8], 'real_hindex': row[9], 'threshold_articles': row[10], 'threshold_citations': row[11], 'threshold_hindex': row[12]}
                candidatesIndex = candidatesIndex + 1
    if not os.path.exists('./data/tmp'):
        os.makedirs('./data/tmp')
    open('./data/tmp/BACKUP_CANDIDATES_OUT.csv', 'a').close()
    shutil.copyfile(filename, './data/tmp/BACKUP_CANDIDATES_OUT.csv')
    os.remove(filename)
    try:
        asn.createCSV(candidates, filename, ['name', 'session', 'level', 'subject', 'id', 'journal_dois', 'dois', 'real_articles',
                                             'real_citations', 'real_hindex', 'threshold_articles', 'threshold_citations', 'threshold_hindex'], 0)
    except:
        log = open('./data/tmp/log.txt', 'a')
        log.write('Error while refactoring CANDIDATES_OUT\n')
        log.close()
        open(filename, 'a').close()
        os.remove('./data/tmp/BACKUP_CANDIDATES_OUT.csv')
    finally:
        os.remove('./data/tmp/BACKUP_CANDIDATES_OUT.csv')


# RIMOZIONE DAL FILE PUBLICATION_DATES DELLE ENTRIES DOPPIE
def cleanPublicationCSV(filename):
    publications = {}
    with open(filename, encoding='utf-8') as document:
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
        log = open('./data/tmp/log.txt', 'a')
        log.write('Error while refactoring PUBLICATION_DATES.csv\n')
        log.close()
        open(filename, 'a').close()
        shutil.copyfile('./data/tmp/BACKUP_PUBLICATION_DATES.csv', filename)
        os.remove('./data/tmp/BACKUP_PUBLICATION_DATES.csv')
    finally:
        os.remove('./data/tmp/BACKUP_PUBLICATION_DATES.csv')


def queryCOCI(doi, date, timeGap):
    url = 'https://w3id.org/oc/index/coci/api/v1/citations/'
    r = requests.get(url+doi)
    data = r.json()
    citations = 0
    for elem in data:
        if len(elem['creation'].split('-')) == 3:
            elemDate = datetime.strptime(elem['creation'], '%Y-%m-%d').date()
        elif len(elem['creation'].split('-')) == 2:
            elemDate = datetime.strptime(elem['creation'], '%Y-%m').date()
        else:
            elemDate = datetime.strptime(elem['creation'], '%Y').date()
        if elemDate < date and (int(date.year)-int(elemDate.year)) < timeGap:
            citations = citations + 1
    return doi, citations


def checkAuthorDBLP(name):
    response = {}
    try:
        name = name.split('-')
        firstName = name[0]
        lastName = name[1]
        letter = lastName[:1].lower()
        url = 'https://dblp.org/pers/' + letter + \
            '/' + lastName + ':' + firstName + '.xml'
        r = requests.get(url)
        o = xmltodict.parse(r.content)
        o = json.dumps(o)
        works = json.loads(o)
        for work in works['dblpperson']['r']:
            journal = False
            if 'article' in work:
                if '@key' in work['article']:
                    if work['article']['@key'].split('/')[0] == 'journals':
                        journal = True
                if 'year' in work['article'] and 'ee' in work['article']:
                    doi = work['article']['ee']
                    if isinstance(doi, list):
                        doi = doi[0]
                        if isinstance(doi, dict):
                            doi = doi['#text']
                    try:
                        doi = doi.split('https://doi.org/')[1].lower()
                        response[doi] = {'journal': journal,
                                         'date': work['article']['year']}
                    except:
                        pass
            if 'inproceedings' in work:
                if 'year' in work['inproceedings'] and 'ee' in work['inproceedings']:
                    doi = work['inproceedings']['ee']
                    if isinstance(doi, list):
                        doi = doi[0]
                        if isinstance(doi, dict):
                            doi = doi['#text']
                    try:
                        doi = doi.split('https://doi.org/')[1].lower()
                        response[doi] = {'journal': journal,
                                         'date': work['inproceedings']['year']}
                    except:
                        pass
            if 'proceedings' in work:
                if 'year' in work['proceedings'] and 'ee' in work['proceedings']:
                    doi = work['proceedings']['ee']
                    if isinstance(doi, list):
                        doi = doi[0]
                        if isinstance(doi, dict):
                            doi = doi['#text']
                    try:
                        doi = doi.split('https://doi.org/')[1].lower()
                        response[doi] = {'journal': journal,
                                         'date': work['proceedings']['year']}
                    except:
                        pass
    except:
        pass
    return response


# INVOCAZIONE DELL'API CROSSREF PER FARSI RESTITUIRE I DATI RELATIVI AD UN DOI
# VIENE VERIFICATO CHE IL DOI SIA COLLEGATO AD UN ARTICOLO PUBBLICATO SU UN JOURNAL E VIENE RESTITUITA LA LISTA DEGLI AUTORI
def checkDoiJournalArticle(doi):
    isJournal = ""
    publicationDate = 0
    printDate = 9999
    onlineDate = 9999
    works = Works()
    author = []
    try:
        data = works.doi(doi)
        if 'type' in data:
            if data['type'] == 'journal-article':
                isJournal = doi
        if 'author' in data:
            author = data['author']
        if 'published-print' in data:
            printDate = data['published-print']['date-parts'][0][0]
        if 'published-online' in data:
            onlineDate = data['published-online']['date-parts'][0][0]
        publicationDate = min(printDate, onlineDate)
        return isJournal, publicationDate, doi, author
    except KeyboardInterrupt:
        exit()
    except:
        print('DOI NOT FOUND: ', doi)
        return isJournal, publicationDate, doi, author


def findCandidateName(authors):
    authorsOccurrency = {}
    for work in authors:  # RICERCA DEL NOME DELL'AUTORE
        if authors[work] is not None:
            for author in authors[work]:
                key = ''
                if 'given' in author:
                    name = author['given']
                else:
                    name = ''
                if 'family' in author:
                    surname = author['family']
                else:
                    surname = ''
                if surname != '' and name != '':
                    key = name + '-' + surname
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
    return candidateName


# ELABORAZIONE DEL TSV DEI CANDIDATI MEDIANTE INVOCAZIONE AI SERVIZI CROSSREF
def formatData(filename, calculatedRows, candidatesCSV, publicationDatesCSV, citationsCSV):
    candidates = {}
    with open(filename, encoding='utf-8') as document:
        reader = csv.reader(document, dialect='excel-tab')
        next(reader)
        # VENGONO SALTATE LE RIGHE FINO A RAGGIUNGERE L'ULTIMA RIGA ELABORATA NELLA PRECEDENTE RUN
        for _ in range(calculatedRows):
            next(reader)
        candidateIndex = 0
        doneRows = calculatedRows + 1
        for row in reader:
            if row[8] != '' and row[13] != '':
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
                for doi in doisArray:
                    dois.append(doi.lower())
                results = []
                authors = {}
                authorsIndex = 0
                with Pool(processes=8) as pool:
                    results = pool.map(checkDoiJournalArticle, doisArray)
                for elem in results:
                    journal = elem[0]
                    publicationDate = elem[1]
                    doi = elem[2].lower()
                    author = elem[3]
                    if journal != "":
                        journalDois.append(journal.lower())
                    if publicationDate != 0 and publicationDate != 9999:
                        publicationDates[doi] = publicationDate
                    authors[authorsIndex] = author
                    authorsIndex = authorsIndex + 1
                candidateName = findCandidateName(authors)
                dblp = checkAuthorDBLP(candidateName)
                for doi in doisArray:
                    doi = doi.lower()
                    if doi in dblp:
                        if dblp[doi]['journal'] == True:
                            if not doi in journalDois:
                                journalDois.append(doi)
                            if not doi in publicationDates:
                                publicationDates[doi] = dblp[doi]['date']
                if len(journalDois) > 0 or len(doisArray) > 0:
                    candidates[candidateIndex] = {
                        'name': candidateName, 'session': session, 'level': level, 'subject': subject, 'id': candidateId, 'journal_dois': journalDois, 'dois': dois, 'real_articles': realData['articles'], 'real_citations': realData['citations'], 'real_hindex': realData['hindex'], 'threshold_articles': threshold['articles'], 'threshold_citations': threshold['citations'], 'threshold_hindex': threshold['hindex']}
                    candidateIndex = candidateIndex + 1
                    asn.createCSV(candidates, candidatesCSV,
                                  ['name', 'session', 'level', 'subject', 'id', 'journal_dois', 'dois', 'real_articles', 'real_citations', 'real_hindex', 'threshold_articles', 'threshold_citations', 'threshold_hindex'], calculatedRows)  # SCRITTURA SUL CSV DEI CANDIDATI
                if len(publicationDates) > 0:
                    asn.createPublicationDatesCSV(
                        publicationDates, publicationDatesCSV)
                candidates = {}
            log = open('./data/tmp/log.txt', 'a')
            log.write('END ROW ' + str(doneRows) + '\n')
            log.close()
            doneRows = doneRows + 1
            calculatedRows = calculatedRows + 1
    cleanCandidatesCSV(candidatesCSV)
    cleanPublicationCSV(publicationDatesCSV)


# VERIFICA DELLO STATO DI AVANZAMENTO DELL'ANALISI DEL TSV CORRISPONDENTE AL NUMERO DI RIGHE MEMORIZZATE NEL FILE CSV
def checkProcess(filename):
    with open(filename, encoding='utf-8') as document:
        reader = csv.reader(document, dialect='excel-tab')
        next(reader)
        calculatedRows = 0
        for _ in reader:
            calculatedRows = calculatedRows + 1
    return calculatedRows
