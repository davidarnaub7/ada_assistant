
from constants import constants


def getNaturalLanguageName(label:str) -> str:
    if label == constants.NEW_MEETING:
        return ' create a new meeting?'
    elif label == constants.LIST_MEETING:
        return ' list meetings?'
    elif label == constants.LIST_TAXIS:
        return ' list taxis bookings?'
    elif label == constants.ASK_FOR_A_TAXI:
        return ' book a taxi?'
    elif label == constants.GREETING:
        return ' greet?'