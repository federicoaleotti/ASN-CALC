import csv
import asn


# INCROCIO DEI DATI CONTENUTI NEL CSV DEI CANDIDATI, NEL CSV DELLE CITAZIONI E NEL CSV DEI SETTORI
# VENGONO CONTATI GLI ARTICOLI, IL NUMERO TOTALE DELLE CITAZIONI E VIENE CALCOLATO L'H-INDEX
# L'H-INDEX VIENE CALCOLATO COSTRUENDO UNA LISTA ORDINATA IN ORDINE DECRESCENTE DEL NUMERO DI CITAZIONI RICEVUTE DA CIASCUN DOI
# SUCCESSIVAMENTE SI ITERA SULLA LISTA FINO A QUANDO L'N-ESIMO NON HA UN VALORE MINORE DELL'ITERATORE + 1
# IL VALORE DELL'H-INDEX CORRISPONDE AL VALORE DELL'ITERATORE
def crossData(candidates, citations):
    crossData = {}
    for candidate in candidates:
        numberOfCitations = 0
        articles = 0
        citationsList = []  # UTILE PER IL CALCOLO DELL'H-INDEX
        name = candidates[candidate]['name']
        journalDois = candidates[candidate]['journalDois'].split(', ')
        dois = candidates[candidate]['dois'].split(', ')
        for _ in journalDois:
            articles = articles + 1
        for doi in dois:
            if doi in citations:
                numberOfCitations = numberOfCitations + int(citations[doi])
                citationsList.append(int(citations[doi]))
        citationsList = sorted(citationsList, reverse=True)
        hIndex = 0
        for i, citation in enumerate(citationsList):
            if citation >= i + 1:  # CONTROLLO PER INCREMENTARE L'H-INDEX. i+1 PERCHE' i PARTE DA 0
                hIndex = hIndex + 1
        crossData[candidate] = {'name': name, 'articles': articles,
                                'citations': numberOfCitations, 'hindex': hIndex}
    return crossData
