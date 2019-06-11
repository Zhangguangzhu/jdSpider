# -*- coding: utf-8 -*-
import random

import scrapy
import time
from scrapy.http import Request
from jdspider.items import GoodsItem
import re, json, random, urllib.request

#jd 查询价格的url
price_url = 'https://p.3.cn/prices/mgets?callback=jQuery&pduid=15107168479481209303158&skuIds=J_'
#jd 查询促销信息的url
promotion_url = 'https://cd.jd.com/promotion/v2?'
#地址
area = '1_72_55682_0'
#查询种类
cat = '670,677,679'

class VcSpider(scrapy.Spider):
	name = "vc"
	# allowed_domains = ["www.jd.com"]
	start_urls = (
		'https://list.jd.com/list.html?cat=%s&delivery=1&page=1' % cat,
	)

	def parse(self, response):
		#爬取主界面的商品名称id厂家信息
		brand_list = response.css('#plist .j-sku-item:nth-child(1)::attr(brand_id)').extract()
		venderid_list = response.css('#plist .j-sku-item:nth-child(1)::attr(venderid)').extract()
		goods_name_list = response.css('#plist .j-sku-item:nth-child(1) .p-name em::text').extract()
		goods_id_list = response.css('div#plist .j-sku-item:nth-child(1)::attr(data-sku)').extract()
		# goods_image_url_list = [ re.findall(r'//(.*)\"',tag)[0] for tag in response.css('#plist .j-sku-item:nth-child(1) .p-img img:').extract() ]
		goods_image_url_list = response.css('#plist .j-sku-item:nth-child(1) .p-img img').extract()
		for index, url in enumerate(goods_image_url_list):
			goods_image_url_list[index] = re.findall(r'//(.*)\"', url)[0]

		for goods_name, goods_brand, goods_vender, goods_id, goods_image_url in zip(goods_name_list,brand_list,venderid_list,goods_id_list, goods_image_url_list):
			goodsinfo = GoodsItem()
			goodsinfo['goods_brand_id'] = goods_brand
			goodsinfo['goods_name'] = goods_name.strip()
			goodsinfo['venderid'] = goods_vender
			goodsinfo['goods_id'] = goods_id.strip()
			goodsinfo['goods_image_url'] = "https://" + goods_image_url
			request_price_url = price_url + goods_id
			if int(goodsinfo['venderid']) >= 1000000000:
				yield Request(url=request_price_url, meta={'goodsinfo': goodsinfo} , callback=self.parse_goods_price)
				time.sleep(1)
		if response.css('.page.clearfix .p-num .pn-next'):
			nextpagenum = int(re.findall(r'page=(.)',response.url)[0]) + 1
			nextpageurl = 'https://list.jd.com/list.html?cat=670,677,679&delivery=1&page=' + str(nextpagenum)
			yield Request(nextpageurl,callback=self.parse)


	def parse_goods_price(self, response):
		#爬取具体商品的价格包含普通价格与会员价格
		price_json_str = re.findall(r'jQuery\(\[(.*)\]\)', response.text)[0]
		goods_price_dict = json.loads(price_json_str)
		goodsinfo = response.meta.get('goodsinfo')

		if "p" in goods_price_dict:
			goodsinfo['goods_price'] = goods_price_dict['p']
		if "tpp" in goods_price_dict:
			goodsinfo['goods_p_price'] = goods_price_dict['tpp']
		else:
			goodsinfo['goods_p_price'] = goods_price_dict['p']
		#不在头部添加referer会被重定向到error界面
		referer = "https://item.jd.com/%s.html" % goodsinfo["goods_id"]
		query = 'callback=jQuery&skuId=%s&area=%s&venderId=%s&cat=%s' % (goodsinfo['goods_id'], area, goodsinfo['venderid'], cat)
		# request_promotion_url = urllib.request.urljoin(promotion_url, query)
		request_promotion_url = promotion_url + query
		if float(goodsinfo['goods_price']) >= 0:
			yield Request(url=request_promotion_url, headers={"Referer": referer},meta={'goodsinfo':goodsinfo}, callback=self.parse_goods_promotion)

	def parse_goods_promotion(self, response):
		#查询促销信息
		try:
			query_promotion_str = response.text.encode(response.encoding).decode('gbk')
		except Exception as e:
			query_promotion_str = response.text.encode(response.encoding).decode('gb18030')

		promotion_json_str = re.findall(r'jQuery\((.*)\)', query_promotion_str)[0]
		# print(type(promotion_json_str),len(promotion_json_str), promotion_json_str)
		promotion = json.loads(promotion_json_str)
		goodsinfo = response.meta.get('goodsinfo')
		goodsinfo['goods_ad'] = re.sub(r'<a.*a>','',promotion['ads'][0]['ad'])
		if promotion['prom']['pickOneTag']:
			goodsinfo['goods_promotion'] = promotion['prom']['pickOneTag'][0]['content']
		else:
			goodsinfo['goods_promotion'] = None
		if promotion['skuCoupon']:
			goodsinfo['goods_discount'] = promotion['skuCoupon'][0]['discount']
			goodsinfo['goods_discount_quote'] = promotion['skuCoupon'][0]['quota']
		else:
			goodsinfo['goods_discount'] = 0
			goodsinfo['goods_discount_quote'] = 0
		if promotion['prom']['tags']:
			if 'gifts' in promotion['prom']['tags'][0]:
				goodsinfo['gifts'] = promotion['prom']['tags'][0]['gifts'][0]['nm']
			else:
				goodsinfo['gifts'] = None
		else:
			goodsinfo['gifts'] = None
		yield goodsinfo
