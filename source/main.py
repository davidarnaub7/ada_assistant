


# EXTERNAL FILES
from classes.chatbot import ChatBot

import constants.constants as constants
import fn_config
import pyttsx3
import speech_recognition as sr

if __name__ == '__main__':
    if fn_config.tts_enable:
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.runAndWait()
    
    if fn_config.asr_enable:  
        r = sr.Recognizer()

    chatbot = ChatBot()
    
    print('ME: ')            
    if fn_config.asr_enable:  

        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)

        # with open("microphone-results.wav", "wb") as f:
            # f.write(audio.get_wav_data())

        # with sr.WavFile("microphone-results.wav") as source:
            # audio = r.record(source)

        text = r.recognize_google(audio)
        # text = r.recognize_sphinx(audio) #requires: brew install swig; pip install pocketsphinx
        print(text)
        statement = text
    else:
         statment = input()

    while chatbot.getState() != constants.SAY_GOODBYE:

        if fn_config.tts_enable:
            engine.say(chatbot.processStatment(statment.lower()))
            engine.runAndWait()

        print('ADA: ')

        print(chatbot.processStatment(statment.lower()))
        print('ME: ')
        if fn_config.asr_enable:  
            
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)

            text = r.recognize_google(audio)
            print(text)
            statement = text
        else:
            statment = input()

