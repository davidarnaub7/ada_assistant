"""
    @file meetingAssistan.py
    @description This class manage whole meetings related actions.
"""

# PYHTON IMPORTS
import datetime

import pandas as pd

from helpers.pipeWriter import addRegister

# AUXILAR INSTANCES
import constants.constants as constants
import db.mongo as mongoClient
from instances.nlp import nlp

# PYTHON CLASSES
from helpers.DateHelper import DateHelper


# MONGO INSTANCE
mongo = mongoClient.mongo.meetings

# STATES
ASKING_FOR_HOUR = "HOUR"
ASKING_FOR_PLACE = "PLACER"
ASKING_FOR_DAY = "DAY"
JOB_DONE = "JOB_DONE"
CHANGING_PARAM= "CHANGING_PARAM"

class MeetingAssistant:
    def __init__(self):
        # AUX VARIABLES
        self.hour: str = None
        self.place: str = None
        self.date: str = None
        self.comment: str = None  # Additional comments to the meeting
        self.meetingLong: str = None

        # STATE VARIABLES
        self.state = None

        # DATA VARIABLES
        self.today: datetime = datetime.datetime.now()

        # HELPERS VARIABLES
        self.dateHelper = DateHelper()
        # i don't know if it a good idea to keep a meeting here or to instantiate a bbdd in the system with the meetings.
        self.meetings = []

        addRegister('Dataset loaded!\n')
        #! Here we have to load all the meetings stored into a yaml/csv/json file.

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

    def setMeetingLongo(self, newMeetingLong: str):
        self.meetingLong = newMeetingLong

    def getMeetingLong(self) -> str:
        return self.meetingLong

    #####################################
    #
    # FUNCTIONAL METHODS
    #
    #####################################
    def processIntent(self, intent, statement, setIntent):
        if intent == constants.NEW_MEETING:
            return self.newMeetingChecker(statement, setIntent)
        elif intent == constants.LIST_MEETING:
            return self.listMeeeting(statement, setIntent)

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
    def checkNewMeetingAndSave(self, setIntent):
        # CONVERTING DATE
        datetype = self.dateHelper.parse_text(self.getDate()  + ' at ' + self.getHour())
        dateStamp = datetime.datetime.fromisoformat(datetype[0]['value']['value'])
        newMeeting = {"date": dateStamp,  "place": self.getPlace()}

        # CHECKING IF MEETING EXITS. IN POSITIVE CASE WE RETURN AN STATMENT
        meetingExits = mongo.find_one({"date": {"$eq": dateStamp}})
        if meetingExits != None:
            return 'Ups. You have a meeting at this date! I cannot allow to you to work this way!';

        # OTHERWISE WE REGISTER THE METHOD
        try:
            mongo.insert_one(newMeeting)
            print('All rigth! You have new meeting in' + self.getDate() +  ' at ' +  self.getHour() + ' in ' + self.getPlace() + ' has been saved!')
            
            self.restartVariables()
            setIntent(None)
            return 'Do you want something else?'
        except:
            return "Oops! Something went wrong! I feel that it was my fault. Sorry!"


        #! FINALLY, IF NOT OTHER CONDITIONS:

    def newMeetingChecker(self, statement, setIntent):
        if self.getState() == None or self.getState() == ASKING_FOR_PLACE or self.getState() == ASKING_FOR_DAY or self.getState() == ASKING_FOR_HOUR:
            return self.newMeetingHandler(statement, setIntent)
        else:
            return self.updatingParam(statement,setIntent)

    def updateParamHandler(self, splitted):
        if splitted == ASKING_FOR_PLACE:
            self.setPlace(self.auxParam)
        elif splitted == ASKING_FOR_HOUR:
            self.setHour(self.auxParam)
        elif splitted == ASKING_FOR_DAY:
            self.setDate(self.auxParam)

    def updatingParam(self, statement, setIntent):
        # VARIABLE THAT WILL INDICATE IF WE HAVE TO CONTINUE OR NOT.
        mustCall = False

        for ent in statement.ents:
            if ent.label_ == 'ASSERT':
                print(ent)
                splitted = self.getState().split('-')[1]
                self.updateParamHandler(splitted)
                print(splitted + ' changed!')
                mustCall = True
            elif ent.label_ == 'NEGATION':
                print('Okey, not changed!')
                mustCall = True

        if mustCall:
            return self.newMeetingHandler(statement, setIntent)

    def newMeetingHandler(self, statement, setIntent):
        addRegister("\nENTITIES: \n")
        [addRegister((ent.text + ' ' + ent.label_)) for ent in statement.ents]
        addRegister('\n')

        for ent in statement.ents:
            if ent.label_ == 'DATE':
                if self.getDate() != None:
                    self.auxParam = ent.text
                    self.setState(CHANGING_PARAM + '-' + ASKING_FOR_DAY)
                    return 'You already has a date for this meeting. Do you want to change it for this one?'
                elif self.getState() != ASKING_FOR_DAY and self.getState():
                    print('Okey, I saved the date you passed me as the date of the meeting')
                    print('However, I was asking for: ' + self.getState())
                self.setDate(ent.text)
            elif ent.label_ == 'TIME':
                if self.getHour() != None:
                    self.auxParam = ent.text
                    self.setState(CHANGING_PARAM + '-' + ASKING_FOR_HOUR)
                    return 'You already has a hour assigned to this meeting. Do you want to change it for this one?'
                elif self.getState() != ASKING_FOR_HOUR and self.getState():
                    print('Okey, I saved the time you passed me as the time of the meeting')
                    print('However, I was asking for: ' + self.getState())
                self.setHour(ent.text)
            elif ent.label_ == 'STREET':
                if self.getPlace() != None:
                    self.auxParam = ent.text
                    self.setState(CHANGING_PARAM + '-' + ASKING_FOR_PLACE)
                    return 'You already has a street assigned to this meeting. Do you want to change it for this one?'
                elif self.getState() != ASKING_FOR_PLACE and self.getState():
                    print('Okey, I saved the street you passed me as the place of the meeting')
                    print('However, I was asking for: ' + self.getState())
                self.setPlace(ent.text)

        addRegister('\n*****************************************\n')
        addRegister('NEW MEETING CONFIG\n')
        addRegister('Hour\t' + str(self.getHour()) +'\n')
        addRegister('Date\t' + str(self.getDate()) +'\n' )
        addRegister('Place\t' + str(self.getPlace()) +'\n')
        addRegister('*****************************************\n')

        if self.getHour() == None:
            self.setState(ASKING_FOR_HOUR)
            return 'What time will it be?'
        
        if self.getDate() == None:
            self.setState(ASKING_FOR_DAY)
            return 'When this meeting will take place?'
        
        if self.getPlace() == None:
            self.setState(ASKING_FOR_PLACE)
            return 'Where will it be?'

        # CHECKING WHETHER OR NOT WE CAN SAVE THE MEETING
        return self.checkNewMeetingAndSave(setIntent)
    
    ######################################
    # 
    # LIST MEETING
    #
    ######################################
    def prettifyMeetings(self, meeting):
        date: datetime = meeting['date']
        return 'At ' + str(date.time().hour+1) + ' in ' + meeting['place']

    def listMeeeting (self, statement, setIntent):

        # Looking the dates he wants to list.
        for ent in statement.ents:
            if ent.label_ == 'DATE':
                self.setDate(ent.text)
        
        if self.getDate() == None:
            self.setState(ASKING_FOR_DAY)
            return 'Which day do you want to know?'
        else:
            addRegister('\n'+'*'*10 + ' Looking for meetings...' + '*'*10 +'\n')
             # CONVERTING DATE
            datetype = self.dateHelper.parse_text(self.getDate())

            # CHECKING LIST NOT EMPTY
            if datetype == []:
                return "Oops! Something went wrong! I feel that it was my fault. Sorry!"   

            dateStamp = datetime.datetime.fromisoformat(datetype[0]['value']['value'])

            # CONVERTING THE CURRENT DATE TO A TIMESTAMP:  
            # Compare somehow the date in mongodb. 
            meetings = mongo.find({"date": {"$gte": dateStamp}})
        
            # Returing prettified meetings
            prettyMeetings = [self.prettifyMeetings(meeting) for meeting in meetings]

            # CUSTOMIZING RESPONSE DEPEDING THE AMOUNT OF MEETINGS
            if prettyMeetings == []:
                print ('You have not meeting programmed for ' +  self.getDate())
            elif len(prettyMeetings) == 1:
                print('You only have one meeting for ' + self.getDate())
            else:
                print('These are the meeting for ' + self.getDate())
            
                
            #Restating variables
            self.restartVariables()

            # PRINTING THE MEETINGS
            for i in range(len(prettyMeetings)):
                print (str(i+1) + ' - ' + prettyMeetings[i])

            setIntent(None)
            return 'Something else?'