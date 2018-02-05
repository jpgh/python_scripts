#!/usr/bin/python -tt
#!-*- coding: UTF-8 -*-

#формируем более удобный файл на базе access логов из директории wDir
#на выходе получаем:
#RU      14/May/2015:00:00:11    GET /?tutby&andmade HTTP/1.1    5.255.253.14
#CN      14/May/2015:00:00:16    GET / HTTP/1.0  125.84.178.197
#RU      14/May/2015:00:00:17    GET /?tutby&%89%D5U%01 HTTP/1.1 5.255.253.14



from __future__ import print_function
from geoip import geolite2
from os import walk, path
import gzip
import re, sys



wDir = "logepay/"
ipReg = re.compile("[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}")
dateReg = re.compile("- \[([a-zA-Z0-9:/]*) .*\]")

# выбираем шаблон для логов(e-pay)
listFiles=[path.join(root,findfile) for root, subDir, files \
    in walk(wDir)  for findfile in files if "e-pay" in findfile]

# nginx    in walk(wDir)  for findfile in files if "epay_access.log" in findfile]

listFiles.sort()
#print(listFiles)

#listFiles=open(fpan)
# пробегаемся по сформированному списку файлов
for findFile in listFiles:
    try:
        if findFile[-3:]==".gz":
            f=gzip.open(findFile)
        else:
            f=open(findFile)
    except:
        print("Error open file: %s" % findFile)
        continue
#    try:
#пробегаемся по каждому файлу
    for line in f:
        match=ipReg.match(line)
        if not match:
            print("Not Ip")
            continue
        ip = match.group(0)
        matchDate = dateReg.search(line)
        if not matchDate:
            date = "No find"
        date = matchDate.group(1)

        if int(date[:2]) < 14 or int(date[:2])>22:
            continue
        url = line.split('"')[1]
#nginx        url = line.split('"')[3]
#исключаем бел ip
        infoIp = geolite2.lookup(ip)
        country = infoIp.country if infoIp else "BY"
        if country != "BY":
             print("%s\t%s\t%s\t%s" % (country, date, url, ip))
    f.close()

