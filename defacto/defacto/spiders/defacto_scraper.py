import scrapy
from scrapy.http import Request
from inline_requests import inline_requests
from ..items import DefactoItem
from urllib.parse import urlencode

API_KEY='ff3cc8159137f06335075d726050e683'

def get_scraperapi_url(url):
    payload = {'api_key': API_KEY, 'url': url }
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url


class DefactoScraperSpider(scrapy.Spider):
    name = "defacto_scraper"
    allowed_domains = ["defacto.com.tr",'api.scraperapi.com']
    
    start_urls = ["https://www.defacto.com.tr/Catalog/PartialIndexScrollResult?page=1&SortOrder=0&pageSize=100&q"]
    
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
        'FEEDS':{
            'defacto_data.csv':{
                'format':'csv',
                'overwrite':True
            }
        }
        
    }

    def parse(self, response):
        

        data = response.json()

        for product in data['Data']['SearchResponse']['Documents']:
            product_id=product['ProductVariantIndex']
            color_variants = product['ProductVariantColorNames']
            product_main_code=product["ProductMainCode"]
            meta={
                'code':product_main_code
            }
            url=f"https://www.defacto.com.tr/Product/GetProductDetailQuickView?productVariantIndex={product_id}&onlyInStock=false"
            #url=get_scraperapi_url(f"https://www.defacto.com.tr/Product/GetProductDetailQuickView?productVariantIndex={product_id}&onlyInStock=false")
            yield scrapy.Request(url=url,callback=self.parse_details,meta=meta)
            
            if len(color_variants) != 0:
                for i in color_variants:
                    variant_id=i['ProductVariantIndex']
                    target_url=f"https://www.defacto.com.tr/Product/GetProductDetailQuickView?productVariantIndex={variant_id}&onlyInStock=false"
                    yield scrapy.Request(url=target_url,callback=self.parse_details,meta=meta)
                    #yield scrapy.Request(url=get_scraperapi_url(target_url),callback=self.parse_details,meta=meta)
            else:
                continue
            
        next_url=data['Data']['NextDataUrl']
        
        if next_url !=None:
            yield scrapy.Request(url=next_url,callback=self.parse)
            
    @inline_requests            
    def parse_details(self,response):
        items = DefactoItem()
        
        code = response.meta.get('code')
        print("status_code: ",response.status)
        data = response.json()
        
        
        product=data['Data']
            
        name=product['ProductName']
        
        
        
        color= product['ProductVariantColorName']
       
        brand = 'Defacto'
        
        category = product['ProductGender'] + '-'+ product['ProductCategoryName']
        
        list_price=product['ProductPriceInclTax']
        

        price=product['ProductVariantDiscountedPriceInclTax']
        
        scrap_url= "https://www.defacto.com.tr/" + product['ProductSeoName'] + '-' + str(product['ProductVariantIndex'])
        
        
        
        for counter,img in enumerate(product['ProductDetailPictures'],start=1):
            if counter > 10:
                break
            else:
                
                items[f'image{counter}'] = 'https://dfcdn.defacto.com.tr/7/' + img['ProductPictureName']
            
        
        
        items['name'] = name
        
        items['scrap_url'] = scrap_url
        
        
        items['color'] = color
               
        items['brand'] = brand
        
        items['category'] = category
        
        items['price'] = price
        
        items['list_price'] = list_price
        

        page_resp = yield Request(url=get_scraperapi_url(scrap_url))
        
        description = page_resp.xpath('//*[@id="section__productinfo"]/div[2]/div/div[2]/ul/li[1]/text()').get()
        
        items['description'] = description.strip().replace('\n',' ')
        
        for size in product['Size']:
            size_name=size['Size']
            qty=size['StockQuantity']
            items['size'] = size_name
            product_code = str(code) + ','  + str(size_name) + ',' + str(color)
            items['product_code'] = product_code
            items['group_code'] = str(code)
            items['qty'] = qty            
            
            yield items

        
        
            
            
                    
