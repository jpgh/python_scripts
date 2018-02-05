#!/usr/bin/python -tt
#!-*- coding: UTF-8 -*-

#Переключение между провайдерами для зон днс. В качестве входных параметров принимает режим работы зоны:
#BT - только белтелекомовские ip; AT - только ip Атланта; Default - режим работы по умолчанию, задействованы
#оба провайдера.
#Как работает: скрипт вызывается для переключения на определенный режим работы из перечисленных выше. Проходим
#по файлу, ищем по маске в A записях какие строки расскоментировать, комментируя остальные A записи для данного
#  доменного имени.
#ВАЖНО: Для записей Default (одновременно 2 провайдера) необходимо указывать комментарий default_value
#затем делаем rndc reload
#Для BT используются маска ip 86.57.158|178.124.157, AT - 87.252.252, Default - ; default_value

from pprint import pprint
import re, os, logging
from sys import argv
from shutil import copy
from datetime import datetime
from subprocess import call

zones = ["/var/named/data/webpay.by.zone.inet", "/var/named/data/e-pay.by.zone.inet"]
backupDir = "backup_inet_zone"


LOG_FORMAT = ('%(levelname) -10s %(asctime)s '
                 ' %(lineno) -d: %(message)s')
LOGGER = logging.getLogger(__name__)



class zoneResult(object):

    def __init__(self, newZone, name):
        self.newZone = newZone
        self.name = name
        self.serialOld, self.serialLineNumber = self.getSerial()


    def findPattern(self, pattern):

        patternUnc = re.compile("^([-.@a-zA-Z0-9_]*)\s*IN\s*A\s*([0-9]{1,3}.){1,3}[0-9]{1,3}")
        for countUncomment, lineUncomment in enumerate(self.newZone):
            lineUncomment = lineUncomment.lstrip()
            match = pattern.search(lineUncomment)

            if not match:
                continue
            domainName = match.group(1)

            if lineUncomment[0] == ";":
                self.newZone[countUncomment] = lineUncomment[1:]

            for countComment, lineComment in enumerate(self.newZone):

                if countComment == countUncomment:
                    continue

                lineComment = lineComment.lstrip()

                match = re.search("^%s\s*IN\s*A\s*([0-9]{1,3}.){1,3}[0-9]{1,3}" % domainName, lineComment)
                if match:
                    self.newZone[countComment] = ";%s" % lineComment


    def getSerial(self):

        patternSerial = re.compile("^[( ]*([0-9]{10})\s*?;\s*?Serial")
        for count, line in enumerate(self.newZone):
            match = patternSerial.search(line)
            if not match:
                continue
            return match.group(1), count

        raise NewZoneException("No find Serial")


    def incrementSerial(self):

        serialNN = "%02d" % (int(self.serialOld[8:]) + 1)
        dateNow = datetime.now().strftime("%Y%m%d")

        if dateNow != self.serialOld[:8]:
            serialNN = "00"

        if int(serialNN) > 97:
            raise NewZoneException("Serial number > 97!")

        serialNew = dateNow+str(serialNN)
        self.newZone[self.serialLineNumber] = self.newZone[self.serialLineNumber].replace(self.serialOld, serialNew)


    def saveZone(self, zone):

        if self.newZone == zone:
            raise NewZoneException("No find change in %s" % self.name)

        self.incrementSerial()
        f = open(self.name, "w")

        for line in self.newZone:
            f.write(line)
        f.close()



class NewZoneException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)



def backup(zoneName, serial, backupDir = "backup_inet_zone"):

    dirD = os.path.join(os.path.dirname(zoneName), backupDir)
    try:
        os.mkdir(dirD)
    except OSError as e:
        pass
    copy(zoneName, os.path.join(dirD, os.path.basename(zoneName)+"_"+serial))


def readZone(zoneName, pattern, backupDir, provider):

    try:
        f = open(zoneName)
        zoneOrig = f.readlines()
        newZone = zoneResult(zoneOrig[:], zoneName)
        newZone.findPattern(pattern)
    except NewZoneException as e:
        LOGGER.error("Error create new zone %s: %s" % (zoneName, e))
        return
    except IOError as e:
        LOGGER.error("Error read zone file %s: %s" % (zoneName, e))
        return
    finally:
        if "f" in locals():
            f.close()

    try:
        backup(zoneName, newZone.serialOld, backupDir)
        newZone.saveZone(zoneOrig)
    except IOError as e:
        LOGGER.error("Error backup or save zone file %s: %s" % (zoneName, e))
        return
    except NewZoneException as e:
        LOGGER.error("Error save zone file  %s: %s" % (zoneName, e))
        return
    call(["rndc", "reload"])
    LOGGER.info("Zone %s updates to %s" % (zoneName, provider ))


def main():

    pattern = {}
    #с начала строки, возможны пробелы, возможен ";", возможны несколько пробелов, не ns[0-9], доменное имя, пробелы, IN, пробелы,
    #  A пробелы, ip адрес. group(1) - доменное имя
    pattern['BT'] = re.compile("^;?\s*?(?!ns[0-9])([-.@a-zA-Z0-9_]*)\s*IN\s*A\s*(86.57.158|178.124.157)")
    pattern['AT'] = re.compile("^;?\s*?(?!ns[0-9])([-.@a-zA-Z0-9_]*)\s*IN\s*A\s*87.252.252")
    pattern['Default'] = re.compile("^;?\s*?(?!ns[0-9])([-.@a-zA-Z0-9_]*)\s*IN\s*A\s*([0-9]{1,3}.){1,3}[0-9]{1,3}\s*;\s*default_value")
    provider = ""

    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, filename = "/var/log/change_dns_script.log")

    if len(argv) == 2:
        provider = argv[1]
    if provider not in ["BT", "AT", "Default"]:
        print("use arg: BT - only Beltelecom; AT - only Atlant; Default - default records;\nExit")
        LOGGER.error("Invalid arg - %s" % provider)
        exit()

    for zoneName in zones:
       readZone(zoneName, pattern[provider], backupDir, provider)


if __name__ == '__main__':
    main()
