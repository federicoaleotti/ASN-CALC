import csv
import asn
import configurations

SUBJECTS = configurations.SUBJECTS
TIME_GAPS = configurations.TIME_GAPS
SESSIONS_MAP = configurations.SESSIONS_MAP


# INCROCIO DEI DATI CONTENUTI NEL CSV DEI CANDIDATI, NEL CSV DELLE CITAZIONI E NEL CSV DEI SETTORI
# VENGONO CONTATI GLI ARTICOLI, IL NUMERO TOTALE DELLE CITAZIONI E VIENE CALCOLATO L'H-INDEX
# L'H-INDEX VIENE CALCOLATO COSTRUENDO UNA LISTA ORDINATA IN ORDINE DECRESCENTE DEL NUMERO DI CITAZIONI RICEVUTE DA CIASCUN DOI
# SUCCESSIVAMENTE SI ITERA SULLA LISTA FINO A QUANDO L'N-ESIMO NON HA UN VALORE MINORE DELL'ITERATORE + 1
# IL VALORE DELL'H-INDEX CORRISPONDE AL VALORE DELL'ITERATORE
def crossData(candidates, citations, publicationDates):
    subjects = set(SUBJECTS)
    crossData = {}
    noFilter = True
    if len(subjects) > 0:
        noFilter = False
    for candidate in candidates:
        if noFilter or candidates[candidate]['subject'] in subjects:
            numberOfCitations = 0
            articles = 0
            citationsList = []  # UTILE PER IL CALCOLO DELL'H-INDEX
            name = candidates[candidate]['name']
            journalDois = candidates[candidate]['journalDois'].split(', ')
            dois = candidates[candidate]['dois'].split(', ')
            sessionDate = SESSIONS_MAP[int(candidates[candidate]['session'])]
            for doi in journalDois:
                timeGap = TIME_GAPS['publications'][int(candidates[candidate]['level'])]
                if doi in publicationDates: # VERIFICO CHE SIA UN DOI TEMPORALMENTE VALIDO
                    if (sessionDate - int(publicationDates[doi])) < timeGap and (sessionDate - int(publicationDates[doi])) > 0: 
                        articles = articles + 1
            for doi in dois:
                timeGap = TIME_GAPS['citations'][int(candidates[candidate]['level'])]
                if doi in publicationDates: # VERIFICO CHE SIA UN DOI TEMPORALMENTE VALIDO
                    if (sessionDate - int(publicationDates[doi])) < timeGap and (sessionDate - int(publicationDates[doi])) > 0: 
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
