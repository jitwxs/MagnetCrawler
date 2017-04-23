# -*- coding: utf-8 -*

from Bt1024Download import *
from BtcherryDownload import *
from CililianDownload import *
from CilisouDownload import *
from FeijibtDownload import *

try:
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='magnet',charset="utf8")
    cursor = conn.cursor()
except:
    print('\nError: database connection failed')

def closeDB():
    global conn,cursor
    conn.close()
    cursor.close()

if __name__ == '__main__':
    input('MUST READ：Before use, please be sure to manually modify the code at the beginning of the MySQL database connection string!After the modification and correct,press Enter key to continue...')
    name = input('\nNote: please enter keywords to search : ')
   
    bt1024 = Bt1024Download('http://www.bt1024.org/q/',name)
    btcherry = BtcherryDownload('http://www.btcherry.info/search?keyword=',name)
    cililian = CililianDownload('http://cililian.me/list/',name)
    cilisou = CilisouDownload('http://www.cilisou.cn/s.php?q=',name)
    feijibt = FeijibtDownload('http://feijibt.com/list/',name)
    thread_list = []
    
    thread_list.append(bt1024)
    thread_list.append(btcherry)
    thread_list.append(cililian)
    thread_list.append(cilisou)
    thread_list.append(feijibt)

    for i in thread_list:
        i.start()
    for i in thread_list:
        i.join()

    print('Crawl over. The application will close...')
