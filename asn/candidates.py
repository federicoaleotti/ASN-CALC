import csv
import requests
import asn


CROSSREF = 'https://api.crossref.org/works/'


# INVOCAZIONE DELL'API CROSSREF PER FARSI RESTITUIRE I DATI RELATIVI AD UN DOI
# VIENE VERIFICATO CHE IL DOI SIA COLLEGATO AD UN ARTICOLO PUBBLICATO SU UN JOURNAL E VIENE RESTITUITA LA LISTA DEGLI AUTORI E DEI SETTORI
def checkDoiJournalArticle(doi):
    url = CROSSREF + doi
    subject = []
    author = []
    try:
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            if 'message' in data:
                if 'type' in data['message']:
                    if data['message']['type'] == 'journal-article':
                        if 'subject' in data['message']:
                            subject = data['message']['subject']
                        if 'author' in data['message']:
                            author = data['message']['author']
                        return True, subject, author
                    else:
                        return False, subject, author
                else:
                    return False, subject, author
            else:
                return False, subject, author
        else:
            return False, subject, author
    except requests.exceptions.RequestException as e:
        print(e)
        print('### DOI NOT FOUND ###', doi)
        return False, subject, author


# ELABORAZIONE DEL TSV DEI CANDIDATI MEDIANTE INVOCAZIONE AI SERVIZI CROSSREF
def formatData(filename, calculatedRows, candidatesCSV, doiSubjectsCSV):
    doiSubjects = {}
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
            level = row[0]
            session = row[1]
            dois = []
            doisArray = row[2].split(", ")
            doisArray = set(doisArray)  # ELIMINA RIPETIZIONI
            authors = {}
            authorsIndex = 0
            for doi in doisArray:
                check, subject, author = checkDoiJournalArticle(doi)
                if check:
                    dois.append(doi)
                    authors[authorsIndex] = author
                    authorsIndex = authorsIndex + 1
                    if subject != []:
                        doiSubjects[doi] = subject
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
            if len(dois) > 0:
                candidates[candidateIndex] = {
                    'name': candidateName, 'level': level, 'session': session, 'dois': dois}
                candidateIndex = candidateIndex + 1
                asn.createCSV(candidates, candidatesCSV,
                              ['name', 'level', 'session', 'dois'], calculatedRows)  # SCRITTURA SUL CSV DEI CANDIDATI
            if len(doiSubjects) > 0:
                # SCRITTURA SUL CSV DEI SETTORI
                asn.createDoiSubjectsCSV(doiSubjects, doiSubjectsCSV)
            doiSubjects = {}
            candidates = {}
            print('END ROW ' + str(doneRows))
            doneRows = doneRows + 1
            calculatedRows = calculatedRows + 1


# VERIFICA DELLO STATO DI AVANZAMENTO DELL'ANALISI DEL TSV CORRISPONDENTE AL NUMERO DI RIGHE MEMORIZZATE NEL FILE CSV
def checkProcess(filename):
    with open(filename) as document:
        reader = csv.reader(document, dialect='excel-tab')
        next(reader)
        calculatedRows = 0
        for _ in reader:
            calculatedRows = calculatedRows + 1
    return calculatedRows
