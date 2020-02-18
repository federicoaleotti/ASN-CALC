CANDIDATES_IN = './data/CANDIDATES_REDUCED.tsv'
CANDIDATES_OUT = './data/CANDIDATES_OUT.csv'
COCI_DATA = './data/COCI_DATA.csv'
CITATIONS_OUT = './data/CITATIONS_OUT.csv'
CROSS_DATA = './data/CROSS_DATA.csv'
REAL_DATA = './data/REAL_DATA.csv'
PUBLICATION_DATES = './data/PUBLICATION_DATES.csv'
TIME_GAPS = {
    "publications": {
        1: 10,
        2: 5
    },
    "citations": {
        1: 15,
        2: 10
    },
    "hindex": {
        1: 15,
        2: 10
    }
}
SESSIONS_MAP = {
    1: 2016,
    2: 2017,
    3: 2017,
    4: 2017,
    5: 2018,
    6: {
        1: '2016-12-02',
        2: '2017-04-03',
        3: '2017-08-04',
        4: '2017-12-05',
        5: '2018-04-06'
    }
}
SUBJECTS = ["01-B1"] 
THRESHOLDS = {
    "INFORMATICA": {
        1: {
            "articles": 9,
            "citations": 304,
            "hindex": 10
        },
        2: {
            "articles": 4,
            "citations": 157,
            "hindex": 7
        }
    }
}
