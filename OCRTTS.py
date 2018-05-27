import pyttsx3
from pytesseract import *


def ocr(img, lang='kor'):
    #recognizes a given letter image
    #returns the recognized letters
    print('Letter Recognizing Started.')
    text = image_to_string(img, lang=lang)
    return text


def tts(text, ADD_VOLUME=0, RATE=150):
    #transform a given text into speech
    #outputs the voice signal through a connected audio device
    print('Speech Synthesis Started.')
    engine = pyttsx3.init()
    volume = engine.getProperty('volume')

    engine.setProperty('volume', volume + ADD_VOLUME) #set volume
    engine.setProperty('rate', RATE) #set voice rate(speed)
    engine.setProperty('voice', 'f1') 

    engine.say(text)
    engine.runAndWait()
