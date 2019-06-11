# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class GoodsItem(scrapy.Item):
    goods_id = scrapy.Field()
    goods_brand_id = scrapy.Field()
    goods_brand_name = scrapy.Field()
    goods_name = scrapy.Field()
    goods_price = scrapy.Field()
    goods_image_url = scrapy.Field()
    goods_ad = scrapy.Field()
    goods_promotion = scrapy.Field()
    goods_p_price = scrapy.Field()
    goods_discount_quote = scrapy.Field()
    goods_discount = scrapy.Field()
    venderid = scrapy.Field()
    gifts = scrapy.Field()
    goods_image_path = scrapy.Field()
