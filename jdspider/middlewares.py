# -*- coding: utf-8 -*-
# from jdspider.settings import IPPOOL
from jdspider.settings import UAPOOL
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
import random

class UAPOOLS(UserAgentMiddleware):

	def __init__(self, user_agent='Scrapy'):
		self.user_agent = user_agent
		print('this is my Useragentmiddleware')

	def process_request(self, request, spider):
		self.user_agent = random.choice(UAPOOL)
		print("User-agent:%s" % self.user_agent)
		request.headers['User-Agent'] = self.user_agent
		# request.headers.setdefault('User-Agent', self.ua)