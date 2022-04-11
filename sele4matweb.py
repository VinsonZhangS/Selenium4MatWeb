# -*- coding:utf-8 -*-

from time import sleep
import json
import os
from lxml import etree
from selenium.webdriver.common.by import By
from selenium import webdriver


class Selenium4MatWeb:
	def __init__(self, url_save_path, data_save_path, if_save, num_page):
		self.save_data = if_save['data']
		self.url_save_path = url_save_path
		self.data_save_path = data_save_path
		self.pages = num_page
		self.all_titanium_dic = {}
		self.save_urls = if_save['urls']
		self.chrome_options = webdriver.ChromeOptions()
		# chrome_options.add_argument('--proxy-server=http://' + proxy)
		# chrome_options.add_argument('--headless')
		self.chrome_options.add_argument('--disable-gpu')
		self.chrome_options.add_argument(
			'user-agent="User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)"'
		)
		self.chrome_driver = "./driver/chromedriver.exe"
		self.init_url = 'https://www.matweb.com/search/CompositionSearch.aspx'
		self.bro = webdriver.Chrome(
			executable_path=self.chrome_driver, chrome_options=self.chrome_options
		)
		self.bro.get(url=self.init_url)

	# 获取所有页面数据
	def get_all_pages(
			self, plus_button='//*[@id="ctl00_ContentMain_ucMatGroupTree_LODCS1_msTreeViewn5"]/img',
			search_button='//*[@id="ctl00_ContentMain_ucMatGroupTree_LODCS1_msTreeViewt21"]',
			find_button='//*[@id="ctl00_ContentMain_btnSubmit"]'
	):
		# 点击加号进一步缩小范围
		button_plus = self.bro.find_element(by=By.XPATH, value=plus_button)
		button_plus.click()
		print('Press Button Plus Done!')
		sleep(30)
		# 点击titanium缩小搜索范围
		button_search_alloy = self.bro.find_element(by=By.XPATH, value=search_button)
		button_search_alloy.click()
		sleep(30)
		print('Press Button "Titanium" Done!')
		# 点击查询
		button_find = self.bro.find_element(by=By.XPATH, value=find_button)
		button_find.click()
		sleep(30)
		print("Submit the Query Done!")
		all_page_text_list = []
		for i in range(self.pages):
			page_text = self.bro.page_source
			all_page_text_list.append(page_text)
			next_page_button = self.bro.find_element(
				by=By.XPATH, value='//*[@id="ctl00_ContentMain_UcSearchResults1_lnkNextPage"]'
			)
			next_page_button.click()
			sleep(30)
		print("Get All Pages Done!")
		return all_page_text_list

	# 获取所有合金的url
	def get_all_url(self):
		all_alloy_urls = []
		for page_text in self.get_all_pages():
			tree = etree.HTML(page_text)
			tr_list = tree.xpath('//*[@id="tblResults"]/tbody/tr[@onmouseout="matweb.DataRow_OnMouseOut(this)"]')
			for tr in tr_list:
				detail_url = 'https://www.matweb.com' + tr.xpath('./td[@style="width:auto; font-weight:bold;"]/a/@href')[0]
				all_alloy_urls.append(detail_url)
		sleep(30)
		print("Get All Urls Done!")
		# 将所有url进行持久化存储
		if self.save_urls:
			with open(self.url_save_path, 'w', encoding='utf-8') as url_path:
				for alloy_url in all_alloy_urls:
					url_path.write(alloy_url)
					url_path.write('\t')
				print('Save as Text Done!')
		return all_alloy_urls

	# 获取所有数据：
	@property
	def get_all_data(self):
		count = 0
		for alloy_url in self.get_all_url():
			tr_list = []
			self.bro.get(url=alloy_url)
			sleep(30)
			detail_page_text = self.bro.page_source
			tree = etree.HTML(detail_page_text)
			alloy_name = (
				tree.xpath('//*[@id="ctl00_ContentMain_ucDataSheet1_pnlMaterialData"]/table[1]//tr[1]/th/text()')[
					0]).strip(
				'\n      \n      \n      \n    '
			)
			altrow_datarowSeparator_list = tree.xpath(
				'//*[@id="ctl00_ContentMain_ucDataSheet1_pnlMaterialData"]/table[2]//tr[@class="altrow datarowSeparator"]'
			)
			datarowSeparator_list = tree.xpath(
				'//*[@id="ctl00_ContentMain_ucDataSheet1_pnlMaterialData"]/table[2]//tr[@class=" datarowSeparator"]'
			)
			altrow_list = tree.xpath(
				'//*[@id="ctl00_ContentMain_ucDataSheet1_pnlMaterialData"]/table[2]//tr[@class="altrow"]'
			)
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
			self.all_titanium_dic[alloy_name] = alloy_dic
			print("Alloy {} Finished!".format(count))
			count += 1
			sleep(30)
		if self.save_data:
			alloy_path = open(self.data_save_path, 'w', encoding='utf-8')
			json.dump(self.all_titanium_dic, alloy_path)
		return self.all_titanium_dic


if __name__ == "__main__":
	url_file_path = './urls/titanium_alloy.txt'
	data_file_path = '../data/data.json'
	save = {
		'data': True,
		'urls': False
	}
	if os.path.exists(url_file_path):
		print("You already have all_alloy_urls_list.")
		fp = open(url_file_path, 'r', encoding='utf-8')
		temp_list = fp.readline()
		all_alloy_urls_list = temp_list.split('\t')
		del all_alloy_urls_list[-1]
		save['urls'] = False
	else:
		save['urls'] = True

	data = Selenium4MatWeb(url_file_path, data_file_path, save, 9)
	all_titanium_dic = data.get_all_data
