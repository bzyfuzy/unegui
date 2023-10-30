import pymongo
from scrapy import Spider, Request
from scrapy.http import HtmlResponse, Response
from scrapy.selector import Selector

from unegui.items import ApartmentItem

contains = 'contains({class}, "{class}")'

class ApartmentSpider(Spider):
    name = "apartment"
    allowed_domains = ["www.unegui.mn"]
    start_urls = []

    def __init__(self):
        # myclient = pymongo.MongoClient("mongodb://192.168.1.10:37017")
        # mydb = myclient["unegui"]
        # mycol = mydb["apartment_categories"]
        for room in range(1, 6):
            self.start_urls.append(f"https://www.unegui.mn/l-hdlh/l-hdlh-zarna/oron-suuts-zarna/{str(room)}-r/")

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
        item = ApartmentItem()
        item["detail"] = response.xpath('//div[contains(@class, "js-description")]/p/text()').get().strip()
        item["b_davhar"] = response.xpath('//span[contains(text(), "Барилгын давхар:")]/following-sibling::a/text()').get().strip()
        item["davhart"] = response.xpath('//span[contains(text(), "Хэдэн давхарт:")]/following-sibling::a/text()').get().strip()
        item["ashiglaltand"] = response.xpath('//span[contains(text(), "Ашиглалтанд орсон он:")]/following-sibling::a/text()').get().strip()
        item["talbai"] = response.xpath('//span[contains(text(), "Талбай:")]/following-sibling::a/text()').get().strip()
        item["address"] = response.xpath('//span[@itemprop="address"]/text()').get().strip()
        item['category'] = response.meta.get("category", "category")
        item['title'] = response.xpath('//h1[contains(@class, "title-announcement")]/text()').get().strip()
        item['link'] = response.url
        item['price'] = response.xpath('//div[contains(@class, "announcement-price__cost")]/meta[@itemprop="price"]/@content').get()
        item['post_date'] = response.xpath('//span[@class="date-meta"]/text()').get().replace("Нийтэлсэн: ", "")
        item['imgs'] = ", ".join(response.xpath(f'//img[contains(@class, "announcement__images-item js-image-show-full")]/@src').getall()) 
        yield item
    