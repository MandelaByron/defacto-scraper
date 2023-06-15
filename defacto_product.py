import requests
import json
from sys import argv
###SAMPLE URL
#url='https://www.defacto.com.tr/oversize-fit-bisiklet-yaka-tisort-2758822'


url=argv[1]
def get_product(url):
    product_url= url

    slug=product_url.split('-')[-1]

    headers={
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }

    url = "https://www.defacto.com.tr/Product/GetProductDetailQuickView"

    querystring = {"productVariantIndex":f"{slug}","onlyInStock":"false"}

    response = requests.request("GET", url,  headers=headers, params=querystring)

    main_data=[]
    #print(response.text)



    data = response.json()


    product=data['Data']
        



    for size in product['Size']:
        items ={
            'scrap_url':'',
            'price':'',
            'list_price':'',
            #'color':'',
            #'size':'',
            'product_code':'',
            'qty':''
            
        }
        color= product['ProductVariantColorName']

        #items['color']=color

        list_price=product['ProductPriceInclTax']


        price=product['ProductVariantDiscountedPriceInclTax']

        scrap_url= "https://www.defacto.com.tr/" + product['ProductSeoName'] + '-' + str(product['ProductVariantIndex'])
        items['scrap_url']=scrap_url
            
        items['price'] = price

        items['list_price'] = list_price

        code= product['ProductLongCode']
        size_name=size['Size']
        #items['size']=size_name
        qty=size['StockQuantity']
        
        product_code = str(code) + '-' + str(size_name) + '-' + str(color)
        items['product_code'] = product_code
        
        items['qty'] = qty            
        
        print(items)
        main_data.append(items)
        print('\n')
        #yield items
    #json_data=
    with open('data.json','w') as fp:
        json.dump(main_data,fp=fp,indent=2)
        #fp.write(json_data)
   
get_product(url)