# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class UneguiItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class CategoryItem(Item):
    parent = Field()
    title = Field()
    url = Field()
    pass



class AdItem(Item):
    title = Field()
    category = Field()
    price = Field()
    post_date = Field()
    link = Field()
    imgs = Field()
    detail= Field()
    millage  = Field()
    engine_type = Field()
    engine_size= Field()
    transmission = Field()
    wheel= Field()
    color = Field()
    pass

class ApartmentItem(Item):
    detail = Field()
    b_davhar = Field()
    davhart = Field()
    ashiglaltand = Field()
    talbai = Field()
    address = Field()
    category = Field()
    title = Field()
    link = Field()
    price = Field()
    post_date = Field()
    imgs = Field()
    pass