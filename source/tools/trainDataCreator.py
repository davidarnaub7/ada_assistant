

import csv

TRAIN_DATA = []
ASSERTION_DATA = []

assertions = ['Yes', 'Yep', 'Yeah', 'Yeap']
negations = ['No', 'Nop', 'Noup', 'Nah']

labels = [" , I would like", '' , ' , I want to']

for assertion in assertions:
    for label in labels:
        ASSERTION_DATA.append((assertion + label, {"entities": [(0, len(assertion), 'ASSERT')]}))
        ASSERTION_DATA.append((assertion, {"entities": [(0, len(assertion), 'ASSERT')]}))
        ASSERTION_DATA.append((assertion.lower() + label, {"entities": [(0, len(assertion), 'ASSERT')]}))
        ASSERTION_DATA.append((assertion.lower(), {"entities": [(0, len(assertion), 'ASSERT')]}))

labels = [" , I do not", " , I do not", ', I would not', '']

for negation in negations:
    for label in labels:
        ASSERTION_DATA.append((negation + label, {"entities": [(0, len(negation), 'NEGATION')]}))
        ASSERTION_DATA.append((negation, {"entities": [(0, len(negation), 'NEGATION')]}))
        ASSERTION_DATA.append((negation.lower() + label, {"entities": [(0, len(negation), 'NEGATION')]}))
        ASSERTION_DATA.append((negation.lower(), {"entities": [(0, len(negation), 'NEGATION')]}))


print(ASSERTION_DATA)

with open('../data/carrers.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    next(reader, None) 
    LABEL = 'STREET';
    for row in reader:
        streets = list(row)
        formal = streets[3].replace('"', '')
        informal = streets[4].replace('"', '')

        PHRASES = ['I have a meeting in ', 'Will be in ']

        for hardcode in PHRASES:
            TRAIN_DATA.append((hardcode + formal, {"entities": [(len(hardcode), len(hardcode)+len(formal), LABEL)]}))
            TRAIN_DATA.append((hardcode + formal, {"entities": [(len(hardcode), len(hardcode)+len(formal.lower()), LABEL)]}))
            TRAIN_DATA.append((hardcode + informal, {"entities": [(len(hardcode), len(hardcode)+len(informal), LABEL)]}))
            TRAIN_DATA.append((hardcode + informal, {"entities": [(len(hardcode), len(hardcode)+len(informal.lower()), LABEL)]}))