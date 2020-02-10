import csv
import asn
import configurations

SUBJECTS = configurations.SUBJECTS
TIME_GAPS = configurations.TIME_GAPS
SESSIONS_MAP = configurations.SESSIONS_MAP
THRESHOLDS = configurations.THRESHOLDS


# VERIFICA SUGLI INDICI E LE SOGLIE
def validateCandidate(level, subject, articles, citations, hindex):
    threshold = THRESHOLDS[subject][level]
    valid = False
    if articles >= threshold["articles"] and citations >= threshold["citations"] and hindex >= threshold["hindex"]:
        valid = True
    return valid


# CONFRONTO TRA DATI CALCOLATI E DATI REALI CONSIDERANDO IL SETTORE
def matchData(crossData, subject):
    validCalc = 0
    validReal = 0
    matching = 0
    for elem in crossData:
        calc = False
        real = False
        if subject == "" or crossData[elem]['subject'] == subject:
            if validateCandidate(int(crossData[elem]['level']), crossData[elem]['subject'],
                                 int(crossData[elem]['articles']), int(crossData[elem]['citations']), int(crossData[elem]['hindex'])):
                validCalc = validCalc + 1
                calc = True
            if validateCandidate(int(crossData[elem]['level']), crossData[elem]['subject'],
                                 int(crossData[elem]['real_articles']), int(crossData[elem]['real_citations']), int(crossData[elem]['real_hindex'])):
                validReal = validReal + 1
                real = True
            if calc == real:
                matching = matching + 1
    return validCalc, validReal, matching


# ANALISI DEI RISULTATI OTTENUTI
# TIPO 1 DIVERSIFICATA TIPO - 2 UNICA
def analizeResults(crossDataCSV):
    crossData = asn.createDict(crossDataCSV)
    results = {}
    if len(SUBJECTS) > 1:
        choice = asn.typeMenu()
        if choice == 1:
            for subject in SUBJECTS:
                validCalc, validReal, matching = matchData(crossData, subject)
                results[subject] = {
                    'validCalc': validCalc, 'validReal': validReal, 'matching': matching}
        else:
            validCalc, validReal, matching = matchData(crossData, "")
            results[0] = {
                'validCalc': validCalc, 'validReal': validReal, 'matching': matching}
    else:
        validCalc, validReal, matching = matchData(crossData, "")
        results[0] = {
            'validCalc': validCalc, 'validReal': validReal, 'matching': matching}
    return results


# AGGIUNGE I DATI REALI AGLI INDICI CALCOLATI
def completeCrossData(crossData, realDataCSV):
    data = {}
    realData = asn.createCrossByIdDict(realDataCSV)
    for candidate in crossData:
        realArticles = realData[crossData[candidate]['id']
                                ][crossData[candidate]['level']]['articles']
        realCitations = realData[crossData[candidate]['id']
                                 ][crossData[candidate]['level']]['citations']
        realHindex = realData[crossData[candidate]['id']
                              ][crossData[candidate]['level']]['hindex']
        data[candidate] = {'id': crossData[candidate]['id'], 'name': crossData[candidate]['name'], 'level': crossData[candidate]['level'], 'subject': crossData[candidate]['subject'], 'articles': crossData[candidate]['articles'], 'real_articles': realArticles,
                           'citations': crossData[candidate]['citations'], 'real_citations': realCitations, 'hindex': crossData[candidate]['hindex'], 'real_hindex': realHindex}
    return data


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
            candidateId = candidates[candidate]['id']
            candidateLevel = int(candidates[candidate]['level'])
            journalDois = candidates[candidate]['journalDois'].split(', ')
            dois = candidates[candidate]['dois'].split(', ')
            sessionDate = SESSIONS_MAP[int(candidates[candidate]['session'])]
            for doi in journalDois:
                timeGap = TIME_GAPS['publications'][candidateLevel]
                if doi in publicationDates:  # VERIFICO CHE SIA UN DOI TEMPORALMENTE VALIDO
                    if (sessionDate - int(publicationDates[doi])) < timeGap and (sessionDate - int(publicationDates[doi])) > 0:
                        articles = articles + 1
            for doi in dois:
                timeGap = TIME_GAPS['citations'][candidateLevel]
                if doi in publicationDates:  # VERIFICO CHE SIA UN DOI TEMPORALMENTE VALIDO
                    if (sessionDate - int(publicationDates[doi])) < timeGap and (sessionDate - int(publicationDates[doi])) > 0:
                        if doi in citations:
                            numberOfCitations = numberOfCitations + \
                                int(citations[doi])
                            citationsList.append(int(citations[doi]))
            citationsList = sorted(citationsList, reverse=True)
            hIndex = 0
            for i, citation in enumerate(citationsList):
                if citation >= i + 1:  # CONTROLLO PER INCREMENTARE L'H-INDEX. i+1 PERCHE' i PARTE DA 0
                    hIndex = hIndex + 1
            crossData[candidate] = {'id': candidateId, 'name': name, 'level': candidateLevel, 'subject': candidates[candidate]['subject'], 'articles': articles,
                                    'citations': numberOfCitations, 'hindex': hIndex}
    crossData = completeCrossData(crossData, './data/REAL_DATA.csv')
    return crossData
