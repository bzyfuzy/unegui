import re
import pymongo
from scrapy import Spider, Request
from scrapy.http import HtmlResponse, Response
from scrapy.selector import Selector

from unegui.items import AdItem

contains = 'contains({class}, "{class}")'

class CronCarSpider(Spider):
    name = "cron_car"
    allowed_domains = ["www.unegui.mn"]
    start_urls = ["https://www.unegui.mn/avto-mashin/-avtomashin-zarna/acura/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/audi/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/baic/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/bmw/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/byd/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/cadillac/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/Changan/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/chery/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/chevrolet/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/chrysler/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/daewoo/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/daihatsu/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/dodge/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/fiat/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/ford/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/geely/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/haval/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/honda/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/hummer/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/hyundai/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/infiniti/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/isuzu/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/jaguar/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/jeep/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/kaiyi/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/kia/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/Lada/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/land-rover/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/lexus/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/lincoln/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/li-auto/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/mazda/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/mercedes-benz/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/mg/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/mini/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/mitsubishi/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/nissan/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/opel/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/peugeot/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/porsche/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/renault/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/samsung/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/ssangyong/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/skoda/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/subaru/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/suzuki/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/Tesla/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/toyota/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/volkswagen/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/volvo/", "https://www.unegui.mn/avto-mashin/-avtomashin-zarna/busad/"]
    # start_urls = ["https://www.unegui.mn/avto-mashin/-avtomashin-zarna/infiniti/"]

    # def __init__(self):
    #     self.client = pymongo.MongoClient("mongodb://192.168.1.10:37017")
    #     self.db = self.client["datasets"]
        # for category in mycol.find():
        #     print(category)
        #     self.start_urls.append(category['url'])

    def parse(self, response: HtmlResponse):
        category_pattern = r"/-avtomashin-zarna/(\w+)/?"
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
       

    def parse_ad(self, response: HtmlResponse):
        item = AdItem()
        item['category'] = response.meta.get("category", "category")
        item['title'] = response.xpath('//h1[contains(@class, "title-announcement")]/text()').get().strip()
        item['link'] = response.url
        item['price'] = response.xpath('//div[contains(@class, "announcement-price__cost")]/meta[@itemprop="price"]/@content').get()
        item['post_date'] = response.xpath('//span[@class="date-meta"]/text()').get().replace("Нийтэлсэн: ", "")
        item['imgs'] = ", ".join(response.xpath(f'//img[contains(@class, "announcement__images-item js-image-show-full")]/@src').getall()) 

        item["detail"] = response.xpath('//div[contains(@class, "js-description")]/p/text()').get().strip()
        item["millage"] = response.xpath('//span[contains(text(), "Явсан:")]/following-sibling::a/text()').get().strip()
        item["engine_type"] = response.xpath('//span[contains(text(), "Хөдөлгүүр:")]/following-sibling::a/text()').get().strip()
        item["engine_size"] = response.xpath('//span[contains(text(), "Мотор багтаамж:")]/following-sibling::a/text()').get().strip()
        item["transmission"] = response.xpath('//span[contains(text(), "Хурдны хайрцаг:")]/following-sibling::a/text()').get().strip()
        item["wheel"] = response.xpath('//span[contains(text(), "Хөтлөгч:")]/following-sibling::a/text()').get().strip()
        item["color"] = response.xpath('//span[contains(text(), "Өнгө:")]/following-sibling::a/text()').get().strip()

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