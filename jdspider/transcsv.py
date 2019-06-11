# -*- coding: utf-8 -*-

import csv, json, os, codecs


def trans(path):
	jsonData = codecs.open(path, 'r', 'utf-8')
	csvfile = open('jdgoods.csv', 'w',newline='')
	writer = csv.writer(csvfile)
	goodsinfolist = json.load(jsonData)
	jsonData.close()
	flag = True
	for goodinfo in goodsinfolist:
		if flag:
			keys = list(goodinfo.keys())
			writer.writerow(keys)
			flag = False
		writer.writerow(list(goodinfo.values()))
	csvfile.close()

if __name__ == '__main__':
	path = os.path.abspath('goodsinfo.json')
	trans(path)