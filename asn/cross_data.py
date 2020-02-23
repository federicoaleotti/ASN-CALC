import csv
import asn
import configurations

SUBJECTS = configurations.SUBJECTS
TIME_GAPS = configurations.TIME_GAPS
SESSIONS_MAP = configurations.SESSIONS_MAP


# VERIFICA SUGLI INDICI E LE SOGLIE
def validateCandidate(level, subject, articles, citations, hindex, thresholdArticles, thresholdCitations, thresholdHindex):
    articlesF = False
    citationsF = False
    hindexF = False
    if articles >= thresholdArticles:
        articlesF = True
    if citations >= thresholdCitations:
        citationsF = True
    if hindex >= thresholdHindex:
        hindexF = True
    return articlesF, citationsF, hindexF


# CONFRONTO TRA DATI CALCOLATI E DATI REALI CONSIDERANDO IL SETTORE
def matchData(crossData, subject):
    results = {
        1: {
            'candidates': 0,
            'articles': 0,
            'citations': 0,
            'hindex': 0,
            'passing': 0,
            'matching': 0
        },
        2: {
            'candidates': 0,
            'articles': 0,
            'citations': 0,
            'hindex': 0,
            'passing': 0,
            'matching': 0
        }
    }
    for elem in crossData:
        calc = False
        real = False
        if subject == "" or crossData[elem]['subject'] == subject:
            articles, citations, hindex = validateCandidate(int(crossData[elem]['level']), crossData[elem]['subject'],
                                                            int(crossData[elem]['articles']), int(crossData[elem]['citations']), int(crossData[elem]['hindex']), int(crossData[elem]['threshold_articles']), int(crossData[elem]['threshold_citations']), int(crossData[elem]['threshold_hindex']))
            if (articles and citations) or (articles and hindex) or (citations and hindex):
                calc = True
                results[int(crossData[elem]['level'])]['passing'] = results[int(
                    crossData[elem]['level'])]['passing'] + 1
            real_articles, real_citations, real_hindex = validateCandidate(int(crossData[elem]['level']), crossData[elem]['subject'],
                                                                           int(crossData[elem]['real_articles']), int(crossData[elem]['real_citations']), int(crossData[elem]['real_hindex']), int(crossData[elem]['threshold_articles']), int(crossData[elem]['threshold_citations']), int(crossData[elem]['threshold_hindex']))
            if (real_articles and real_citations) or (real_articles and real_hindex) or (real_citations and real_hindex):
                real = True
            if calc == real:
                results[int(crossData[elem]['level'])]['matching'] = results[int(
                    crossData[elem]['level'])]['matching'] + 1
            if articles == real_articles:
                results[int(crossData[elem]['level'])]['articles'] = results[int(
                    crossData[elem]['level'])]['articles'] + 1
            if citations == real_citations:
                results[int(crossData[elem]['level'])]['citations'] = results[int(
                    crossData[elem]['level'])]['citations'] + 1
            if hindex == real_hindex:
                results[int(crossData[elem]['level'])]['hindex'] = results[int(
                    crossData[elem]['level'])]['hindex'] + 1
            results[int(crossData[elem]['level'])]['candidates'] = results[int(
                crossData[elem]['level'])]['candidates'] + 1
    return results


# ANALISI DEI RISULTATI OTTENUTI
# TIPO 1 DIVERSIFICATA TIPO - 2 UNICA
def analizeResults(crossDataCSV):
    crossData = asn.createDict(crossDataCSV)
    results = {}
    if len(SUBJECTS) > 0:
        results = {}
        for subject in SUBJECTS:
            result = matchData(crossData, subject)
            results[subject] = result
    else:
        crossDataSubjects = asn.getAllSubjects(crossDataCSV)
        results = {}
        for subject in crossDataSubjects:
            result = matchData(crossData, subject)
            results[subject] = result
    return results


# INCROCIO DEI DATI CONTENUTI NEL CSV DEI CANDIDATI, NEL CSV DELLE CITAZIONI E NEL CSV DEI SETTORI
# VENGONO CONTATI GLI ARTICOLI, IL NUMERO TOTALE DELLE CITAZIONI E VIENE CALCOLATO L'H-INDEX
# L'H-INDEX VIENE CALCOLATO COSTRUENDO UNA LISTA ORDINATA IN ORDINE DECRESCENTE DEL NUMERO DI CITAZIONI RICEVUTE DA CIASCUN DOI
# SUCCESSIVAMENTE SI ITERA SULLA LISTA FINO A QUANDO L'N-ESIMO NON HA UN VALORE MINORE DELL'ITERATORE + 1
# IL VALORE DELL'H-INDEX CORRISPONDE AL VALORE DELL'ITERATORE
def crossData(candidates, citations, publicationDates):
    crossData = {}
    for candidate in candidates:
        numberOfCitations = 0
        articles = 0
        citationsList = []  # UTILE PER IL CALCOLO DELL'H-INDEX
        candidateId = candidates[candidate]['id']
        candidateLevel = int(candidates[candidate]['level'])
        journalDois = candidates[candidate]['journal_dois'].split(', ')
        dois = candidates[candidate]['dois'].split(', ')
        name = candidates[candidate]['name']
        sessionDate = SESSIONS_MAP[int(candidates[candidate]['session'])]
        for doi in journalDois:
            timeGap = TIME_GAPS['publications'][candidateLevel]
            if doi in publicationDates:  # VERIFICO CHE SIA UN DOI TEMPORALMENTE VALIDO
                if (sessionDate - int(publicationDates[doi])) < timeGap and (sessionDate - int(publicationDates[doi])) >= 0:
                    articles = articles + 1
        for doi in dois:
            timeGap = TIME_GAPS['citations'][candidateLevel]
            if doi in publicationDates:  # VERIFICO CHE SIA UN DOI TEMPORALMENTE VALIDO
                if (sessionDate - int(publicationDates[doi])) < timeGap and (sessionDate - int(publicationDates[doi])) >= 0:
                    if doi in citations:
                        numberOfCitations = numberOfCitations + \
                            int(citations[doi])
                        citationsList.append(int(citations[doi]))
        citationsList = sorted(citationsList, reverse=True)
        hIndex = 0
        for i, citation in enumerate(citationsList):
            if citation >= i + 1:  # CONTROLLO PER INCREMENTARE L'H-INDEX. i+1 PERCHE' i PARTE DA 0
                hIndex = hIndex + 1
        crossData[candidate] = {'name': name, 'session': candidates[candidate]['session'], 'level': candidateLevel, 'subject': candidates[candidate]['subject'], 'id': candidateId, 'articles': articles, 'citations': numberOfCitations, 'hindex': hIndex, 'real_articles': candidates[candidate]['real_articles'],
                                'real_citations': candidates[candidate]['real_citations'], 'real_hindex': candidates[candidate]['real_hindex'], 'threshold_articles': candidates[candidate]['threshold_articles'], 'threshold_citations': candidates[candidate]['threshold_citations'], 'threshold_hindex': candidates[candidate]['threshold_hindex']}
    return crossData
