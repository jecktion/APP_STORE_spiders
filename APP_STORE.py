# -*- coding: utf-8 -*-
# 此程序用来抓取 的数据
import hashlib
import os

import requests
import time
import random
import re
from multiprocessing.dummy import Pool
import csv
import json
import sys


class Spider(object):
	# def __init__(self):
		# self.date = '2000-01-01'
	
	def get_headers(self):
		user_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0',
		               'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0',
		               'IBM WebExplorer /v0.94', 'Galaxy/1.0 [en] (Mac OS X 10.5.6; U; en)',
		               'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
		               'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
		               'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)',
		               'Opera/9.52 (Windows NT 5.0; U; en)',
		               'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.2pre) Gecko/2008071405 GranParadiso/3.0.2pre',
		               'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.458.0 Safari/534.3',
		               'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.0 (KHTML, like Gecko) Chrome/4.0.211.4 Safari/532.0',
		               'Opera/9.80 (Windows NT 5.1; U; ru) Presto/2.7.39 Version/11.00']
		user_agent = random.choice(user_agents)
		headers = {'Host': 'www.shilladfs.com', 'Connection': 'keep-alive',
		           'User-Agent': user_agent,
		           'Referer': 'http://www.shilladfs.com/estore/kr/zh/Skin-Care/Basic-Skin-Care/Pack-Mask-Pack/p/3325351',
		           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		           'Accept-Encoding': 'gzip, deflate, br',
		           'Accept-Language': 'zh-CN,zh;q=0.8'
		           }
		return headers
	
	def p_time(self, stmp):  # 将时间戳转化为时间
		stmp = float(str(stmp)[:10])
		timeArray = time.localtime(stmp)
		otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
		return otherStyleTime
	
	def replace(self, x):
		# 将其余标签剔除
		removeExtraTag = re.compile('<.*?>', re.S)
		x = re.sub(removeExtraTag, "", x)
		x = re.sub(re.compile('[\n\r]'), '  ', x)
		x = re.sub(re.compile('\s{2,}'), '  ', x)
		x = re.sub('=', '  ', x)
		return x.strip()
	
	def GetProxies(self):
		# 代理服务器
		proxyHost = "http-dyn.abuyun.com"
		proxyPort = "9020"
		# 代理隧道验证信息
		proxyUser = "HI18001I69T86X6D"
		proxyPass = "D74721661025B57D"
		proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
			"host": proxyHost,
			"port": proxyPort,
			"user": proxyUser,
			"pass": proxyPass,
		}
		proxies = {
			"http": proxyMeta,
			"https": proxyMeta,
		}
		return proxies
	
	def get_comments(self, game_id, product_number, plat_number):  # 获取新版的数据
		page = 0
		while 1:
			print 'page:',page
			url = 'https://itunes.apple.com/WebObjects/MZStore.woa/wa/userReviewsRow?cc=us&id=' + game_id + '&displayable-kind=11&startIndex=' + str(
				10000 * page) + '&endIndex=' + str(10000 * (page + 1)) + '&sort=0&appVersion=all'
			headers = {
				'User-Agent': 'iTunes/11.0 (Windows; Microsoft Windows 7 Business Edition Service Pack 1 (Build 7601)) AppleWebKit/536.27.1',
			}
			results = []
			retry = 10
			while 1:
				try:
					text = requests.get(url, headers=headers, proxies=self.GetProxies(), timeout=100).text
					items = json.loads(text, strict=False)['userReviewList']
					print len(items)
					break
				except Exception as e:
					retry -= 1
					if retry == 0:
						print e
						return None
					else:
						continue
			if len(items) == 0 and page == 0:
				page = 1
				continue
			last_modify_date = self.p_time(time.time())
			for item in items:
				try:
					rate = str(item['rating'])
				except:
					rate = ''
				comments = self.replace(item['body'].replace('=', ''))
				nick_name = self.replace(item['name'].replace('=', ''))
				cmt_time = item['date'].replace('T', ' ').replace('Z', '')
				cmt_date = cmt_time.split()[0]
				# if cmt_date < self.date:
				# 	continue
				like_cnt = '0'
				cmt_reply_cnt = '0'
				long_comment = '0'
				src_url = 'https://itunes.apple.com/WebObjects/MZStore.woa/wa/userReviewsRow'
				tmp = [product_number, plat_number, nick_name, cmt_date, cmt_time, comments, like_cnt,
				       cmt_reply_cnt, long_comment, last_modify_date, src_url]
				print '|'.join(tmp)
				results.append([x.encode('gbk', 'ignore') for x in tmp])
			if len(results) == 0:
				return None
			else:
				with open('data_comments_4.csv', 'a') as f:
					writer = csv.writer(f, lineterminator='\n')
					writer.writerows(results)
				page += 1


if __name__ == "__main__":
	spider = Spider()
	s1 = []
	with open('data.csv') as f:
		tmp = csv.reader(f)
		for i in tmp:
			if 'ID' not in i[2] and len(i[2]) > 0:
				s1.append([i[2], i[0], 'P25'])
	for j in s1:
		print j[1],j[0]
		if j[1] in ['F0000177']:
			spider.get_comments(j[0], j[1], j[2])

