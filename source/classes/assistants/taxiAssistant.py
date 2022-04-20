"""
    @file meetingAssistan.py
    @description This class manage whole meetings related actions.
"""

# PYHTON IMPORTS
import datetime

import pandas as pd

# AUXILAR INSTANCES
import constants.constants as constants
import db.mongo as mongoClient
from instances.nlp import nlp

# PYTHON CLASSES
from helpers.DateHelper import DateHelper
from helpers.pipeWriter import addRegister


# MONGO INSTANCE
mongo = mongoClient.mongo.taxis

# STATES
ASKING_FOR_HOUR = "HOUR"
ASKING_FOR_PLACE = "PLACER"
ASKING_FOR_DAY = "DAY"
JOB_DONE = "JOB_DONE"
CHANGING_PARAM= "CHANGING_PARAM"

class TaxiAssistant:
    def __init__(self):
        # SLOTS VARIABLES
        self.hour: str = None
        self.place: str = None
        self.date: str = None
        
        # STATE VARIABLES
        self.state = None

        # DATA VARIABLES
        self.today: datetime = datetime.datetime.now()

        # HELPERS VARIABLES
        self.dateHelper = DateHelper()
      

    #####################################
    #
    # SETTERS AND GETTERS
    #
    #####################################
    def setHour(self, newHour: str):
        self.hour = newHour

    def getHour(self) -> str:
        return self.hour

    def setPlace(self, newPlace: str):
        self.place = newPlace

    def getPlace(self) -> str:
        return self.place

    def setDate(self, newDate: str):
        self.date = newDate

    def getDate(self) -> str:
        return self.date

    def setState(self, newState: str):
        self.state = newState

    def getState(self) -> str:
        return self.state

    #####################################
    #
    # FUNCTIONAL METHODS
    #
    #####################################
    def processIntent(self, intent, statement, setIntent):
        if intent == constants.ASK_FOR_A_TAXI:
            return self.newTaxiChecker(statement)
        elif intent == constants.LIST_TAXIS:
            return self.listTaxis(statement, setIntent)

    # RESET ALL THE VARIABLES IN THE SLOT
    def restartVariables(self):
        self.setDate(None)
        self.setPlace(None)
        self.setHour(None)

    """
        @func checkNewMeetingAndSave

        @description Check if the new meeting can be added. In positive case, then check if the user wants to book a
        taxi or a restaurant. In negative case it throw an error message.

        @return String
    """
    def checkNewMeetingAndSave(self):
        # CONVERTING DATE
        datetype = self.dateHelper.parse_text(self.getDate()  + ' at ' + self.getHour())
        dateStamp = datetime.datetime.fromisoformat(datetype[0]['value']['value'])
        newTaxi = {"date": dateStamp,  "place": self.getPlace()}

        # CHECKING IF MEETING EXITS. IN POSITIVE CASE WE RETURN AN STATMENT
        taxisExists = mongo.find_one({"date": {"$eq": dateStamp}})
        
        # IF taxisExists != None MEANS THAT SOME TAXI BOOKING ALREADY EXISTS
        if taxisExists != None:
            return 'Ups. You have a taxi at this date! I cannot allow to taxi drives to work this way!';

        # OTHERWISE WE REGISTER THE METHOD
        try:
            # INSERTING THE NEW REGISTER IN MONGO
            mongo.insert_one(newTaxi)
            print('All rigth! You have new taxi booked in ' + self.getDate() +  ' at ' +  self.getHour() + ' in ' + self.getPlace() + ' has been saved!')
            
            # CLEANING THE SLOT
            self.restartVariables()

            return 'Do you want something else?'
        except:
            return "Oops! Something went wrong! I feel that it was my fault. Sorry!"

    # CHECKS IN WHICH STATE THE FRAME IS
    def newTaxiChecker(self, statement):
        if self.getState() == None or self.getState() == ASKING_FOR_PLACE or self.getState() == ASKING_FOR_DAY or self.getState() == ASKING_FOR_HOUR:
            return self.newTaxiHandler(statement)
        else:
            return self.updatingParam(statement)

    # CALL TO THE METHOD THAT WILL UPDATE THE CURRENT PARAM
    def updateParamHandler(self, splitted):
        if splitted == ASKING_FOR_PLACE:
            self.setPlace(self.auxParam)
        elif splitted == ASKING_FOR_HOUR:
            self.setHour(self.auxParam)
        elif splitted == ASKING_FOR_DAY:
            self.setDate(self.auxParam)

    # CHECKING WHETHER THE USER WANTS TO UPDATE THE PARAM OF NOT
    def updatingParam(self, statement):
        # VARIABLE THAT WILL INDICATE IF WE HAVE TO CONTINUE OR NOT.
        mustCall = False

        # LOOKING FOR ENTITIES WHICH CORRESPONDS TO AN ASSERT (THE USER WANTS TO UPDATE THE PARAM)
        # OR TO A NEGATION (THE USER DOESN'T WANT TO UPDATE THE PARAM)
        for ent in statement.ents:
            if ent.label_ == 'ASSERT':
                addRegister(ent+'\n')
                splitted = self.getState().split('-')[1]
                self.updateParamHandler(splitted)
                addRegister(splitted + ' changed!\n')
                mustCall = True
            elif ent.label_ == 'NEGATION':
                addRegister('Okey, not changed!\n')
                mustCall = True

        if mustCall:
            return self.newTaxiHandler(statement)

    # CHECKING ENTITIES TO FILL THE SLOT NEEDED TO BOOK A TAXI.
    def newTaxiHandler(self, statement):
        # WILL PIPE THIS REGISTER
        addRegister("ENTITIES:")
        [addRegister((ent.text + ' ' + ent.label_)) for ent in statement.ents]
        addRegister('\n')
        
        # ITERRATING OVER ALL ENTITIES OF THE SENTENCE
        for ent in statement.ents:

            if ent.label_ == 'DATE':
                # IF WE ALREADY HAVE A DATE THIS MEANS THAT THE USER WANTS TO UPDATE IT
                if self.getDate() != None:
                    # KEEPING THE PARAM
                    self.auxParam = ent.text
                    # UPDATING THE STATE OF THE SYSTEM TO CHANGING_PARAM
                    self.setState(CHANGING_PARAM + '-' + ASKING_FOR_DAY)
                    return 'You already has a date for this taxi. Do you want to change it for this one?'
                # ELSE IF THE USER INTRODUCE THE DATE BUT THE SYSTEM IS NOT ASKING FOR THE DATE 
                # THE SYSTEM WILL KEEP THE PARAM AND SHOW THE FOLLOWING MESSAGE. 
                elif self.getState() != ASKING_FOR_DAY and self.getState():
                    print(
                        'Okey, I saved the date you passed me as the date for the taxi')
                    print('However, I was asking for: ' + self.getState())
                self.setDate(ent.text)
            elif ent.label_ == 'TIME':
                if self.getHour() != None:
                    self.auxParam = ent.text
                    self.setState(CHANGING_PARAM + '-' + ASKING_FOR_HOUR)
                    return 'You already has a hour assigned to this taxi booking. Do you want to change it for this one?'
                elif self.getState() != ASKING_FOR_HOUR and self.getState():
                    print('Okey, I saved the time you passed me as the time of the taxi')
                    print('However, I was asking for: ' + self.getState())
                self.setHour(ent.text)
            elif ent.label_ == 'STREET':
                if self.getPlace() != None:
                    self.auxParam = ent.text
                    self.setState(CHANGING_PARAM + '-' + ASKING_FOR_PLACE)
                    return 'You already has a street assigned to this taxi booking. Do you want to change it for this one?'
                elif self.getState() != ASKING_FOR_PLACE and self.getState():
                    print('Okey, I saved the street you passed me as the place of the taxi booking')
                    print('However, I was asking for: ' + self.getState())
                self.setPlace(ent.text)

        addRegister('\n'+'*'*10+'\n')
        addRegister('NEW MEETING CONFIG\n')
        addRegister('Hour\t' + str(self.getHour()) +'\n')
        addRegister('Date\t' + str(self.getDate()) +'\n' )
        addRegister('Place\t' + str(self.getPlace()) +'\n')
        addRegister('*'*10+'\n')

        if self.getHour() == None:
            self.setState(ASKING_FOR_HOUR)
            return 'Great!. What time do you want the taxi comes?'
        
        if self.getDate() == None:
            self.setState(ASKING_FOR_DAY)
            return 'Okey!. When do you want the taxi?'
        
        if self.getPlace() == None:
            self.setState(ASKING_FOR_PLACE)
            return 'Right!. Where will you be?'

        # CHECKING WHETHER OR NOT WE CAN SAVE THE MEETING
        return self.checkNewMeetingAndSave()
    
    ######################################
    # 
    # LIST MEETING
    #
    ######################################

    # THIS MAKES THE OUTPUT UNDESTANDABLE TO THE USER.
    def prettifyTaxi(self, taxi):
        date: datetime = taxi['date']
        return 'At ' + str(date.time().hour+1) + ' in ' + taxi['place']

    # THIS METHODS HANLDES THE LISTING OF THE TAXI BOOKINGS.
    def listTaxis (self, statement, setIntent):
        # Looking the dates he wants to list.
        for ent in statement.ents:
            if ent.label_ == 'DATE':
                self.setDate(ent.text)
        
        if self.getDate() == None:
            self.setState(ASKING_FOR_DAY)
            return 'Which day do you want to know?'
        else:
            addRegister('*'*10 + ' Looking for meetings...' + '*'*10+'\n')
             # CONVERTING DATE
            datetype = self.dateHelper.parse_text(self.getDate())

            # CHECKING LIST NOT EMPTY
            if datetype == []:
                return "Oops! Something went wrong! I feel that it was my fault. Sorry!"   

            # PARSING THE DATE TO SOME FORMAT UNDERSTOOD BY MONGODB.
            dateStamp = datetime.datetime.fromisoformat(datetype[0]['value']['value'])

            # CONVERTING THE CURRENT DATE TO A TIMESTAMP:  
            # Compare somehow the date in mongodb. 
            taxis = mongo.find({"date": {"$gte": dateStamp}})
        
            # Returing prettified meetings
            prettyTaxis = [self.prettifyTaxi(taxi) for taxi in taxis]

            # CUSTOMIZING RESPONSE DEPEDING THE AMOUNT OF MEETINGS
            if prettyTaxis == []:
                print ('You have not taxis programmed for ' +  self.getDate())
            elif len(prettyTaxis) == 1:
                print('You only have one taxi for ' + self.getDate())
            else:
                print('These are the taxis for ' + self.getDate())
            
                
            # CLEANING THE SLOTS.
            self.restartVariables()

            # PRINTING ALL THE MEETINGS
            for i in range(len(prettyTaxis)):
                print (str(i+1) + ' - ' + prettyTaxis[i])

            setIntent(None)
            return 'Something else?'