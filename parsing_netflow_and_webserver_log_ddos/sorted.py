#!/usr/bin/python
#!-*- coding: UTF-8 -*-

#получаем общую статистику сетевых соединений по часам.
#на входе файл, полученный countryip.py, на выходе:
#2015-05-14 14   BY: 53744       CN: 6507
#2015-05-14 15   BY: 50624       CN: 56749
#только страны, к-во соединений от которых > 5000
#
#

from pprint import pprint
import fileinput

def printHour(dictHour):
    country = ""
    by = 0
    if res == {}: return
    date = dictHour.keys()[0]
    for key in dictHour[date]:
        if key == "BY" or key == "??":
            by += dictHour[date][key]
#сравниваем значение с 10000 - т.к. записи в netflow у нас дублируются.
        if dictHour[date][key] > 10000 and key != 'BY' and key !="??":
#из-за дублирования делим общее количество на 2
            country += key + ": "+str(dictHour[date][key]/2)+"\t"
    if len(country) > 0:
# с бел Ip тоже делим на 2
        print("%s\tBY: %s\t%s" %(date, by/2, country))



f = open("/var/tmp/all_nfdump_stat")
fIp = open("ip","w")
res = {}
prevHour = 0

for line in f:
    arrLine = line.split()
    hour = arrLine[2].split(":")[0]

    date = arrLine[1]+" "+hour

    if hour != prevHour:
         printHour(res)
         res = {}
         res[date] = {}

    if not arrLine[0] in res[date].keys():
        res[date][arrLine[0]] = 0

    res[date][arrLine[0]] += 1
    prevHour = hour

printHour(res)

