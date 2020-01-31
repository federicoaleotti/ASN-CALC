import csv
import asn


# INCROCIO DEI DATI CONTENUTI NEL CSV DEI CANDIDATI, NEL CSV DELLE CITAZIONI E NEL CSV DEI SETTORI
# VENGONO CONTATI GLI ARTICOLI, IL NUMERO TOTALE DELLE CITAZIONI E VIENE CALCOLATO L'H-INDEX
# L'H-INDEX VIENE CALCOLATO COSTRUENDO UNA LISTA ORDINATA IN ORDINE DECRESCENTE DEL NUMERO DI CITAZIONI RICEVUTE DA CIASCUN DOI
# SUCCESSIVAMENTE SI ITERA SULLA LISTA FINO A QUANDO L'N-ESIMO NON HA UN VALORE MINORE DELL'ITERATORE + 1
# IL VALORE DELL'H-INDEX CORRISPONDE AL VALORE DELL'ITERATORE
def crossData(candidates, citations, subjects, subjectsCSV):
    crossData = {}
    subjectsDict = asn.createSimpleDict(
        subjectsCSV)  # DIZIONARIO {'DOI': 'SETTORI'}
    for elem in subjectsDict:
        elemSubjects = set()
        for elemSubject in subjectsDict[elem].split(', '):
            elemSubjects.add(elemSubject)
        subjectsDict[elem] = elemSubjects
    filtered = False
    if len(subjects) > 0:
        filtered = True
    for candidate in candidates:
        numberOfCitations = 0
        articles = 0
        citationsList = []  # UTILE PER IL CALCOLO DELL'H-INDEX
        name = candidates[candidate]['name']
        dois = candidates[candidate]['dois'].split(', ')
        for doi in dois:
            subjectHit = False  # CONTROLLO CHE IL DOI IN OGGETTO FACCIA PARTE DEI SETTORI RICHIESTI
            if filtered:
                for subject in subjects:
                    if doi in subjectsDict:
                        doiSubjects = subjectsDict[doi]
                        if subject in doiSubjects:
                            subjectHit = True
            else:
                subjectHit = True
            if subjectHit:  # SE IL DOI E' VALIDO INCREMENTO GLI ARTICOLI PUBBLICATI E LE CITAZIONI CHE VENGONO ANCHE INSERITE NELLA LISTA DELLE CITAZIONI
                articles = articles + 1
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
