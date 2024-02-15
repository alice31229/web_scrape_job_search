import re
import json
import html
import datetime 
import requests
import pandas as pd 
import urllib.request
from bs4 import BeautifulSoup


HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
             'cookie': 'over18=1;'}

# 爬取 個別職缺頁面 工作內容 條件要求
def get_job_detail(url_jobID): 

    r = requests.get(url_jobID, headers=HEADERS)
    r.encoding = 'utf-8' #轉換編碼至UTF-8
    soup = BeautifulSoup(r.text)
    
    # 工作內容 條件要求 
    judge = soup.select("div[class='w-full normal:w-auto min-w-0 flex flex-col gap-4 normal:gap-8 flex-[3_1_0%] job__content']")

    # 找 工作內容
    try:
        job_content_title = judge[0].find(string=re.compile("工作內容"))
        job_content_title = job_content_title.parent
        jobContent = job_content_title.find_next_sibling()
        jobContent = jobContent.text
        jobContent = jobContent.replace('\n', '')

    except:
        jobContent = '-'


    # 找 條件要求
    try:
        job_requirement_title = judge[0].find(string=re.compile("條件要求"))
        job_requirement_title = job_requirement_title.parent
        jobRequirement = job_requirement_title.find_next_sibling()
        jobRequirement = jobRequirement.text
        jobRequirement = jobRequirement.replace('\n', '')

    except:
        jobRequirement = '-'
        
    
    # 工作內容 條件要求 遠端型態 加分條件 員工福利 薪資範圍
        
    return jobContent, jobRequirement


# 職缺列表 各職缺 
def webCrawl_Yourator(pages):

    # columns
    job_title = []
    company_name = []
    address = []
    money = []
    job_content = []
    job_requirement = []
    tags = []

    url_page = f'https://www.yourator.co/api/v4/jobs?category[]=%E8%B3%87%E6%96%99%E5%B7%A5%E7%A8%8B%20%2F%20%E6%A9%9F%E5%99%A8%E5%AD%B8%E7%BF%92&page=1&sort=recent_updated'
    #url_page = f'https://www.yourator.co/api/v2/jobs?position[]=full_time&sort=recent_updated'
    r = urllib.request.Request(url_page, headers=HEADERS)
    r = urllib.request.urlopen(r)

    soup = BeautifulSoup(r, 'html.parser')
    data = json.loads(str(soup))

    for j in data['payload']['jobs']:
        job_title.append(j['name'])
        company_name.append(j['company']['brand'])
        address.append(j['location'])
        money.append(j['salary'])
        temp = j['tags']

        if temp != []:
            temp = ', '.join(temp)
        else:
            temp = '-'

        tags.append(temp)

        jobDetail_url = 'https://www.yourator.co'+j['path']
        
        Con, Req =  get_job_detail(jobDetail_url)
        job_content.append(Con)
        job_requirement.append(Req) 

        
    for p in range(2,pages):
        
        url_page = f'https://www.yourator.co/api/v4/jobs?category[]=%E8%B3%87%E6%96%99%E5%B7%A5%E7%A8%8B%20%2F%20%E6%A9%9F%E5%99%A8%E5%AD%B8%E7%BF%92&page=1&sort=recent_updated&page={p}'
        #url_page = f'https://www.yourator.co/api/v2/jobs?position[]=full_time&sort=recent_updated&page={p}'
        r = urllib.request.Request(url_page, headers=HEADERS) 
        r = urllib.request.urlopen(r)

        soup = BeautifulSoup(r, 'html.parser')
        data = json.loads(str(soup))
        
        if data['payload']['nextPage'] != None: 

            for j in data['payload']['jobs']:
                job_title.append(j['name'])
                company_name.append(j['company']['brand'])
                address.append(j['location'])
                money.append(j['salary'])
                temp = j['tags']

                if temp!=[]:
                    temp = ', '.join(temp)
                else:
                    temp='-'

                tags.append(temp)

                jobDetail_url = 'https://www.yourator.co'+j['path']

                Con, Req =  get_job_detail(jobDetail_url)
                
                job_content.append(Con)
                job_requirement.append(Req) 
                
                
        else:
            break

    final_df = pd.DataFrame()

    final_df['職缺名稱'] = job_title
    final_df['公司名稱'] = company_name
    final_df['工作內容'] = job_content
    final_df['條件要求'] = job_requirement
    final_df['工作地'] = address
    final_df['薪資'] = money
    final_df['標籤'] = tags

    return final_df

# 爬取 職缺類別為 資料工程/機器學習 的職缺
jobs = webCrawl_Yourator(3)
jobs