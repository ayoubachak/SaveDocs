import scrapy

class DocsSpider(scrapy.Spider):
    name = 'docs'
    start_urls = ['https://example.com/docs']  # Replace with the actual documentation base URL

    def parse(self, response):
        # Extract the content and follow links to the next pages
        for href in response.css('a::attr(href)'):  # Adjust the selector based on your site's layout
            yield response.follow(href, self.parse)

        # You might also want to collect URLs here and save them for later use
        page_url = response.url
        self.logger.info('A document page found: %s', page_url)
        yield {
            'url': page_url
        }

