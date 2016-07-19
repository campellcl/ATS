"""
Items.py
A subclass of scrapy.Items which stores Scrapy returned information.
@Author: Chris Campell
@Version: 7/17/2016
"""

import scrapy

class HikerItem(scrapy.Item):
    """
    HikerItem(scrapy.Item) -A data structure for a Hiker object where data is stored by Scrapy.
    @Author: Chris Campell
    @Version: 7/17/2016
    """
    id = scrapy.Field()
    name = scrapy.Field()
    trail_name  = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    dir = scrapy.Field()
    about_url = scrapy.Field()
    journal_url = scrapy.Field()
    journal = scrapy.Field()
