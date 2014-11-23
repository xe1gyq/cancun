#!/usr/bin/python

import ConfigParser
import os
import string
import sys

from core.aprsnet import AprsNet
from core.voicesynthetizer import VoiceSynthetizer
from core.phonetic import Phonetic

class Aprstt(object):

    def __init__(self, voicesynthetizer):

        self.aprs = AprsNet()
        self.phonetic = Phonetic()

        self.conf = ConfigParser.ConfigParser()
        self.path = "configuration/aprstt.config"
        self.conf.read(self.path)

        self.speaker = voicesynthetizer

    def dtmf_replace(pair):
        d = {}
        d["2A"] = "A"
        d["2B"] = "B"
        d["2C"] = "C"
        d["3A"] = "D"
        d["3B"] = "E"
        d["3C"] = "F"
        d["4A"] = "G"
        d["4B"] = "H"
        d["4C"] = "I"
        d["5A"] = "J"
        d["5B"] = "K"
        d["5C"] = "L"
        d["6A"] = "M"
        d["6B"] = "N"
        d["6C"] = "O"
        d["7A"] = "P"
        d["7B"] = "Q"
        d["7C"] = "R"
        d["7D"] = "S"
        d["8A"] = "T"
        d["8B"] = "U"
        d["8C"] = "V"
        d["9A"] = "W"
        d["9B"] = "X"
        d["9C"] = "Y"
        d["9D"] = "Z"
        return d[pair]

    def key_composition(self, string):
        message = None
        callsign = None
        if '*' in string:
            string = string.split('*')
            message = string[0]
            callsign = string[1]
        return message, callsign

    def keytype_get(self, string):
        datafields = {'PP': 'callsign', 'PS': 'position', 'SP': 'status', 'SS': 'message'}
        keytype = string[:2]
        return datafields.get(keytype)

    def keytype_translate(self, keytype):
        keytypes = {'callsign': 'indicativo', 'position': 'posicion', 'status': 'estado', 'message': 'mensaje'}
        return keytypes.get(keytype)

    def user_get(self, string):
        user = string[2:4]
        if string[4:5] == '0':
            generic = True
        else:
            generic = False
        return user, generic

    def command_get(self, generic, string):
        if generic:
             request = string[5:]
        else:
             request = string[4:]
        return request

    def callsign_decode(self, string):
        string = string[1:-1:]
        try:
            if len(string) > 5:
                self.callsign_decoded = self.conf.get("long", string)
            else:
                self.callsign_decoded = self.conf.get("short", string)
        except:
            self.speaker.speechit("Indicativo no valido")
            sys.exit(1)

        return self.callsign_decoded

    def position_decode(self, string):
        return string[1::].upper()

    def status_decode(self, string):
        return string[1::].upper()

    def query(self, string):

        print '[Cancun] APRS Touch Tone | ' + string

        if self.keytype_get(string) is 'callsign':
            user, generic = self.user_get(string)
            callsign = self.conf.get("users", user)
            self.speaker.speechit("Estacion " + ' '.join(self.phonetic.decode(callsign)))

        command = self.command_get(generic, string)
        if generic:
            user = 'generic'
        else:
            user = callsign

        messagenumber = command[2:4]
        messagetype = self.keytype_get(command[0:2])
        messagetype = self.keytype_translate(messagetype)
        message = messagetype + ' ' + messagenumber
        self.speaker.speechit(message)
        message = self.conf.get(user, command)
        self.speaker.speechit(message)
        aprs_message = callsign.upper() + " " + message
        self.aprs.send_packet(aprs_message)

        return

if __name__ == '__main__':

    test = Aprstt("temp")