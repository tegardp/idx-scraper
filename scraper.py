import json
import os
import sys
import requests
import pandas as pd
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.support.ui import Select

def get_company_list():
    url = 'https://idx.co.id/perusahaan-tercatat/laporan-keuangan-dan-tahunan/'
    browser = webdriver.Chrome('chromedriver')
    browser.get(url)

    select = Select(browser.find_element_by_xpath('//*[@id="emitenList"]'))
    options = select.options
    company_list = []
    
    for option in options:
        company_list.append(option.get_attribute("value"))
    
    return company_list

def get_response(year,quarter,company):
    IDX_API = f"https://idx.co.id/umbraco/Surface/ListedCompany/GetFinancialReport?indexFrom=0&pageSize=10&year={year}&reportType=rdf&periode={quarter}&kodeEmiten={company}"
    response = requests.get(IDX_API)
    data = response.json()
    
    return data

def download_file(company, url):
    cwd = os.path.dirname(os.path.realpath(__file__))
    r = requests.get(url, allow_redirects=True)

    if url.find('/'):
        filename = company +' - '
        filename += url.rsplit('/', 1)[1]

    filename = os.path.join(cwd,'download', filename)
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb+") as f:
        f.write(r.content)

def company_status(d):
    df = pd.DataFrame.from_dict(d)
    df.to_csv('status perusahaan.csv')

def check_file_exist():
    cwd = os.path.dirname(os.path.realpath(__file__))
    cf = os.path.join(cwd, 'status perusahaan.csv')
    return os.path.exists(cf)


def main():
    year = '<tahun>'
    quarter = '<tw1/tw2/tw3/tahunan>'
    try:
        year = sys.argv[1]
        quarter = sys.argv[2]

        list_lk_name = ['lk ',' lk ', '_lk', 'lk_', '_lk_', 'laporan keuangan', 'laporan_keuangan', 'lap keu', 'lk-', '-lk', 'lap_keu', '3103', '31 maret', '31maret', '3006', '30 maret', '30maret', '3009', '30september', '30 september', 'audit', 'pt', 'tbk']
        company_list = []
        company_done = {}
        temp_name = []
        temp_status = []

        if(check_file_exist()):
            df = pd.read_csv('status perusahaan.csv')
            df = df[df['status']==False]
            company_list =  df['company'].to_numpy()
        else:
            company_list = get_company_list()
        
        for company in tqdm(company_list):
            status = False
            temp_name.append(company)
            data = get_response(year, quarter, company)
            
            if (len(data['Results']) > 0):
                list_attachment = data['Results'][0]['Attachments']
                for item in list_attachment:
                    file_name = item['File_Name'].lower()
                    if(any(check in file_name for check in list_lk_name)):
                        download_file(company, item['File_Path'])
                        status = True
            temp_status.append(status)
            
            company_done = {'company': temp_name, 'status': temp_status}
            company_status(company_done)
    except:
        print(f'Jalankan script dengan cara: scraper.py {year} {quarter}')

    
    
                


main()
