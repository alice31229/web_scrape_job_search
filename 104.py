import requests
from bs4 import BeautifulSoup
import pandas as pd

from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
             'cookie': 'over18=1;'}


def webCrawl_104(pages):

    jobTitle = []
    companyName = []
    trade = []
    duty = []
    onlineDate = []
    location = []
    salary = []
    companyStandard = []
    applyCount = []
    jobContent = []
    jobCriteria = []
    
    # selenium settings
    options = Options()
    options.chrome_executable_path='./chromedriver'
    driver = webdriver.Chrome(options=options)

    for p in range(1, pages+1):
    
        # 職缺列表頁的 URL
        url = f'https://www.104.com.tw/jobs/search/?ro=0&jobcat=2007001022&kwop=7&keyword=%E6%95%B8%E6%93%9A%E5%B7%A5%E7%A8%8B&expansionType=area%2Cspec%2Ccom%2Cjob%2Cwf%2Cwktm&area=6001001000&order=12&asc=0&page={p}&mode=s&jobsource=index_s&langFlag=0&langStatus=0&recommendJob=1&hotJob=1'
        #url = f'https://www.104.com.tw/jobs/search/?ro=1&jobcat=2007001018%2C2007001021%2C2007001022%2C2007001012%2C2007001020&expansionType=area%2Cspec%2Ccom%2Cjob%2Cwf%2Cwktm&order=16&asc=0&page={p}&mode=s&jobsource=2018indexpoc&langFlag=0&langStatus=0&recommendJob=1&hotJob=1'
        
        # 發送 HTTP 請求
        response = requests.get(url, headers=HEADERS)

        # 使用 BeautifulSoup 解析網頁原始碼
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取職缺標題、公司名稱、工作地點、薪資等資訊
        job_title = soup.find_all(class_='js-job-link') 
        company_name = soup.find_all('ul', class_='b-list-inline b-clearfix') 
        
        date = soup.find_all('span', class_='b-tit__date') 
        date = date[3:] # 前三個空的
        
        location_experience_education = soup.find_all(class_='b-list-inline b-clearfix job-list-intro b-content') 
        
        salary_companyStandard = soup.find_all('div', class_='job-list-tag b-content') 
        salary_companyStandard = salary_companyStandard[2:] # 前兩個空的
        
        apply_count = soup.find_all('a', class_='b-link--gray gtm-list-apply') 
        
        for n in range(len(job_title)):
            
            jobTitle.append(job_title[n].text)
            applyCount.append(apply_count[n].text)
            onlineDate.append(date[n].text.strip())
            


            company_name_lst = [i for i in company_name[n].text.split('\n') if i.strip()!='']
            
            companyName.append(company_name_lst[0])
            try:
                trade.append(company_name_lst[1])
            except:
                trade.append('-')
            

            location_experience_education_lst = [i for i in location_experience_education[n].text.split('\n')]

            location.append(location_experience_education_lst[1])


            judge = ''.join(salary_companyStandard[n].text)

            lst = [i for i in salary_companyStandard[n].text.split('\n')]
            
            salary.append(lst[1])

            if '員工' in judge:

                index = [i for i, s in enumerate(lst) if '員工' in s]

                companyStandard.append(lst[index[0]])


            else:
                companyStandard.append('-')
                
            # change url and get job content / criteria
            driver.get('https:'+job_title[n]['href'])

            # job content and requirement and duty
            try:
                jobs_duty = driver.find_element(By.CSS_SELECTOR, '.category-item.col.p-0.job-description-table__data')
                jd = jobs_duty.text.replace('認識','')
                jd = jd.replace('職務','')
                jd = jd.replace('\n','')
                duty.append(jd)
            except:
                duty.append('-')
            
            try:
                jobs_con = driver.find_element(By.CSS_SELECTOR, "div[class^='job-description-table']")
                jc = jobs_con.text.replace('\n','')
                jobContent.append(jc)
            except:
                jobContent.append('-')
                
            try:
                jobs_req = driver.find_element(By.CSS_SELECTOR, '.job-requirement-table.row')
                jr = jobs_req.text.replace('\n','')
                jobCriteria.append(jr)
                
            except:
                jobCriteria.append('-')

    driver.close()
    
    df = pd.DataFrame()
    
    df['職稱']=jobTitle
    df['工作內容']=jobContent
    df['條件需求']=jobCriteria
    df['公司名稱']=companyName
    df['產業']=trade
    df['職務']=duty
    df['上架日期']=onlineDate
    df['工作地']=location
    df['薪資']=salary
    df['公司規模']=companyStandard
    df['應徵人數']=applyCount
    
    return df
                

# take input pages 2 for data engineer jobs as an example
jobs = webCrawl_104(2)
jobs