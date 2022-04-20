import spacy
import random
from spacy.util import minibatch, compounding
from spacy.training.example import Example

from trainDataCreator import TRAIN_DATA, ASSERTION_DATA;

nlp=spacy.load('en_core_web_md')
ner=nlp.get_pipe("ner")

print(nlp.pipe_names)

for _, annotations in TRAIN_DATA:
  for ent in annotations.get("entities"):
    print('ADDING ENTITY: ')
    print(ent[0])
    ner.add_label(ent[2])


print(len(TRAIN_DATA))

for iteration in range(2):
    # shuufling examples  before every iteration
    random.shuffle(TRAIN_DATA)
    random.shuffle(ASSERTION_DATA)
    losses = {}
    # batch up the examples using spaCy's minibatch
    batches = minibatch(TRAIN_DATA[1:150] + ASSERTION_DATA, size=compounding(4.0, 32.0, 1.001))
    for batch in batches:
        for text, annotations in batch:
            # create Example
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            # Update the model
            nlp.update([example], losses=losses, drop=0.3)
            print("Losses", losses)

doc = nlp("I have a meeting in Duana, no")
print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
doc = nlp("Yes, I want")
print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
doc = nlp("Yes")
print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
doc = nlp("No, I don't want")
print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
doc = nlp("No")
print("Entities", [(ent.text, ent.label_) for ent in doc.ents])

print(ner.labels)
# nlp.select_pipes(enable=disbale_pipes)
print(nlp.pipe_names)
nlp.to_disk('../nlp/streetModel')