import re
import html

from selenium import webdriver
from selenium.webdriver.common.keys import Keys 

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import time
import locale
import requests
from bs4 import BeautifulSoup
import pandas as pd

# functions to optimize code
def split_level_type_duty_trade(words, lst, Text):
    
    if words in Text:
        Text = Text.replace(words,'')
        Text = Text.replace('\n','')
        lst.append(Text)
    else:
        lst.append('-')
        
    return lst


# 未登入
def LinkedIn_noLogIn(scrolls, keywords):

    jobTitle = []
    jobCompany = []
    address = []
    builtIn = []
    jobDetail_URL = []
    content=[]
    level=[]
    type=[]
    duty=[]
    trade=[]

    # bs4 settings
    HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
              'cookie': 'over18=1;'}

    # selenium settings
    options=Options()
    options.chrome_executable_path='./chromedriver'
    driver=webdriver.Chrome(options=options)
    #driver.get('https://www.linkedin.com/jobs/search/?location=%E5%8F%B0%E7%81%A3&geoId=104187078&f_TPR=r86400&f_JT=F&currentJobId=3482773339&position=1&pageNum=0')
    driver.get(f'https://www.linkedin.com/jobs/search/?keywords={keywords}&location=%E5%8F%B0%E7%81%A3&locationId=&geoId=104187078&f_TPR=r604800&f_JT=F&position=1&pageNum=0')

    # total jobs count
    jobs_num = driver.find_element(By.CLASS_NAME, 'results-context-header__job-count')
    locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' ) 
    jobs_num = locale.atoi(jobs_num.text)
    scrolls_max = jobs_num//25
    
    scroll=0
    
    if scrolls>scrolls_max:
        scrolls=scrolls_max
        
        print(f"Max scroll down counts: {scrolls}")

    while scroll<=scrolls:

        if scrolls>=6:
            jobMoreBtn = driver.find_elements(By.TAG_NAME, 'button')

            try:
                for btn in jobMoreBtn[::-1]:
                    if btn.text=='更多職缺': # or btn.text=='Show more':
                        jobMoreBtn = btn

                        break

                jobMoreBtn.send_keys(Keys.ENTER)

                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(3)

                scroll+=1

            except:
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(3)
                scroll+=1
        
        else:
          #if scroll<=5:
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(3)
            scroll+=1

    titleTags=driver.find_elements(By.CLASS_NAME, 'base-search-card__title')
    companyTags=driver.find_elements(By.CLASS_NAME, 'base-search-card__subtitle')
    workcityTags=driver.find_elements(By.CLASS_NAME, 'job-search-card__location')
    onlineTags=driver.find_elements(By.TAG_NAME, 'time')
    jobDetailURL=driver.find_elements(By.TAG_NAME, 'a')

    for n in range(len(titleTags)):
        jobTitle.append(titleTags[n].text)
        jobCompany.append(companyTags[n].text)
        address.append(workcityTags[n].text)
        builtIn.append(onlineTags[n].get_attribute('datetime'))


    for n in range(len(jobDetailURL)):

        j = jobDetailURL[n].get_attribute('href')
        if 'jobs/view' in j and 'result_search-card' in j:
            jobDetail_URL.append(j)


    for url in jobDetail_URL:
        r = requests.get(url, headers=HEADERS)
        r.encoding = 'utf-8' #轉換編碼至UTF-8
        #soup = BeautifulSoup(r.text, features='lxml')
        soup = BeautifulSoup(r.text)

        jobContent = soup.find("section",'show-more-less-html')
        try:
            content_text = jobContent.text
            content_text = content_text.replace('\n','')
            content.append(content_text)
        except:
            content.append('-')

        jobItems = soup.find_all("li",'description__job-criteria-item')

        if len(jobItems)==4:
            for i in jobItems:
                Text = i.text
                if '職階等級' in Text:
                    Text = Text.replace('職階等級','')
                    Text = Text.replace('\n','')
                    level.append(Text)
                elif '工作類型' in Text:
                    Text = Text.replace('工作類型','')
                    Text = Text.replace('\n','')
                    type.append(Text)
                elif '工作職能' in Text:
                    Text = Text.replace('工作職能','')
                    Text = Text.replace('\n','')
                    duty.append(Text)
                elif '所屬產業' in Text:
                    Text = Text.replace('所屬產業','')
                    Text = Text.replace('\n','')
                    trade.append(Text)
        else:
            Text = i.text
            level = split_level_type_duty_trade('職階等級', level, Text)
            type = split_level_type_duty_trade('工作類型', type, Text)
            duty = split_level_type_duty_trade('工作職能', duty, Text)
            trade = split_level_type_duty_trade('所屬產業', trade, Text)

    driver.close()

    df = pd.DataFrame()

    df['職稱']=jobTitle
    df['公司']=jobCompany
    df['地址']=address
    df['職缺內容']=content
    df['職缺上架日期']=builtIn
    df['職等']=level
    df['工作類型']=type
    df['職務']=duty
    df['產業']=trade

    return df

# 以資料科學家為例 滑鼠滾動到底三次 所爬取的職缺內容
jobs = LinkedIn_noLogIn(3,'Data Scientist')
jobs