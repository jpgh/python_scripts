#!/usr/bin/python
#-*- coding: utf8 -*-
import re, sys
import smtplib
from ssl import get_server_certificate, PROTOCOL_SSLv23
from urlparse import urlparse
from logtail import Pygtail
from time import sleep
from datetime import datetime
from subprocess import call, Popen, PIPE
import pexpect

log = "/var/log/messages"
notValidCert = "unable to find valid certification path"
#url = re.compile('request for \"https\:\/\/([A-Za-z0-9\.-_:]*)[\"/]{1}')
urlR = re.compile('request for \"(https\:\/\/.*)\"')
msg = ""
added = False

#отправка почты
def sendEmail(bodyMail,head):

    fromM="Monitoring_sandbox_notify_certs@webpay.by"
    subject=head
    dateNow=datetime.now()
    strDateNow=dateNow.strftime("%a, %d %b %Y %X %z (%Z)")
#    recipients=["admin@webpay.by","shad862@gmail.com"]
    recipients=["admin@webpay.by"]

    for toM in recipients:
        msg = "Date: %s\nFrom: %s\nTo: %s\nSubject: %s\n\n%s"  % ( strDateNow, fromM, toM, subject, bodyMail)
        emailS=smtplib.SMTP('mail.webpay.by:25')
        emailS.sendmail(fromM, toM, msg)


# logtail, продолжаем с прошлой ротации
logIter = Pygtail(log)

#перебираем записи в логе с места, на котором остановились в прошлый раз
for line in logIter:

    if not (notValidCert in line):
        continue

    matchDomain = urlR.search(line)

    if not matchDomain:
        continue

    url = matchDomain.group(1)
    urlParse = urlparse(url)
    domain = urlParse.hostname
    port = urlParse.port if urlParse.port else 443
    if not domain or not port:
        continue
#    print(domain+":"+str(port))

    if not "valid certification path' - %s" % domain in msg:
        msg += "Find error 'unable to find valid certification path' - %s\n" % domain

#получаем сертификат с сайта мерчанта
#    print(domain +":"+str(port))
    try:
        cert = get_server_certificate((domain,port), ssl_version=PROTOCOL_SSLv23)
    except:
        msg += "No get server certificate %s:%s, Error: %s\n" % (domain, str(port), str(sys.exc_info()))
        continue
#    print(cert)
#записываем сертификат во временный файл
    try:
        fileCert = open("/tmp/certs_temp","w")
        fileCert.write(cert)
        fileCert.close()
    except:
        msg += "Error write cert to file, %s:%s, Error: %s\n" % (domain, (str(port)), str(sys.exc_info()))
        continue

#добавляем сертификат в java хранилище
    try:
        keytool = pexpect.spawn('/usr/java/default/bin/keytool -import -alias %s  -file /tmp/certs_temp -keystore /usr/java/default/jre/lib/security/jssecacerts' % domain)
        keytool.expect("Enter keystore password:")
        keytool.sendline("changeit")
        keytool.expect(".*")
        keytool.sendline("yes")
        keytool.expect('.*')
    except:
        msg += "Error add cert to keystore, %s:%s, Error: %s\n" % (domain, (str(port)), str(sys.exc_info()))
        continue

    added = True
    if not "Added certs %s" % domain in msg:
        msg+= "Added certs %s to keystore\n" % domain

#msg += "test\n"
if added:
# если найдены сертификаты - рестартуем wildfly
    call(["/etc/init.d/wildfly", "restart"])
    sleep(30)
    statW = Popen(["/etc/init.d/wildfly", "status"], stdout=PIPE)
    out, err = statW.communicate()
    if not "wildfly is running" in out:
        msg += "!!!!!! Wildfly NOT RUNNING !!!!!\n"

# отправляем все сообщения на почту
    sendEmail(msg, "Certs sandbox")

#Хороший вариант, но интерактивность до первой команды.
#После этого соединение закрывается

#pipeKey = subprocess.Popen(["yum", "shell"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=False)
#out, err = pipeKey.communicate(input = "help")

