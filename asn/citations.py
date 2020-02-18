import csv
import asn
from datetime import datetime
import configurations


SESSIONS_MAP = configurations.SESSIONS_MAP
TIME_GAPS = configurations.TIME_GAPS


# ANALISI DEI DATI COCI
# VIENE COSTRUITO UN DIZIONARIO CONTENENTE {DOI: NUMERO_DI_CITAZIONI_RICEVUTE}
# I DOI CHE NON SONO PRESENTI TRA I DOI DEGLI ARTICOLI DEI CANDIDATI PUBBLICATI SU JOURNAL VENGONO SCARTATI
# QUANDO L'ANALISI TERMINA VIENE CREATO UN CSV CONTENENTE I DATI DEL DIZIONARIO
def analizeCociData(filename, citationsCSV, candidatesCSV):
    candidatesDois = asn.createCandidatesDoisDict(candidatesCSV)
    dois = {}
    with open(filename, encoding='utf-8') as document:
        reader = csv.reader(document, delimiter=",")
        noDate = 0
        allDois = 0
        for row in reader:
            doi = row[2]
            doi = doi.lower()
            if doi in candidatesDois:
                allDois = allDois + 1
                sessionDate = SESSIONS_MAP[6][int(
                    candidatesDois[doi]['session'])]
                sessionDate = datetime.strptime(sessionDate, '%Y-%m-%d').date()
                timeGap = TIME_GAPS['citations'][int(
                    candidatesDois[doi]['level'])]
                try:
                    if len(row[3].split('-')) == 3:
                        creation = datetime.strptime(row[3], '%Y-%m-%d').date()
                    elif len(row[3].split('-')) == 2:
                        creation = datetime.strptime(row[3], '%Y-%m').date()
                    else:
                        creation = datetime.strptime(row[3], '%Y').date()
                    if creation < sessionDate and (int(sessionDate.year)-int(creation.year)) < timeGap:
                        if doi in dois:
                            dois[doi] = dois[doi] + 1
                        else:
                            dois[doi] = 1
                except:
                    noDate = noDate + 1
                    pass
    asn.createCitationsCSV(dois, citationsCSV, 0)
    print(noDate, ' DOIS WITHOUT DATE ON ', allDois, ' DOIS')