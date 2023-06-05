from defacto.spiders.defacto_scraper import DefactoScraperSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

def main():
    settiings=get_project_settings()
    process = CrawlerProcess(settings=settiings)
    process.crawl(DefactoScraperSpider)
    process.start()
    
if __name__ == '__main__':
    main()