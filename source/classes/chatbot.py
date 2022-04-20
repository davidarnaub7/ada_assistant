
# CLASSES
from classes.assistants.meetingAssistant import MeetingAssistant
from classes.assistants.greetingAssistant import GreetingAssistant
from classes.assistants.taxiAssistant import TaxiAssistant

# CONSTANTS
import constants.constants as constants
from instances.nlp import nlp

# THIRD PARTY LIBRARY
from yaml import Loader, Dumper
from yaml import load, dump
import yaml

from helpers.pipeWriter import addRegister
# AUXILARY FUNCTIONS
from helpers.resolutor import getNaturalLanguageName


# CLASS DEFINITION
class ChatBot:
    global nlp
    def __init__(self):
        # CLASSES
        self.meetingAssitant = MeetingAssistant() # classe meeting
        self.greetingAssistant = GreetingAssistant() # clase greeting
        self.taxiAssistant = TaxiAssistant() # clase taxis booking

        # STATE VARIABLES
        self.intent:str = None  
        self.state: str = None

        #AUXILIAR VARIALES
        self.newStatement: str = None # Statement we want to safe in disambiguation part

        # DATA VARIABLES
        self.dictionary: dict = {}

        # LOADING THE DICTONARY WITH ASSOCIATED ACTIONS
        stream = open("./data/dict.yaml")
        loaded = load(stream, Loader=Loader)
        
        addRegister('loading Dataset....\n\n')
        
        for key, value in loaded.items():
            self.dictionary[key] = value 
       
        print('*********************** ADA ASSISTANT ***************************\n')
        
    ## GETTERS AND SETTERS
    def setNewIntent(self, newIntent: str):
        self.intent = newIntent
    
    def getIntent(self) -> str:
        return self.intent

    def setState(self, newState:str):
        self.state = newState

    def getState(self) -> str:
        return self.state
    
    def setNewStatement(self, nStatement: str):
        self.newStatement = nStatement
    
    def getNewStatement (self) -> str:
        return self.newStatement
    ########################################
    # 
    # CHATBOT LOGIC    
    #
    ########################################
    def goodbyeHandler (self): 
       pass 
    
    def greetingHandler(self, intent, statment):
        self.setNewIntent(None)
        return 'Hi! How can I help you today?'
        
    # ROUTING
    def getAssociatedMethod(self):
        methods = {
            # GREETING ASSISTANT
            constants.GREETING: self.greetingAssistant.processIntent,
            constants.SAY_GOODBYE: self.greetingAssistant.processIntent,
            # MEETING ASSISTANT
            constants.NEW_MEETING: self.meetingAssitant.processIntent,
            constants.LIST_MEETING: self.meetingAssitant.processIntent,
            # TAXI ASSISTANT
            constants.ASK_FOR_A_TAXI: self.taxiAssistant.processIntent,
            constants.LIST_TAXIS: self.taxiAssistant.processIntent,
        }

        return methods[self.getIntent()]

    # CALLER
    def callAssociatedMethod(self, statement: str) -> str:
        # GETTING THE ASSOCIATED METHOD TO THE CURRENT INTENT
        method = self.getAssociatedMethod()
        # CALLING AND RETURNING THIS ASSOCIATED METHOD WITH SOME PARAMS
        return method(self.getIntent(), statement, self.setNewIntent)

    # CHECK IF THE USER WANTS TO DO WHAT WE HAVE JUST PROPOSED OR IF WE WERE WRONG.
    def disambigautionHandler(self, statement: str) -> str:
        for ent in statement.ents:
            if ent.label_ == 'ASSERT':
                # ADDING THE NEWSTATEMENT TO THE DICTIONARY
                self.dictionary[self.getIntent()].append(self.getNewStatement())
                
                # REMOVING STATEMENT
                self.setNewStatement(None)
                
                #? add to data.yaml
                with open('./data/dict.yaml', 'w') as outfile:
                    yaml.dump(self.dictionary, outfile, default_flow_style=False)
                self.setState(constants.STATE_ASSIGNED)
                return self.callAssociatedMethod(nlp(statement))
            elif ent.label_ == 'NEGATION':
                # REMOVING STATEMENT
                self.setNewStatement(None)
                self.setState(None)
                return 'Sorry, I could not understand you. Can you rephrase your statement?'

    # IF WE ARE CHECKING A STATE MEANS THAT ARE IN A DISAMBIGUATION PROCESS.add()
    # OTHERWISE WE WANT TO PROCESS THE STATEMENT IN ORDER TO FIND A NEW INTENT
    # OR TO PASS THE RESPONSABILITY TO THE CURRENT FRAME.
    def processStatmentHandler (self, statement: str) -> str:
        if self.getState() == constants.CHECKING_STATE:
            return self.disambigautionHandler(nlp(statement))
     
        return self.processStatment(statement)
    
    # MAIN METHOD
    # CHECKS THE SIMILARITY OF ALL OUR DICTIONARY OF INTENTS WITH THE INTRODUCED STATEMENT.
    def processStatment(self, statement: str) -> str:
        basestatment = nlp(statement) # parsing the statment to spacy
        minSimiliraty = 0 # Auxilary variable to store a (maybe) provisional minSimilarity
        newIntent = None # Auxilary variable to store a (maybe) provisional intent
        hugeSimilarityFound = False # barrier to stop once we found a huge similarity

        # IF WE HAVEN'T STATE
        if self.getIntent() == None:
            addRegister('\nSearching a new intent...\n')
            addRegister('\nSIMILARITIES:\n')
        
        # ITERRATING ALL THE POSIBLES STATES WITH ALL POSIBLES EXAMPLES
        for key, value in self.dictionary.items():
            for sentence in value:
                nlpSentence = nlp(sentence)
                setenceSimilarity = basestatment.similarity(nlpSentence) 
                addRegister(sentence + ' \t  ' + str(setenceSimilarity) + '\n')

                # CHECKING IF THE NEW SIMILIRATY IS SO CLOSE TO 1    
                if setenceSimilarity >= constants.MIN_SIMILARITY:
                    hugeSimilarityFound = True
                
                # CHECKING IF THE NEW SIMILIRATY IS BIGGER THAN THE PREVIOUS SIMILIRATY    
                if setenceSimilarity > minSimiliraty:
                    newIntent = key
                    minSimiliraty = setenceSimilarity
                
                # IN CASE THE SIMILIRATY NEARS TO 1, MEANS THAT WE HAVE FOUND THE INTENT WE WANT
                # SO WE BREAK THE FOR
                if hugeSimilarityFound:
                    break

        """
        IMPORTANT INFORMATION

        1. If minSimiliraty < 0.6 and self.intent == None -> means that we have not current intent and futhermore, we haven't been able to indetify the new intent.
           So in that case we have to ask again
        
        2. if inSimiliraty > 0.6 (greater!) this means that we have found a new intent despite the fact we are in a current one. In that case, we have to 
            call a new method which will ask if they want to put off the current action by the new one.
        
        3. Otherwise, if we have a similarity lower than the MIN_SIMILARITY but greater than the THRESHOLD this means that we probably found a intent but we are not
            sure. So we start the disambiguation proccess.

        4. If nothing above happen means that we are in a current intent, and the given current information are related to some stuff of this intent. Consequently, we call
           to the frame that has to manage this intent.
        """
        if minSimiliraty < constants.THRESHOLD and self.getIntent() == None:
            return "Sorry I do not understand that. Please rephrase your statement."
        elif minSimiliraty > constants.MIN_SIMILARITY:
            self.setNewIntent(newIntent)
            addRegister('\n'+'*'*20+'\n')
            addRegister('NEW INTENT DETECTED: \t' + self.getIntent() + ' \n')
            addRegister('*'*20+'\n')
        elif minSimiliraty < constants.MIN_SIMILARITY and minSimiliraty > constants.THRESHOLD and self.getIntent() == None:
            self.setNewIntent(newIntent)
            self.setState(constants.CHECKING_STATE)
            self.setNewStatement(statement)
            addRegister('\n'+'*'*20+'\n')
            addRegister('NEW INTENT PROBABLY DETECTED: \t' + self.getIntent() + ' \n')
            addRegister('*'*20+'\n')
            return 'I am not pretty sure if you want to ' +  getNaturalLanguageName(newIntent)

        return self.callAssociatedMethod(basestatment) 

    