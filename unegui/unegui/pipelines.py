# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import csv
from datetime import date
import os
import pymongo

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.utils import log
from unegui.items import ApartmentItem

class UneguiPipeline:
    def process_item(self, item, spider):
        return item


class JSONStorePipeline:
    def process_item(self, item, spider):
        now = date.today().strftime("%Y_%m_%d")
        folder = "cars"
        if type(item) == ApartmentItem:
            folder = "apartments"
        csv_path = os.environ.get('CSVS_PATH')
        row = ItemAdapter(item).asdict()
        category = row.get("category", "default_category")
        file_path= os.path.join(csv_path, folder, f"ads_{category}_{now}.csv")
        file_exists = os.path.isfile(file_path)
        with open(file_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
        return item


class MongoDBPipeline:
    collection_name = "categories"

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE", "items"),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        return item