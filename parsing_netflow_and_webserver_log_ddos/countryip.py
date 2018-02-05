#!/usr/bin/python
#!-*- coding: UTF-8 -*-

#встраиваистся в конвеер на выход nfdump, трафик должен быть уже отсортирован
#формирует на выходе файл для каждой записи со структурой:

#BY 2015-05-14 12:05:00.170 195.222.65.18:50440 -> 86.57.158.94:443 1104
#CN 2015-05-14 12:05:00.180 114.244.38.106:57708 -> 86.57.158.94:80 0

#пример nfdump: 
#nfdump -M /var/netflow/profiles-data/live/upstream1/2015 -R 05/14/nfcapd.201505141205:06/09/nfcapd.201506091535 | grep -E ">     86.57.158.94" | /home/podskokov/countryip.py > /var/tmp/all_nfdump_stat

from geoip import geolite2
import fileinput

for line in fileinput.input():
    arrLine = line.split()
    infoIp = geolite2.lookup(arrLine[5].split(":")[0])
    country = infoIp.country if infoIp else "??"
    print("%s %s %s %s %s %s %s" % (country, arrLine[0], arrLine[1], arrLine[5], arrLine[6], arrLine[7], arrLine[11]) )
