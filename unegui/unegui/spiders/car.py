import pymongo
from scrapy import Spider, Request
from scrapy.http import HtmlResponse, Response
from scrapy.selector import Selector

from unegui.items import AdItem

contains = 'contains({class}, "{class}")'

class CarSpider(Spider):
    name = "car"
    allowed_domains = ["www.unegui.mn"]
    start_urls = []

    def __init__(self):
        myclient = pymongo.MongoClient("mongodb://192.168.1.10:37017")
        mydb = myclient["unegui"]
        mycol = mydb["categories"]
        for category in mycol.find():
            self.start_urls.append(category['url'])

    def parse(self, response: HtmlResponse):
        category = response.url.rstrip('/').split("/")[-1]
        paginition = response.xpath('//ul[@class="number-list"]/li/a/text()').getall()       
        if not paginition:
            last_page = 1
        else:
            last_page = int(paginition[-1])
        for n in range(1, last_page+1):
            yield(Request(response.url.rstrip('/') + "/?page=" + str(n), self.parse_page, meta={"category": category}))

    def parse_page(self, response: HtmlResponse):
        ads = Selector(response).xpath('//div[contains(@class, "advert js-item-listing")]')
        for ad in ads:
            link = "https://www.unegui.mn/" + ad.xpath('*/*/a[@class="advert__content-title"]/@href').extract()[0]
            yield(Request(link,callback=self.parse_ad, meta={"category": response.meta.get("category", "category")}))

    def parse_ad(self, response: HtmlResponse):
        item = AdItem()
        item['category'] = response.meta.get("category", "category")
        item['title'] = response.xpath('//h1[contains(@class, "title-announcement")]/text()').get().strip()
        item['link'] = response.url
        item['price'] = response.xpath('//div[contains(@class, "announcement-price__cost")]/meta[@itemprop="price"]/@content').get()
        item['post_date'] = response.xpath('//span[@class="date-meta"]/text()').get().replace("Нийтэлсэн: ", "")
        item['imgs'] = ", ".join(response.xpath(f'//img[contains(@class, "announcement__images-item js-image-show-full")]/@src').getall()) 
        yield item
        # for ad in ads:
        #     item = AdItem()
        #     imgs = response.xpath(f'//img[{contains.format("@class", "advert js-item-listing")}]')
        #     item['category'] = category
        #     item['title'] = ad.xpath(
        #         '*/*/a[@class="advert__content-title"]/text()').get().strip()
        #     item['link'] = "https://www.unegui.mn/" + ad.xpath(
        #         '*/*/a[@class="advert__content-title"]/@href').extract()[0]
        #     yield item


    # def parse(self, response):
    #     pass
    
    # def parse(self, response:HtmlResponse):
    #     categories = Selector(response).xpath('//ul[@class="rubrics-list clearfix js-toggle-content toggle-content "]/li')
    #     print(categories)
    #     for category in categories:
    #         item = CategoryItem()
    #         item['parent'] = "Автомашин зарна"
    #         item['title'] = category.xpath(
    #             'a/text()').extract()[0].replace("\xa0", "")
    #         item['url'] = "https://www.unegui.mn/" + category.xpath(
    #             'a/@href').extract()[0]
    #         yield item