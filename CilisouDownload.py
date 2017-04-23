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

class CilisouDownload(threading.Thread):
    def __init__(self,url,name):
        threading.Thread.__init__(self)
        self.url = url
        self.name = name

    def run(self):
        webSiteName = 'cilisou'
        page = 0
        tableName ='{}_{}'.format(webSiteName,self.name)
        try:
            cursor.execute("CREATE TABLE {}(Title text, Time text, File text, Size text, Link text)".format(tableName))
        except:
            print('\nWarning: create table {} failure, maybe already exists'.format(tableName))
    
        self.url = self.url + '{}'.format(self.name)
        soup = getSoupObj(self.url + '&p={}'.format(page))

        print('\nTip: began to crawl {} website'.format(webSiteName))
        try:
            while(page <=0):
                print('\nTip: the current processing {} pages ：{:^3}'.format(webSiteName,page))
                titles =[]
                times = []
                files = []
                sizes = []
                links = []
                r = soup('table',{'class':re.compile(r'torrent_name')})
                for i in r:
                    title = i.find_all('a',href = re.compile(r'info'))
                    if len(title)>0:
                        titles.append(title[0].text)
                    t = i.find_all('td',{'class':'ttth'})
                    if len(t)>0:
                        link = t[0].find_all('a',{'href':re.compile(r'magnet:')})[0].attrs['href'][:60]
                        links.append(link)
                    t = i.find_all('td',{'class':''})
                    if len(t)>0:
                        size = t[0].find_all('span',{'class','attr_val'})[0].text.strip()
                        file = t[1].find_all('span',{'class','attr_val'})[0].text.strip()
                        time = t[3].find_all('span',{'class','attr_val'})[0].text.strip()
                        sizes.append(size)
                        files.append(file)
                        times.append(time)
                for i in range(0,min(len(titles),len(links),len(sizes),len(files),len(times))):
                    cursor.execute("insert into {}(Title,Time,File,Size,Link) values(%s,%s,%s,%s,%s)".format(tableName),(titles[i],times[i],files[i],sizes[i],links[i]))
                    conn.commit()
                page += 1
                soup = getSoupObj(self.url + '{}/'.format(page))
        except:
            print('\nError: {} to crawl ceiling or crawler death'.format(webSiteName))
            closeDB()
            traceback.print_exc()
        else:
            closeDB()
