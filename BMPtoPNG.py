#!/usr/bin/python -tt
#!-*- coding: UTF-8 -*-

#конвертация всех файлов из bmp в png в указанной директории wDir


from os import walk, path, remove
import Image, pprint

wDir = "/var/share/sshots"
res = {
    'countProcessing': 0,
    'countBmp': 0,
    'countRemove': 0,
    'countConvert': 0,
    'countError': 0,
}

listFiles=[path.join(root,findfile) for root, subDir, files \
    in walk(wDir)  for findfile in files]

print("Всего файлов: {0}".format(len(listFiles)))

for fileS in listFiles:
    res['countProcessing'] += 1
    if fileS[-4:] != ".bmp":
        continue
    res['countBmp'] += 1
    filename = path.basename(fileS)
    try:
        Image.open(fileS).save(fileS[:-3]+"png")
        res['countConvert'] += 1
    except:
        print("Don't convert "+fileS+"!!!")
        res['countError'] += 1
        continue
    remove(fileS)
    print("{0} сконвертирован".format(fileS))
    res['countRemove'] += 1

res['old'] = res['countConvert'] - res['countRemove']

print("Файлов просмотрено: {countProcessing}; из их bmp: {countBmp}; ошибок:{countError}; не удалено bmp: {old} ".format(**res))


