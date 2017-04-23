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
    
class BtcherryDownload(threading.Thread):
    def __init__(self,url,name):
        threading.Thread.__init__(self)
        self.url = url
        self.name = name

    def run(self):
        webSiteName = 'btcherry'
        page = 1
        tableName ='{}_{}'.format(webSiteName,self.name)
        try:
            cursor.execute("CREATE TABLE {}(Title text, Time text, File text, Size text, Link text)".format(tableName))
        except:
            print('\nWarning: create table {} failure, maybe already exists'.format(tableName))
    
        self.url = self.url + '{}&p='.format(self.name)
        soup = getSoupObj(self.url + str(page))

        print('\nTip: began to crawl {} website'.format(webSiteName))   
        try:
            while(True):
                print('\nTip: the current processing {} pages ：{:^3}'.format(webSiteName,page))
                r = soup('div',{'class':'r','style':''})
                for i in r:
                    title = i.find_all('h5',{'class':'h'})[0].text
                    link = i.find_all('a',href = re.compile(r'magnet:'))[0].attrs['href'][:60]
                    divs = i.find_all('div')[0]
                    time = ''
                    file = ''
                    size = ''
                    for j in divs.find_all('span'):
                        if(re.search(r'收录时间：',j.text)):
                            time = re.sub(r'收录时间：','',j.text)
                        elif(re.search(r'大小：',j.text)):
                            size = re.sub(r'大小：','',j.text)
                        elif(re.search(r'文件数：',j.text)):
                            file = re.sub(r'文件数：','',j.text)  
                    
                    cursor.execute("insert into {}(Title,Time,File,Size,Link) values(%s,%s,%s,%s,%s)".format(tableName),(title,time,file,size,link))
                    conn.commit()
                page += 1
                soup = getSoupObj(self.url + str(page))
        except:
            print('\nError: {} to crawl ceiling or crawler death'.format(webSiteName))
            closeDB()
            traceback.print_exc()
        else:
            closeDB()
