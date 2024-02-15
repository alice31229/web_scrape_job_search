import requests 
import pandas as pd 
from bs4 import BeautifulSoup 


HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
             'cookie': 'over18=1;'}

def cakeresume_webCrawl(pages):

    job_title = []
    company_name = []
    job_description = []
    address = []
    money = []
    level = []
    chances = []
    updates = []
    experience = []
    management = []
    trade = []
    duty = []
    job_skill = []
    
    #URL = 'https://www.cakeresume.com/jobs?location_list%5B0%5D=Taiwan&job_type%5B0%5D=full_time'
    URL = 'https://www.cakeresume.com/jobs?location_list%5B0%5D=Taiwan&profession%5B0%5D=it_data-engineer'
    
    r = requests.get(URL, headers=HEADERS)
    r.encoding = 'utf-8' #轉換編碼至UTF-8
    soup = BeautifulSoup(r.text)

    jobTitle = soup.select("a[class='JobSearchItem_jobTitle__bu6yO']")
    companyName = soup.select("a[class='JobSearchItem_companyName__bY7JI']")
    jobDescription = soup.select("div[class='JobSearchItem_description__si5zg']")
    workcity = soup.select("div[class='JobSearchItem_featureSegments__ywEPs']")
    item = soup.select("div[class='JobSearchItem_features__hR3pk']") 

    for i in item:
        iii = i.find('div','InlineMessage_label__LJGjW')
        temp = iii.text.split('・') # 工作機會數, 全職兼職, 經驗需求
        chances.append(temp[0])
        level.append(temp[2])


    for i in range(len(jobTitle)):
        job_title.append(jobTitle[i].text)
        company_name.append(companyName[i].text)
        job_description.append(jobDescription[i].text)
        
        try:
            address.append(workcity[i*2+1].text)
        except:
            address.append('-')
        
            
        r = requests.get('https://www.cakeresume.com'+jobTitle[i]['href'], headers=HEADERS)
        r.encoding = 'utf-8' #轉換編碼至UTF-8
        soup = BeautifulSoup(r.text)

        items = soup.select("div[class='JobDescriptionRightColumn_row__5rklX']")
        updates_one = soup.find('div','InlineMessage_label__LJGjW')

        updates.append(updates_one.text)

        trade_duty = soup.select("span[class='Breadcrumbs_labelText__ZXeZH']")
        trade.append(trade_duty[3].text)
        duty.append(trade_duty[4].text)

        judge = ''
        for i in items:
            Text = i.text
            judge+=Text

            if 'TWD' in Text or 'NT' in Text or 'K+ null' in Text:
                money.append(Text)

            elif 'experience' in Text or '工作經驗' in Text:
                experience.append(Text)

            elif 'Managing' in Text or '管理' in Text:
                management.append(Text)

        if 'experience' not in judge and '工作經驗' not in judge:
            experience.append('-')

        if 'Managing' not in judge and '管理' not in judge:
            management.append('-')


        jobSkill = soup.select("div[class='RailsHtml_container__LlMcK']")
        job_skill.append(jobSkill[1].text)
        
    
    for p in range(2, pages+1):
        #url = f'https://www.cakeresume.com/jobs?location_list%5B0%5D=Taiwan&job_type%5B0%5D=full_time&page={p}'
        url = f'https://www.cakeresume.com/jobs?location_list%5B0%5D=Taiwan&profession%5B0%5D=it_data-engineer&page={p}'
        r = requests.get(url, headers=HEADERS)
        r.encoding = 'utf-8' #轉換編碼至UTF-8
        soup = BeautifulSoup(r.text)

        jobTitle = soup.select("a[class='JobSearchItem_jobTitle__bu6yO']")
        companyName = soup.select("a[class='JobSearchItem_companyName__bY7JI']")
        jobDescription = soup.select("div[class='JobSearchItem_description__si5zg']")
        workcity = soup.select("div[class='JobSearchItem_featureSegments__ywEPs']")
        item = soup.select("div[class='JobSearchItem_features__hR3pk']") 
    
        for i in item:
            iii = i.find('div','InlineMessage_label__LJGjW')
            temp = iii.text.split('・') # 工作機會數, 全職兼職, 經驗需求
            chances.append(temp[0])
            level.append(temp[2])


        for i in range(len(jobTitle)):
            job_title.append(jobTitle[i].text)
            company_name.append(companyName[i].text)
            job_description.append(jobDescription[i].text)
            
            try:
                address.append(workcity[i*2+1].text)
            except:
                address.append('-')



            r = requests.get('https://www.cakeresume.com'+jobTitle[i]['href'], headers=HEADERS)
            r.encoding = 'utf-8' #轉換編碼至UTF-8
            soup = BeautifulSoup(r.text)

            items = soup.select("div[class='JobDescriptionRightColumn_row__5rklX']")
            updates_one = soup.find('div','InlineMessage_label__LJGjW')

            updates.append(updates_one.text)

            trade_duty = soup.select("span[class='Breadcrumbs_labelText__ZXeZH']")
            trade.append(trade_duty[3].text)
            duty.append(trade_duty[4].text)

            judge = ''
            for i in items:
                Text = i.text
                judge += Text

                if 'TWD' in Text or 'NT' in Text or 'K+ null' in Text:
                    money.append(Text)

                elif 'experience' in Text or '工作經驗' in Text:
                    experience.append(Text)

                elif 'Managing' in Text or '管理' in Text:
                    management.append(Text)

            if 'experience' not in judge and '工作經驗' not in judge:
                experience.append('-')

            if 'Managing' not in judge and '管理' not in judge:
                management.append('-')


            jobSkill = soup.select("div[class='RailsHtml_container__LlMcK']")
            job_skill.append(jobSkill[1].text)
        
        
    
    jobs = pd.DataFrame()

    # 欄位： 職缺內容, 公司名稱, 地址, 薪資, 網址, 應徵人數
    jobs['職稱'] = job_title
    jobs['公司名稱'] = company_name
    jobs['職缺描述'] = job_description
    jobs['職缺需求'] = job_skill
    jobs['地址'] = address
    jobs['薪資'] = money
    jobs['所需人數'] = chances
    jobs['更新時間'] = updates
    jobs['職等'] = level
    jobs['工作經驗要求'] = experience
    jobs['管理責任要求'] = management
    jobs['產業'] = trade
    jobs['職務'] = duty

    
    jobs['職缺描述'] = jobs['職缺描述'].str.replace('\n', '')
    jobs['職缺需求'] = jobs['職缺需求'].str.replace('\n', '')
    
    return jobs

# 爬取 台灣 數據工程師 職缺
jobs = cakeresume_webCrawl(2)
jobs 
