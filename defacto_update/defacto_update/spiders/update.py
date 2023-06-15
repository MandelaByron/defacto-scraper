import scrapy
from scrapy.http import Request
from inline_requests import inline_requests
from ..items import DefactoUpdateItem
from urllib.parse import urlencode


API_KEY='ff3cc8159137f06335075d726050e683'

# def get_scraperapi_url(url):
#     payload = {'api_key': API_KEY, 'url': url }
#     proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
#     return proxy_url


class UpdateSpider(scrapy.Spider):
    name = "update"
    
    allowed_domains = ["defacto.com.tr",'api.scraperapi.com']
    start_urls = ["https://www.defacto.com.tr/Catalog/PartialIndexScrollResult?page=1&SortOrder=0&pageSize=100&q"]
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
        'FEEDS':{
            'defacto_update_data.csv':{
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
        
        code=response.meta.get('code')
        items =DefactoUpdateItem()
        print("status_code: ", response.status)
        
        data = response.json()
        
        
        product=data['Data']
            

        color= product['ProductVariantColorName']

        
        list_price=product['ProductPriceInclTax']
        

        price=product['ProductVariantDiscountedPriceInclTax']
        
        scrap_url= "https://www.defacto.com.tr/" + product['ProductSeoName'] + '-' + str(product['ProductVariantIndex'])
        items['scrap_url']=scrap_url
         
        items['price'] = price
        
        items['list_price'] = list_price
      
        
        for size in product['Size']:
            size_name=size['Size']
            qty=size['StockQuantity']
           
            product_code = str(code) + ','  + str(size_name) + ',' + str(color)
            items['product_code'] = product_code
           
            items['qty'] = qty            
            
            yield items

        
        
            
            
                    
