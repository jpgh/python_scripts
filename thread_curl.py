#!/usr/bin/python
#!-*- coding: utf-8 -*-
import requests
import lxml.html as html
from datetime import datetime
from time import sleep
import threading

class ThrCurl(threading.Thread):
    stat_exit=False
    def __init__(self, mutex,c,fileLog):
        super(ThrCurl,self).__init__()
        self.mutex = mutex
        self.c=c
        self.fileLog=fileLog
    def run(self):
#        with self.mutex:
        print("Поток %s \r" % self.c)
        r = requests.get("https://vaadin.webpay.by/cluster-demo/put.jsp", verify=False)
        cookie = dict(JSESSIONID=r.cookies['JSESSIONID'])
        while True:
            strResp = ""
            dateStart = datetime.now()
            try:
                rt = requests.get('https://vaadin.webpay.by/cluster-demo/get.jsp', verify=False, cookies=cookie)
            except:
                continue
            dateDiff = datetime.now()-dateStart
            timeResp = dateDiff.microseconds+dateDiff.seconds*1000000
            page = html.document_fromstring(rt.text)
            lResp = page.xpath("//body/text()")

            for line in lResp:
                if "The time" in line:
                    for symb in line:
                        if not symb in ["\n","\r","\f"]:
                            strResp+=symb

            with self.mutex:
                self.fileLog.write("%s - response_code: %s time_resp: %s answ: '%s'; thread - %s\n" \
                     % (dateStart.strftime("%x %X"), rt.status_code, timeResp, strResp, self.c))
            sleep(0.5)
            if self.stat_exit: break

if __name__=="__main__":
    f=open("log", "a")
    submutex = threading.Lock()
    i=0
    threads=[]
    while (i<300):
        i+=1
        thread = ThrCurl(submutex,i,f)
        thread.start()
        threads.append(thread)
        sleep(1)

    while True:
        resp=raw_input("q - выход")
        if resp == 'q': break

    for thread in threads:
        thread.stat_exit=True
    for thread in threads:
        thread.join()
    f.close()
