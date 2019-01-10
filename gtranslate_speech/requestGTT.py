# coding=utf8
import requests
import os
from uuid import uuid4
import wave
import logging
import re


class GTSpeech(object):
    def __init__(self):
        self.urlBase = None
        self.querystring = dict(ie = "UTF-8",client = "tw-ob")#,"tl":"en"}
        self.headers = {
            'cache-control' : "no-cache"
        }
        self.urlIndex = 0
        self.urls = ['.vn', '.br', '.pt']
        self.mp3 = True
        self.fileName = "GTT"
        self.extensions = dict(mp3= ".mp3", wav= ".wav")
        self.ffmpeg = None
        self.maxTry = 10
        self.nTry=0
        self.regex=  r"(\s|\w)+"

        pass
    
    def __checkLib(self):
        try:
            self.ffmpeg =  __import__('ffmpeg')
            # import ffmpeg
            return True
        except ImportError:
            raise Exception("You must have ffmpeg lib installed")
        pass

    def setText(self, text):
        matches = re.search(self.regex, text)
        print(matches.group(0))
        self.querystring["q"] = matches.group(0)
        return self
        
    def __setLang(self, lang):
        self.querystring["tl"]= lang
        pass

    def __request(self):
        self.__buildUrl()
        response = requests.request("GET", self.urlBase, headers=self.headers, params=self.querystring)
        if(response.ok):
            self.__writeFileMp3(response)
            return True
        else:
            logging.warning('Trying request again, something is wrong')
            if(self.__haveTries()):
                _ = self.__request()
        return False
    
    def __haveTries(self):
        self.nTry +=1
        if(self.nTry <= self.maxTry):
            return True
        return False


    def __changeUrl(self):
        self.urlIndex += 1
        if(self.urlIndex >= len(self.urls)):
            self.urlIndex = 0
        pass
    def __buildUrl(self):
        url = dict(protocol="https://", url="translate.google.com", country=self.urls[self.urlIndex], route="/translate_tts")
        self.urlBase = url['protocol']+url['url']+url['country']+url['route']
        self.__changeUrl()
        pass


    def __writeFileMp3(self, response):
        path = os.path.join('./', self.__getFileName('mp3'))
        with open(path, 'wb+') as f:
            f.write(response.content)

    def __getFileName(self, type):
        return self.fileName + self.extensions[type]

    def __writeFileWav(self):
        if(os.path.isfile(self.__getFileName('mp3'))):
            out, _ = (self.ffmpeg
                .input(self.__getFileName('mp3'))
                .output('-', format='s16le', acodec='pcm_s16le', ac=1, ar='16k')
                .overwrite_output()
                .run(capture_stdout=True)
            )
            CHANNELS = 1
            RATE = 16000
            swidth = 2
            with wave.open(os.path.join('./', self.__getFileName('wav')), 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(swidth)
                wf.setframerate(RATE)
                wf.writeframes(out)
            self.__removeMp3()

    def __removeMp3(self):
        if(not self.mp3):
            os.remove(os.path.join('./', self.__getFileName('mp3')))

    def __setFileName(self, filename):
        if(filename != ''):
            self.fileName = filename
        else:
            self.fileName = str(uuid4()).replace('-','')[:10]+"-"+self.querystring["q"]
        pass

    def toWav(self):
        if(bool(self.__checkLib())):
            self.__writeFileWav()
        pass

    def __clearTries(self):
        self.nTry = 0


    def listen(self, filename='', lang='en', mp3=True):
        self.__setLang(lang)
        self.__setFileName(filename)
        self.mp3 = mp3
        if(self.__request()):
            logging.debug('File successfully created')
        else:
            logging.critical('Could not connect to server')
        self.__clearTries()
        return self
    pass



# r = RequesterGTT()
# r.setText("Hellooo my name is neto").listen(lang="en", mp3=False).toWav()
# r.setText("Hellooo my name is lucas").listen(mp3=False).toWav()
# r.setText("Hellooo my name is ane").listen('gogogo', mp3=True).toWav()
