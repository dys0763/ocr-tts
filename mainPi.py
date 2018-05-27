from ImgPC import *
from OCRTTS import *
from DetectPaperPi import *
import RPi.GPIO as GPIO
import time
import os


def main_process(LANG='kor'):
    #the main function that consist of all the functions
    #takes a photo and speaks recognized letters
    src_points, resolution, x = find_paper()
    img = capture_paper(src_points, resolution)
    os.system("xdg-open Paper.jpg")
    if x:
        try:
            print('Image Processing Started.')
            img_final = main_filter(img)
            cv2.destroyAllWindows()
            try: 
                text = ocr(img_final, lang=LANG)
                if not text:
                    print('No Letter is Recognized')
                else:
                    file = open('Recognized Characters.txt', 'w')
                    file.write(text)
                    file.close()
                    os.system('xdg-open "Recognized Characters.txt"')
                    try:
                        tts(text)
                    except:
                        print('Text to Speech Failed')
            except:
                print('Letter Recognizing Failed')
        except:
            print('Image Processing Failed')


GPIO.setmode(GPIO.BOARD)
GPIO.setup(40, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    button_input = GPIO.input(40)
    start_time = 0
    if not button_input:
        print('Button Pushed')
        start_time = time.time()
        lang = 'kor+kor100'
        while not button_input:
            if start_time - time.time() > 1: #if the botton is pushed for 1 sec, the selected language will be English
                lang = 'eng'
                break
            button_input = GPIO.input(40)
        print('Selected Language : {}'.format(lang))
        main_process(LANG=lang)
        print('Waiting for Response...')

GPIO.cleanup()
