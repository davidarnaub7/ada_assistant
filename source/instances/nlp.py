from helpers.pipeWriter import addRegister
import spacy
# THIRD PARTY LIBRARIES
import os
import path_config




print(os.getcwd())
print('loading spacy...')
print(spacy.__version__)
os.chdir(path_config.source_path)
print(os.getcwd())
nlp = spacy.load('nlp/streetModel')

if path_config.executor =='antonio':
    import en_core_web_sm
    nlp = en_core_web_sm.load() 
else:
    nlp = spacy.load("en_core_web_md") # load the base pipeline
    
street_nlp = spacy.load("nlp/streetModel") # load the street pipeline
# give this component a copy of its own tok2vec
# street_nlp.replace_listeners("tok2vec", "ner", ["model.tok2vec"])

# now you can put the drug component before or after the other ner
# This will print a W113 warning but it's safe to ignore here
nlp.add_pipe(
    "ner",
    name="ner_street",
    source=street_nlp,
    after="ner",
)

doc = nlp("I have a meeting in la duana at 15:00, NO")
addRegister('Spacy loaded!...\n')