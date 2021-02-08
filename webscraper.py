from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
from sqlalchemy import create_engine
engine = create_engine('sqlite://', echo=False)

def loadhtml(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    htmltext = driver.page_source
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
           break
        last_height = new_height
    driver.quit()
    return htmltext


def finddata(htmltext):
    soup = BeautifulSoup(htmltext, "lxml")
    f1 = soup.find("table",{"class":"table table-responsive-sm table-bordered"})
    tbody_all = f1.find_all('tbody')
    list2 = []
    tuple1 = ()
    n = 0
    while n<len(tbody_all):
        topic = tbody_all[n].find('tr')
        td_tag = topic.td
        topictext = td_tag.get_text()
        header_all = tbody_all[n].find_all('th')
        for header in header_all:
            a_tag = header.a
            txt = a_tag.get_text()
            url = a_tag['href']
            list2.append((topictext, txt, url))
        n+=1
    tuple1 = tuple(list2)
    return tuple1

def findintro(htmltext):
    list2 = []
    soup = BeautifulSoup(htmltext, "lxml")
    f1 = soup.find("div",{"class":'offset-md-1 col-md-10'})
    all_text = f1.get_text()
    all_text = all_text.replace('\n','')
    return all_text


def savetodatabase(tuple1):
    data = tuple1
    df = pd.DataFrame(data, columns=['Intro', 'Course title','URL'])
    pd.set_option("display.max_rows", None, "display.max_columns", None,'display.max_colwidth', None)
    return df



def getcoursedesc(dataframe):
    n = 0
    list = []
    tuple1 = ()
    while n < len(dataframe.index):
        url_1 = dataframe.iloc[n]['URL']
        url_2 = 'https://www.ucsc-extension.edu'
        url_2 += url_1
        htmltext = loadhtml(url_2)
        intro_info = findintro(htmltext)
        list.append(intro_info)
        n+=1
    return list

def savetodatabasefinal(dataframe,list,title):
    dataframe['Course Description'] = list
    dataframe.style.set_caption(title)
    csv_name = title
    csv_name_append = '.csv'
    csv_name += csv_name_append
    dataframe.to_csv(csv_name, encoding='utf-8', index=False)
    dataframe.to_sql('general database', con=engine)
    pd.set_option("display.max_rows", None, "display.max_columns", None,'display.max_colwidth', -1)
    print(title)
    print(database.head(20))

if __name__ == '__main__':


    url = 'https://www.ucsc-extension.edu/certificates/database-and-data-analytics/'
    title = "general database"


    htmltext = loadhtml(url)
    tab_info = finddata(htmltext)
    database = savetodatabase(tab_info)
    introductioninfo = getcoursedesc(database)
    savetodatabasefinal(database,introductioninfo,title)



