# ocr-tts

This project consists of dynamic image processing, static image processing, tesseract-OCR and pyttsx3.

Required Libraries: OpenCV(cv2), Numpy, Pytesseract, Pyttsx3

Required Hardwares: Pull-Up Button(pin 40), Camera Module for Raspberry Pi, 3.5mm plug Audio Output Device


YOUTUBE

Introduction

https://youtu.be/yivvSipqWnA


test

https://youtu.be/cybrp_YRUT4


----------------
Required process before execute this system
------------------

sudo nano ~/.profile
(sleep 10 && . /home/pi/ocr-tts/auto.sh)&


Location : /home/pi/

sudo git clone https://github.com/dys0763/ocr-tts.git

--------------------------------

Location : /home/pi/

sudo git clone https://github.com/dys0763/espeak-data.git

--------------------------------

Location : /usr/share/tessract-ocr/

sudo rm -r tessdata

sudo git clone https://github.com/dys0763/tessdata.git

YOUTUBE - making tesseract data

https://youtu.be/dhgL_cLnVBo
