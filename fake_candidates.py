import random
import csv
import asn
import string


def randomString(stringLength=12):
    letters = list(map(chr, range(97, 123)))
    val = ""
    for _ in range(stringLength):
        val = val + random.choice(letters)
    return val


candidates = {}
candidateIndex = 0
with open('./data/CANDIDATES_OUT.csv') as document:
    reader = csv.reader(document, delimiter=",")
    next(reader)
    count = 0
    for row in reader:
        count = count + 1
        candidateId = randomString()
        # subject = random.choice(['INFORMATICA', 'GEOMETRIA E ALGEBRA',
        #                          'RICERCA OPERATIVA', 'CHIMICA INDUSTRIALE', 'ELETTRONICA'])
        candidates[candidateIndex] = {"id": candidateId, "name": row[0], "level": row[1], "session": row[2],
                                      "subject": 'INFORMATICA', "journalDois": row[3], "dois": row[4]}
        candidateIndex = candidateIndex + 1
asn.createCSV(candidates, './data/FAKE_CANDIDATES_OUT.csv',
              ["id", "name", "level", "session", "subject", "journalDois", "dois"], 0)
