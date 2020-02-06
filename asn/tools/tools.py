import csv


def checkFileIsPresent(filename):
    try:
        f = open(filename)
        f.close()
        return True
    except IOError:
        return False


# CREAZIONE O MODIFICA DI UN FILE CSV A PARTIRE DA UN DIZIONARIO CONTENENTE I DATI NELLA FORMA {0:{"COL": VAL, "COL": VAL}}
# RICEVE IN INPUT IL PATH RELATIVO DEL FILE DA CREARE O MODIFICARE
# E UN ARRAY CONTENENTE I VALORI DELLE COLONNE DEL CSV DEL TIPO ["COL1", "COL2"]
# LA MODIFICA AVVIENE COME APPEND IN CODA DELLE NUOVE RIGHE
def createCSV(data, filename, keys, calculatedRows):
    with open(filename, 'a', newline='', encoding='utf-8') as document:
        writer = csv.writer(document)
        if calculatedRows == 0:
            csvData = [keys]
        else:
            csvData = []
        for elem in data:
            rowCSV = []
            for key in keys:
                if isinstance(data[elem][key], list):
                    arrToString = ''
                    for item in data[elem][key]:
                        if not arrToString == '':
                            arrToString = arrToString + ', ' + item
                        else:
                            arrToString = item
                    rowCSV.append(arrToString)
                else:
                    rowCSV.append(data[elem][key])
            csvData.append(rowCSV)
        writer.writerows(csvData)


# CREAZIONE O MODIFICA DEL CSV DELLE CITAZIONI A PARTIRE DA UN DIZIONARIO CONTENENTE I DATI NELLA FORMA {"COL": VAL, "COL": VAL}
def createCitationsCSV(data, filename):
    with open(filename, 'a', newline='', encoding='utf-8') as document:
        writer = csv.writer(document)
        writer.writerow(['doi', 'citations'])
        for doi in data:
            row = [doi, data[doi]]
            writer.writerow(row)



def createPubblicationDatesCSV(data, filename):
    with open(filename, 'a', newline='', encoding='utf-8') as document:
        writer = csv.writer(document)
        for doi in data:
            row = [doi, data[doi]]
            writer.writerow(row)


# CREAZIONE DI UN DIZIONARIO A PARTIRE DA UN FILE CSV NELLA FORMA {0:{"COL": VAL, "COL": VAL}}
def createDict(filename):
    data = {}
    with open(filename, encoding='utf-8') as document:
        reader = csv.reader(document, delimiter=",")
        headers = next(reader)
        index = 0
        for row in reader:
            dataElem = {}
            for i, header in enumerate(headers):
                dataElem[header] = row[i]
            data[index] = dataElem
            index = index + 1
    return data


# CREAZIONE DI UN DIZIONARIO A PARTIRE DA UN FILE CSV NELLA FORMA {"COL": VAL, "COL": VAL}
def createSimpleDict(filename):
    data = {}
    with open(filename, encoding='utf-8') as document:
        reader = csv.reader(document, delimiter=",")
        next(reader)
        for row in reader:
            data[row[0]] = row[1]
    return data


# CREAZIONE DEL SET CONTENENTE I DOI DEGLI ARTICOLI PUBBLICATI SU JOURNAL DEI CANDIDATI
def createCandidatesDoisSet(filename):
    dois = set()
    with open(filename, encoding='utf-8') as document:
        reader = csv.reader(document, delimiter=",")
        next(reader)
        for row in reader:
            doisList = row[4].split(', ')
            for doi in doisList:
                dois.add(doi)
    return dois
