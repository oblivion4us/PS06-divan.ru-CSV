import scrapy

class IlluminatenewwscrapSpider(scrapy.Spider):
    name = "illuminatenewwscrap"
    allowed_domains = ["divan.ru"]
    start_urls = ["https://www.divan.ru/kaliningrad/category/stoly"]

    def parse(self, response):
        illuminaires = response.css('div.WdR1o')
        for illuminaire in illuminaires:
            name = illuminaire.css('div.lsooF span::text').get()
            price = illuminaire.css('div.q5Uds span::text').get()
            link = illuminaire.css('a').attrib['href']

            price_with_currency = f"{price} рублей"

            yield {
                'name': f"{name}",
                'price': f"{price_with_currency}",
                'link': f"{link}"
            }