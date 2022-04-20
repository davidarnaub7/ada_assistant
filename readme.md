
# ChatBot
This chatbot (called ADA) attends to a meeting assistant or secretary. The system manages the meetings you have over time. It identifies collisions and nearby meetings. It also gives the possibility to book a cab to go from one meeting to another or to make a reservation at a restaurant if the meeting ends at lunchtime. In the same way, the system recognizes and responds by text or voice commands. 

# Tech Stack

1. Python
2. Spacy
3. MongoDB

# How to run the system

# Requeriments 
You must create an account in MongoAtlas and add the endpoint url in *./db/mongo.py*. The url is provided by MongoAtlas. However, it has to be something like this

**mongodb+srv://username:passwd@cluster0.number.mongodb.net/myFirstDatabase?retryWrites=true&w=majority;**

As you see, you must put your username and password and the cluster and collection you'd like to store the information.

## Libraries
There are some libraries you must install in order to run the system:
1. pyyaml
2. pendulum
3. pyduckling-native
4. pymongo
5. spacy

You must run the system with python3.7 otherwise exists some conflicts that prevent us from running it.

## Execution
The main program is in main.py in the root directory.

```
python3 o python main.py
```

# How to create a pipe
In the root of the project do the following commands:
```
mkfifo pipe1
```
Now if you want to see the registers open another terminal tab and write:
```
tail -f pipe1
```
Finally, if you want to remove the pipe just do the following command:
```
rm pipe1
```

# Additional Notes
The system can be trained to recognize labels that best suit your situation (Name Entity Recognition Training). For example, the streets of the city where you live or the terms you use in your job.

To train the system you must go to **helpers/trainDataCreator.py**. Once there, you must change the *../data/carrers.csv* for the file you want to process (this file must contains the labels and must follow the format of carrers.csv). Then, you must change the *PHRASES* variables by the phrases 
that will preeced to the labels you want to process. Finally, you must change the variable LABEL by the entity name you want to give to those labels. In that case, we are adding the streets of Barcelona, so we use the label STREET and we are using as PHRASES *'I have a meeting in ', 'Will be in '*.

```python
with open('../data/carrers.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    next(reader, None) 
    PHRASES = ['I have a meeting in ', 'Will be in ']
    LABEL = 'STREET';
    for row in reader:
        streets = list(row)
        formal = streets[3].replace('"', '')
        informal = streets[4].replace('"', '')

        for hardcode in PHRASES:
            TRAIN_DATA.append((hardcode + formal, {"entities": [(len(hardcode), len(hardcode)+len(formal), LABEL)]}))
            TRAIN_DATA.append((hardcode + formal, {"entities": [(len(hardcode), len(hardcode)+len(formal.lower()), LABEL)]}))
            TRAIN_DATA.append((hardcode + informal, {"entities": [(len(hardcode), len(hardcode)+len(informal), LABEL)]}))
            TRAIN_DATA.append((hardcode + informal, {"entities": [(len(hardcode), len(hardcode)+len(informal.lower()), LABEL)]}))
```