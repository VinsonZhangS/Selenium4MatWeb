# -*- coding:utf-8 -*-
from selenium import webdriver
from time import sleep
from lxml import etree
from selenium.webdriver.common.by import By
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

if __name__ == "__main__":
    chrome_driver = "./driver/chromedriver.exe"
    url = 'https://www.matweb.com/search/CompositionSearch.aspx'
    bro = webdriver.Chrome(
        executable_path = chrome_driver
    )
    bro.get(url = url)
    sleep(30)
    #进入查询界面：
    button_plus = bro.find_element(by = By.XPATH, value ='//*[@id="ctl00_ContentMain_ucMatGroupTree_LODCS1_msTreeViewn5"]/img')
    button_plus.click()
    sleep(30)
    #点击titanium缩小搜索范围
    button_search_alloy = bro.find_element(by = By.XPATH, value ='//*[@id="ctl00_ContentMain_ucMatGroupTree_LODCS1_msTreeViewt21"]')
    button_search_alloy.click()
    sleep(30)
    #点击查询
    find_button = bro.find_element(by=By.XPATH, value='//*[@id="ctl00_ContentMain_btnSubmit"]')
    find_button.click()
    sleep(30)
    #获取所有页面数据
    all_pages_list = []
    for i in range(9):
        page_text = bro.page_source
        all_pages_list.append(page_text)
        next_page_button = bro.find_element(by=By.XPATH, value='//*[@id="ctl00_ContentMain_UcSearchResults1_lnkNextPage"]')
        next_page_button.click()
        sleep(30)
    #获取所有合金的url
    all_alloy_urls_list = []
    for page_text in all_pages_list:
        tree = etree.HTML(page_text)
        tr_list = tree.xpath('//*[@id="tblResults"]/tbody/tr[@onmouseout="matweb.DataRow_OnMouseOut(this)"]')
        for tr in tr_list:
            detail_url = 'https://www.matweb.com' + tr.xpath('./td[@style="width:auto; font-weight:bold;"]/a/@href')[0]
            all_alloy_urls_list.append(detail_url)
    sleep(30)
    #获取所有数据：
    all_titanium_dic = {}
    count = 0
    for alloy_url in all_alloy_urls_list:
        count += 1
        bro.get(url = alloy_url)
        sleep(30)
        detail_page_text = bro.page_source
        tree = etree.HTML(detail_page_text)
        alloy_name = (
            tree.xpath('//*[@id="ctl00_ContentMain_ucDataSheet1_pnlMaterialData"]/table[1]/tbody/tr[1]/th/text()')[
                0]).strip(
            '\n      \n      \n      \n    ')
        altrow_datarowSeparator_list = tree.xpath(
            '//*[@id="ctl00_ContentMain_ucDataSheet1_pnlMaterialData"]/table[2]/tbody/tr[@class="altrow datarowSeparator"]')
        datarowSeparator_list = tree.xpath(
            '//*[@id="ctl00_ContentMain_ucDataSheet1_pnlMaterialData"]/table[2]/tbody/tr[@class=" datarowSeparator"]')
        altrow_list = tree.xpath(
            '//*[@id="ctl00_ContentMain_ucDataSheet1_pnlMaterialData"]/table[2]/tbody/tr[@class="altrow"]')
        tr_list.extend(altrow_datarowSeparator_list)
        tr_list.extend(datarowSeparator_list)
        tr_list.extend(altrow_list)
        temp_dic = {}
        alloy_dic = {}
        for tr in tr_list:
            property = tr.xpath('./td[1]//text()')[0].strip('\xa0')
            metric = tr.xpath('./td[2]//text()')
            metric = ''.join(metric)
            temp_dic[property] = metric
        for a in temp_dic:
            if a != '':
                alloy_dic[a] = temp_dic[a]
        all_titanium_dic[alloy_name] = alloy_dic
        print("Alloy {} Finished!".format(count))
        sleep(30)

    fp = open("./20220406.json", 'w', encoding='utf-8')
    json.dump(all_titanium_dic, fp)
    print("All Crawler Work Done!")