# -*- coding: utf-8 -*-
# 此程序用来抓取 的数据
import os

import csv
import json
import sys
from save_data import database


class Spider(object):
	def __init__(self):
		self.db = database()
	
	def get_data(self):  # 获取数据
		results = []
		paths = os.listdir(os.getcwd())
		for path in paths:
			if 'new_data_comment.csv' in path:
				with open(path, 'rU') as f:
					tmp = csv.reader(f)
					for i in tmp:
						# print 'i:',i
						t = [x.decode('gbk', 'ignore') for x in i]
						# print 't:',t
						if len(t) == 11:
							dict_item = {'product_number': t[0],
										 'plat_number': t[1],
										 'nick_name': t[2],
										 'cmt_date': t[3],
										 'cmt_time': t[4],
										 'comments': t[5],
										 'like_cnt': t[6],
										 'cmt_reply_cnt': t[7],
										 'long_comment': t[8],
										 'last_modify_date': t[9],
										 'src_url': t[10]}
							results.append(dict_item)
						else:
							print '少字段>>>t:',t
		return results
	
	def save_sql(self, table_name):  # 保存到sql
		items = self.get_data()
		all = len(items)
		count = 1
		for item in items:
			try:
				print 'count:%d | all:%d' % (count, all)
				count += 1
				self.db.up_data(table_name, item)
			except Exception as e:
				print '插入数据库错误>>>',e
				pass


if __name__ == "__main__":
	spider = Spider()
	spider = Spider()
	print u'开始录入数据'
	spider.save_sql('T_COMMENTS_PUB') # 手动输入库名
	print u'录入完毕'
	spider.db.db.close()
