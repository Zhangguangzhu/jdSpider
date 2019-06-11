# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request
import codecs, json
from sqlalchemy import Column, String, create_engine, Table, Integer, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from scrapy.exporters import JsonItemExporter
import pymysql, os, logging
from jdspider.settings import MYSQL_HOST, MYSQL_DBNAME, MYSQL_USER, MYSQL_PASSWD


class JdspiderPipeline(object):
	def process_item(self, item, spider):
		return item


class GoodsImagePipeline(ImagesPipeline):

	def get_media_requests(self, item, info):
		if "goods_image_url" in item:
			yield Request(item['goods_image_url'], headers={'Referer':'https://list.jd.com/list.html?cat=670,677,681'})

	def item_completed(self, results, item, info):
		for status, values in results:
			item['goods_image_path'] = values['path']
		return item

class JsonWithEncodeingPipeline(object):

	def __init__(self):
		self.file = open('goodsinfo.json', 'wb')
		self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False,sort_keys=True)
		self.exporter.start_exporting()

	def close_spider(self, spider):
		self.exporter.finish_exporting()
		self.file.close()

	def process_item(self, item, spider):
		self.exporter.export_item(item)
		return item

class DBPipeline(object):

	def __init__(self):
		self.conn = pymysql.connect(host=MYSQL_HOST,user=MYSQL_USER,passwd=MYSQL_PASSWD,db=MYSQL_DBNAME, charset="utf8")
		self.cursor = self.conn.cursor()

	def process_item(self, item, spider):
		goods_id = item['goods_id']
		brands_id = item['goods_brand_id']
		# goods_brand_name = item['goods_brand_name']
		goods_name = item['goods_name']
		goods_price = item['goods_price']
		goods_ad = item['goods_ad']
		goods_promotion = item['goods_promotion']
		goods_p_price = item['goods_p_price']
		goods_discount_quote = item['goods_discount_quote']
		goods_discount = item['goods_discount']
		goods_image_path = item['goods_image_path']
		# goods_image = pymysql.Binary(self.get_image(goods_image_path))
		# goods_image = b''
		gifts = item['gifts']
		if goods_promotion:
			goods_promotion = pymysql.escape_string(goods_promotion)
		insert_sql = "insert into jdgoods value ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (goods_id,
																											 pymysql.escape_string(goods_name),
																											 brands_id,
																											 goods_price,
																											 pymysql.escape_string(goods_ad),
																											 goods_promotion,
																											 goods_p_price,
																											 goods_discount,
																											 goods_discount_quote,
																											 gifts,goods_image_path)
		query_sql = "select goods_id from jdgoods where goods_id = %s" % (goods_id)
		update_sql = "update jdgoods set goods_price='%s',goods_p_price='%s',goods_discount='%s',goods_discount_quote='%s',goods_ad='%s',goods_promotion='%s' where goods_id='%s'" % (goods_price,
																																								  goods_p_price,
																																								  goods_discount,
																																								  goods_discount_quote,
																																								  pymysql.escape_string(goods_ad),
																																								  goods_promotion,
																																													  goods_id)
		try:
			res = self.cursor.execute(query_sql)
			if not res:
				self.cursor.execute(insert_sql)
			else:
				self.cursor.execute(update_sql)
			self.conn.commit()
		except Exception as error:
			logging.error(error)
			self.conn.rollback()
		return item

	def get_image(self, goods_image_path):
		image_par_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),"image")
		# image_abs_path = os.path.join(image_par_path, goods_image_path)
		# with open(image_abs_path, 'rb') as f:
		#     img = f.read()
		return image_par_path

	def close_spider(self, spider):
		self.conn.close()

class SqlalchemyDBPileline(object):

	def __init__(self):
		self.engine = create_engine('mysql+mysqldb://%s:%s@localhost:3306/%s?charset=utf8' % (MYSQL_USER, MYSQL_PASSWD, MYSQL_DBNAME))
		self.Base = declarative_base()

		class Jdgoods(self.Base):
			__tablename__ = 'jdgoods'
			goods_id = Column(String(15), primary_key=True)
			goods_name = Column(String(100))
			brands_id = Column(String(15))
			goods_price = Column(Float(8,2))
			goods_ad = Column(String(300))
			goods_promotion = Column(String(100))
			goods_p_price = Column(Float(8,2))
			goods_discount = Column(Float(7,2))
			goods_discount_quote = Column(Float(7,2))
			gifts = Column(String(100))
			goods_image_path = Column(String(100))

		self.Jdgoods = Jdgoods
		self.Base.metadata.create_all(self.engine)
		DBsession = sessionmaker(bind=self.engine)
		self.session = DBsession()

	def process_item(self, item, spider):
		goodsinfo = self.session.query(self.Jdgoods).filter_by(goods_id=item['goods_id']).first()
		try:
			if not goodsinfo:
				goodsinfo = self.Jdgoods(goods_id=item['goods_id'], goods_name=item['goods_name'], brands_id=item['brands_id'],
									goods_price=item['goods_price'], goods_ad=item['goods_ad'], goods_promotion=item['goods_promotion'],
									goods_p_price=item['goods_p_price'],goods_discount=item['goods_discount'],goods_discount_quote=item['goods_discount_quote'],
									gifts=item['gifts'],goods_image_path=item['goods_image_path'])
				self.session.add(goodsinfo)
			else:
				goodsinfo.goods_price = item['goods_price']
				goodsinfo.goods_ad = item['goods_ad']
				goodsinfo.goods_promotion = item['goods_promotion']
				goodsinfo.goods_p_price = item['goods_p_price']
				goodsinfo.goods_discount = item['goods_discount']
				goodsinfo.goods_discount_quote = item['goods_discount_quote']
				goodsinfo.gifts = item['gifts']
			self.session.commit()
		except Exception as e:
			print(e)
			self.session.rollback()
		return item

	def close_spider(self, spider):
		self.session.close()