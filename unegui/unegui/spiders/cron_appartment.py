import re
from typing import Any
import pymongo
from scrapy import Spider, Request
from scrapy.http import HtmlResponse, Response
from scrapy.selector import Selector

from unegui.items import ApartmentItem

contains = 'contains({class}, "{class}")'

class CronApartmentSpider(Spider):
    name = "cron_apartment"
    allowed_domains = ["www.unegui.mn"]
    start_urls = []

    def __init__(self):
        for room in range(1, 6):
            self.start_urls.append(f"https://www.unegui.mn/l-hdlh/l-hdlh-zarna/oron-suuts-zarna/{str(room)}-r/")

    # def parse(self, response: HtmlResponse):
    #     category = response.url.rstrip('/').split("/")[-1]
    #     paginition = response.xpath('//ul[@class="number-list"]/li/a/text()').getall()       
    #     if not paginition:
    #         last_page = 1
    #     else:
    #         last_page = int(paginition[-1])
    #     for n in range(1, last_page+1):
    #         yield(Request(response.url.rstrip('/') + "/?page=" + str(n), self.parse_page, meta={"category": category}))

    def parse(self, response: HtmlResponse):
        category_pattern = r"/oron-suuts-zarna/(\w+)/?"
        category_match = re.search(category_pattern, response.url)
        category = "default"
        if category_match:
            category = category_match.group(1)
        category = category.lower()
        ads = Selector(response).xpath('//div[contains(@class, "advert js-item-listing")]')
        end_it = False
        for ad in ads:
            link = "https://www.unegui.mn" + ad.xpath('*/*/a[@class="advert__content-title"]/@href').extract()[0]
            date = ad.xpath('*//div[@class="advert__content-date"]/text()').get()
            is_regular = ad.xpath('@data-t-regular').get()
            if not date.lower() in ["өнөөдөр"] and is_regular is not None:
                end_it = True
                break
            yield(Request(link,callback=self.parse_ad, meta={"category": category}))    
        next_page = response.xpath('//a[@class="number-list-next js-page-filter number-list-line"]/@href').get()
        if(next_page and end_it):
            yield(Request("https://www.unegui.mn"+next_page, self.parse, meta={"category": category}))
        

    # def parse_page(self, response: HtmlResponse):
    #     ads = Selector(response).xpath('//div[contains(@class, "advert js-item-listing")]')
    #     for ad in ads:
    #         link = "https://www.unegui.mn/" + ad.xpath('*/*/a[@class="advert__content-title"]/@href').extract()[0]
    #         yield(Request(link,callback=self.parse_ad, meta={"category": response.meta.get("category", "category")}))

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
    