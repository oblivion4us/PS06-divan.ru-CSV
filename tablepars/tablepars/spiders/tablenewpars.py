import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose
from urllib.parse import urljoin
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font
from pydispatch import dispatcher
from scrapy import signals


class TableItem(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    link = scrapy.Field()


class TableLoader(ItemLoader):
    default_output_processor = TakeFirst()
    price_in = MapCompose(lambda x: f"{x} рублей")


class TablenewparsSpider(scrapy.Spider):
    name = "tablenewpars"
    allowed_domains = ["divan.ru"]
    start_urls = ["https://www.divan.ru/kaliningrad/category/stoly"]

    def __init__(self, *args, **kwargs):
        super(TablenewparsSpider, self).__init__(*args, **kwargs)
        self.crawled_data = []
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def parse(self, response):
        tables = response.css('div.WdR1o')

        for table in tables:
            loader = TableLoader(item=TableItem(), selector=table)
            loader.add_css('name', 'div.lsooF span::text')
            loader.add_css('price', 'div.q5Uds span::text')
            loader.add_css('link', 'a::attr(href)')
            item = loader.load_item()

            # Create full URL
            item['link'] = urljoin(response.url, item['link'])

            self.crawled_data.append(item)
            yield item

    def spider_closed(self, spider):
        # Save data to Excel
        df = pd.DataFrame(self.crawled_data)
        wb = Workbook()
        ws = wb.active
        ws.title = "Столы"
        ws.append(['Название стола', 'Стоимость'])

        for index, row in df.iterrows():
            ws.append([row['name'], row['price']])
            cell = ws.cell(row=index + 2, column=1)
            cell.hyperlink = row['link']
            cell.font = Font(color='0000FF', underline='single')

        wb.save('stoly_data.xlsx')

        df.to_csv('stoly_data.csv', index=False)
