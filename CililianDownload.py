#encoding : utf-8

from bs4 import BeautifulSoup
import requests,re,traceback,pymysql,threading

try:
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='magnet',charset="utf8")
    cursor = conn.cursor()
except:
    print('\nError: database connection failed')

def getHTMLText(url):
    try:
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
        r = requests.get(url,timeout=30,headers = headers)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return ''

def getSoupObj(url):
    try:
        html = getHTMLText(url)
        soup = BeautifulSoup(html,'html.parser')
        return soup
    except:
        print('\nError: failed to get the Soup object')
        return None

def closeDB():
    global conn,cursor
    conn.close()
    cursor.close()

class CililianDownload(threading.Thread):
    def __init__(self,url,name):
        threading.Thread.__init__(self)
        self.url = url
        self.name = name

    def run(self):
        webSiteName = 'cililian'
        page = 1
        tableName ='{}_{}'.format(webSiteName,self.name)
        try:
            cursor.execute("CREATE TABLE {}(Title text, Time text, File text, Size text, Link text)".format(tableName))
        except:
            print('\nWarning: create table {} failure, maybe already exists'.format(tableName))
    
        self.url = self.url + '{}/'.format(self.name)
        soup = getSoupObj(self.url + '{}.html'.format(page))

        print('\nTip: began to crawl {} website'.format(webSiteName))
        try:
            while(True):
                print('\nTip: the current processing {} pages ：{:^3}'.format(webSiteName,page))
                r = soup('li')
                for i in r:
                    title = i.find_all('div',{'class':'T1'})[0].text
                    link = i.find_all('div',{'class':'dInfo'})[0].find_all('a',{'href':re.compile(r'magnet:')})[0].attrs['href'][:60]
                    text = i.find_all('dl',{'class':'BotInfo'})[0].text
                    infos = text.strip().split('\n')
                    time = ''
                    file = ''
                    size = ''
                    for j in infos:
                        if(re.search(r'创建时间:',j)):
                            time = re.sub(r'创建时间:','',j).strip()
                        elif(re.search(r'种子大小:',j)):
                            size = re.sub(r'种子大小:','',j).strip()
                        elif(re.search(r'文件数量:',j)):
                            file = re.sub(r'文件数量:','',j).strip()

                    cursor.execute("insert into {}(Title,Time,File,Size,Link) values(%s,%s,%s,%s,%s)".format(tableName),(title,time,file,size,link))
                    conn.commit()
                page += 1
                soup = getSoupObj(self.url + '{}/'.format(page))
        except:
            print('\nError: {} to crawl ceiling or crawler death'.format(webSiteName))
            closeDB()
            traceback.print_exc()
        else:
            closeDB()
