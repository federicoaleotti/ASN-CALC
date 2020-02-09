# ASN-CALC
Tool to calculate ASN indices and compare them with real data.

## DESCRIZIONE
### INPUT
I dati di partenza vengono forniti attraverso un file TSV che contiene le informazioni relative ai candidati. Il file è strutturato come segue:
1. id: id del candidato
2. subject: il settore di appartenenza del candidato tra i possibili settori bibliografici (es.: INFORMATICA)
3. session: la sessione in cui il candidato partecipa al concorso
4. level: il livello a cui il candidato vuole accedere (1 o 2)
5. dois: i doi associati alle produzioni dei candidati separati da ", "

Vengono inoltre usati i dati relativi alle citazioni presenti su COCI, quindi è necessario fornire in input il file CSV scaricabile [qui](http://opencitations.net/download#coci) contenente il dump.

Infine è necessario fornire un file CSV contenente i dati reali degli indici calcolati per i candidati. Attualmente il formato atteso è il seguente:
1. id: id del candidato
2. level: il livello a cui il candidato vuole accedere (1 o 2)
3. articles: il numero di articoli pubblicati su journal
4. citations: il numero di citazioni ricevute da tutte le produzioni del candidato
5. hindex: hindex del candidato

Tutto ciò che è statico (es.: la configurazione dei path, dei gap temporali, dei settori usati per filtrare, delle soglie etc.) viene gestito nel file configurations.py

### OUTPUT
Si ottiene in output un file CSV che contiene gli indici calcolati e gli indici reali 

### WORKFLOW
#### CREAZIONE DEL CSV DEI CANDIDATI
Per prima cosa viene elaborato il CSV dei candidati in modo da rimuovere eventuali ripetizioni ed ottenere informazioni utili ai calcoli successivi mediante le API Crossref.

Per ogni doi presente tra i dois dei candidati viene invocata l'API Crossref che restituisce tutte le informazioni presenti per quel doi, viene verificata la tipologia di pubblicazione (se è un articolo journal o meno) e vengono estratti gli autori e la data di pubblicazione.

A partire dai dati ottenuti viene costruito un CSV intermedio in cui sono riportati id, "name" del candidato(ottenuto guardando il numero di occorrenze dei nomi presenti tra gli autori), level, session, subject, journalDois e dois; ed un file CSV contenente le date di pubblicazione dei singoli articoli

#### CREAZIONE DEL CSV DELLE CITAZIONI
Partendo dal file di COCI e dal file CSV dei candidati prodotto al passo precedente viene generato un dizionario delle citazioni: per ogni riga del file COCI se l'articolo citato è presente tra i doi dei candidati viene inserito in un dizionario le cui chiavi sono i doi stessi (citati) ed i valori sono le citazioni ricevute (se il doi è già presente il valore viene incrementato). A partire dal dizionario delle citazioni viene generato un CSV intermedio in cui sono presenti doi e citations

#### INCROCIO DEI DATI E GENERAZIONE DEL FILE CSV DI OUTPUT
A partire dai dati precedentemente prodotti (candidati, citazioni, date di pubblicazione), vengono calcolati gli indici: per ogni candidato, se il suo settore è presente tra i SUBJECTS nel file di configurazione o se SUBJECTS == [], vengono calcolati:
- articles: somma dei journalDoi che rispettino i vincoli temporali dati da TIME_GAPS e SESSION_MAP (file configurazione)
- citations: somma delle citazioni ottenute da ogni doi (che rispetti i vincoli temporali) del candidato presenti sul CSV delle citazioni
- hindex: calcolato ordinando in maniera descrescente il numero delle citazioni ottenute dai doi validi ed iterando sulla lista. Quando l'iteratore è maggiore dell'i-esimo elemento il suo valore coincide con l'hindex.

Viene successivamente genereato un CSV contenente i dati del candidato (id, nome, livello e settore) e quelli appena calcolati accanto ai dati reali ricavati dal CSV dei dati reali in input.

Infine viene verificato se il candidato superi o meno i valori soglia riportati nel file di configurazione, se tutti e tre gli indici sono superiori alle soglie il candidato è valido, altrimenti no. Lo stesso viene fatto sui dati reali, in questo modo è possibile confrontare i due esiti.

## TO DO

- Ottenere i dati reali
- Ottenere un file TSV dei candidati strutturato come descritto sopra
- Implementare l'analisi dei risultati per settore
- Implementare la visualizzazione di grafici
