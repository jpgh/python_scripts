import serial, smtplib, time, sys
#-*- coding: UTF-8 -*-
#������ ����� � COM(1, ���� ����� ������, ������ �������� ���) ����� � ����. Windows.
#���������� ���������� ������ pyserial
#������� ������ - ��� � 10 ����� ���������� COM-����(������ 30 ������)
#��� �������� - ����� � ����
#����� ������� ������ �������� - ���� ���� ������, ��� ����� ���� � ����� - � �����,
#����� ���� ��������� ������ ���, ��� ����������

def sendEmail(bodyMail):
    msgTxt=""
    resL=[]
    toM="admin@webpay.by"
    fromM="Logging ATS"
    subject="Error logging ATS"

    msg = "From: %s\nTo: %s\nSubject: %s\n\n%s"  % ( fromM, toM, subject, bodyMail)
    emailS=smtplib.SMTP('mail.webpay.by:25')
#�������������� � ����-������ - ����� �� ���������� ������� �������, � ����� �������� ����� ���������� ���������
    msg=bytes(msg.encode('utf-8'))
    emailS.sendmail(fromM, toM, msg)

#��� ������ ���� �������� ��� ����� �� ���-�� ����� ttyS0.
#������, ��� ������� �� ����� ���� ������, ��� �� ��������� ����� �������� ������ nohup cat /dev/ttyS0 >> log
port="COM1"
logFile=r"D:\log\ats.txt"

while(True):
    try:
        log=open(logFile,"a")
#timeout=30 - �������� ������� �����, ���� <20 - ���� �� �������� ����������� �� �����
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

