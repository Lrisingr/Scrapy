# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from crawlbot.items import CrawlbotItem,Article
from datetime import datetime,timedelta
from crawlbot.loaders import TechCrunchArticleLoader

class TechcrunchSpider(CrawlSpider):
    name = 'techcrunch'
    allowed_domains = ['techcrunch.com']
    start_urls = ['https://techcrunch.com/']
    rules = (Rule(LinkExtractor(allow=r'startups/'), callback='parse_item', follow=True),)

    def start_requests(self):
        start_date = datetime(2005,6,11) #start_date specific co techcrunch started posts from that date
        date = start_date
        while date <= datetime.now(): # requests and enque all the articles from start_date to now
            new_request = scrapy.Request(self.generate_url(date)) # generate and request next URL
            new_request.meta["date"] = date
            new_request.meta["page_number"] = 1
            yield new_request
            date += timedelta(days=1)
            pass

    def generate_url(self, date, page_number=None):
        url = 'https://techcrunch.com/' + date.strftime("%Y/%m/%d") + "/"
        if page_number:
            url  += "page/" + str(page_number) + "/"
        return url
    #call parse on each Request ,it pasrses all the articles in the response
    #and go to next page fo given date ,to access the info later pass metadata (date & pagenumber)
    #the resulting response object(article) will have date and page_number and we can access them

    def parse(self,response):
        date = response.meta['date']
        page_number = response.meta['page_number']
        # using a xpath selector get URL for every article for the given page_number
        # which then passes it to parse_article,then parse_article calls itself on the net page
        # if there is no page it returns 404
        articles = response.xpath('//h2[@class="post-title"]/a/@href').extract() #etract all the content in the post-title and store as a list
        for url in articles: # loop through the list and parse each article
            request = scrapy.Request(url,callback=self.parse_article) #request article and callback parse_article
            request.meta['date'] = date
            yield request
            #Since a day has many number of articles the above loops through those and now increment the page_number to go through the next page
        url = self.generate_url(date,page_number+1)
        request = scrapy.Request(url,callback=self.parse)
        request.meta['date'] = date
        yield request

    def parse_article(self,response):
        #time for for ItemLoaders stuff
        #Refer https://doc.scrapy.org/en/latest/topics/loaders.html#input-and-output-processors to understand what itemloader are
        l = TechCrunchArticleLoader(Article(),response=response)
            #starts-with because that division may have many tags under it
        l.add_xpath('title', '//h1/text()') #gets the title of that article
        l.add_xpath('text', '//div[starts-with(@class,"article-entry text")]/p//text()')
        l.add_xpath('tags', '//div[@class="loaded acc-handle"]/a/text()')
        l.add_value('date', str(response.meta['date']))
        l.add_value('url', response.url)
        return l.load_item()
