"""
    @file greetingAssitant.py
    @description This class manage whole greetings related actions.
"""

import random
import constants.constants as constants

class GreetingAssistant:
    def __init__(self):
        # MOCK VARIABLES
        self.greetings: str = ['Hi David, How can I help you today?', '¡Hey David! Nice to see you again. Tell me', 'Hi David, tell me what to do']
        self.bye: str = ['Bye David', "Bye! I'll be just here.", 'Have fun!', 'Have a nice day David!']

    #####################################
    #
    # FUNCTIONAL METHODS
    #
    #####################################
    def processIntent(self, intent, statement, setIntent):
        if intent == constants.GREETING:
            return self.greetUser(statement, setIntent)
        if intent == constants.SAY_GOODBYE:
            return self.sayGoodBye(statement)
    
    # SELECTS A GREET RANDOMLY AND RETURN IT.
    def greetUser(self, statement, setIntent):
        index = random.randint(0, len(self.greetings)-1)
        setIntent(None)
        return self.greetings[index]

    # SELECTS A GOODBYE RANDOMLY AND RETURN IT.
    def sayGoodBye(self,statment):
        index = random.randint(0, len(self.greetings)-1)
        return self.bye[index]
