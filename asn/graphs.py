import asn
import pandas as pd
import matplotlib.pyplot as plt


def sampleGraph():
    data = pd.read_csv('./data/CROSS_DATA.csv')
    citations = data["citations"]
    hindex = data["hindex"]
    plt.scatter(citations, hindex)
    plt.savefig("./data/images/CITATIONS_HINDEX.png")
    plt.show()



def validHistogram(validCalc, validReal):
    d = {0: validCalc, 1: validReal}
    df = pd.DataFrame(data=d)
    df.hist(column='Numero di candidati che rispettano i requisiti')
    
