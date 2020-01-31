import csv
import asn


# ANALISI DEI DATI COCI
# VIENE COSTRUITO UN DIZIONARIO CONTENENTE {DOI: NUMERO_DI_CITAZIONI_RICEVUTE}
# I DOI CHE NON SONO PRESENTI TRA I DOI DEGLI ARTICOLI DEI CANDIDATI PUBBLICATI SU JOURNAL VENGONO SCARTATI
# QUANDO L'ANALISI TERMINA VIENE CREATO UN CSV CONTENENTE I DATI DEL DIZIONARIO
def analizeCociData(filename, citationsCSV, candidatesCSV):
    candidatesDois = asn.createCandidatesDoisSet(candidatesCSV)
    dois = {}
    with open(filename, encoding='utf-8') as document:
        reader = csv.reader(document, delimiter=",")
        for row in reader:
            doi = row[2]
            if doi in candidatesDois:
                if doi in dois:
                    dois[doi] = dois[doi] + 1
                else:
                    dois[doi] = 1
    asn.createCitationsCSV(dois, citationsCSV)
