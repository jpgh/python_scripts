import serial, smtplib, time, sys
#-*- coding: UTF-8 -*-
#запись логов с COM(1, если нужен другой, просто изменить им€) порта в файл. Windows.
#необходимо установить модуль pyserial
#ѕринцип работы - раз в 10 минут опрашивает COM-порт(читает 30 секунд)
#что прочитал - пишет в файл
#“акой принцип работы приемлем - если порт закрыт, ј“— пишет себе в буфер - и потом,
#когда порт откроетс€ отдаст все, что накопилось

def sendEmail(bodyMail):
    msgTxt=""
    resL=[]
    toM="admin@webpay.by"
    fromM="Logging ATS"
    subject="Error logging ATS"

    msg = "From: %s\nTo: %s\nSubject: %s\n\n%s"  % ( fromM, toM, subject, bodyMail)
    emailS=smtplib.SMTP('mail.webpay.by:25')
#преобразование в байт-строку - иначе не передаютс€ русские символы, а байты почтовый агент распознает нормально
    msg=bytes(msg.encode('utf-8'))
    emailS.sendmail(fromM, toM, msg)

#ƒл€ линукс надо изменить им€ порта на что-то вроде ttyS0.
#¬ообще, дл€ линукса не нужет этот огород, тот же результат можно получить сделав nohup cat /dev/ttyS0 >> log
port="COM1"
logFile=r"D:\log\ats.txt"

while(True):
    try:
        log=open(logFile,"a")
#timeout=30 - вы€влено опытным путем, если <20 - логи не успевают прочитатьс€ из порта
        s = serial.Serial(port, timeout=30)
        mess=s.readlines()
        for line in mess:
            log.write(line.decode('utf-8'))
        mess=[]
    except :
         sendEmail(str(sys.exc_info()[1]))
    finally:
        if 's' in locals(): s.close()
        if 'log' in locals(): log.close()
		time.sleep(600)

