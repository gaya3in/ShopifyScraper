import os
import django
import csv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ShopifyScraper.settings')
django.setup()

import requests
import psycopg2
import re
import time
from shopify.models import Website, Endpoint



class ScrapeShopify:

############################################################################################
#  Initialize Class Variables                                                              #
############################################################################################
    def __init__(self, url, json_data):
        self.url = url
        self. json_data = json_data

############################################################################################
# Get Domain Name from the URL provided                                                    #
############################################################################################
    def getDomainName(self):
        url1 = self.url.removeprefix("https://www.")
        domainName = url1.partition("/")[0]
        return domainName

############################################################################################
# Format the URLs AND return direct and checkout links for the SKU                         #
############################################################################################
    def getDirectAndCheckoutLinks(self, handle, variantid):
        domain = self.getDomainName()
        url1 = f'https://www.{domain}/products/{handle}'
        url2 = f'https://www.{domain}/products/cart/add?id={variantid}&quantity=1'
        return url1,url2

############################################################################################
# Get Valid SKU - Slice and check Pattern for Type2,
#                 Check Pattern for Type1
############################################################################################
    def ValidSku(self, sku):
        try:
            global sliced_sku
            #Check for Nike Stock Codes
            if sku.find("-") >= 1:
                if sku.count("-") > 1:
                    sliced_sku = sku[:sku.rfind("-")]
                    if re.search("^[A-Z0-9]{2}[0-9]{4}-[0-9]{3}$", sliced_sku):
                        return "Type2:Nike"
                    else:
                        return "other"
                else:
                    if re.search("^[A-Z0-9]{2}[0-9]{4}-[0-9]{3}$", sku):
                        return "Type1:Nike"
                    sliced_sku = sku[:sku.find("-")]
                    if re.search("^[A-Z]{2}[0-9]{4}$", sliced_sku):
                        return "Type2:Adidas"
                    else:
                        return "other"
            elif re.search("^[A-Z]{2}[0-9]{4}$", sku):
                return "Type1:Adidas"
            else:
                return "other"
        except Exception as e:
            print(e)
            print("SKU:" , sku)

############################################################################################
# Read each ProductId, VariantId from the last scraped CSV file
# Return True if already scraped
# Return False if not scraped before
############################################################################################
    def checkIfScraped(self, productid, variantid):
        with open("scraped_data.csv", "r") as csv_file:
           reader = csv.reader(csv_file, delimiter=",")
           for row in reader:
                  if row:
                       if row[0] == str(productid) and row[1] == str(variantid):
                              #print("match found!!!!")
                              return True
           return False

############################################################################################
# 1. Read data from the JSON file
# 2. Connect Postgres DB
# 3. Open csv file to save scraped data
# 4. Save data in DB and write the saved data iin CSV file
############################################################################################
    def readData(self):
        count=0
        try:
            connect = psycopg2.connect(dbname="testdb", user="postgres", password="123456", host="localhost",
                                       port="5433")
            cursor = connect.cursor()
            with open("scraped_data.csv", "a", newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["ProductId", "VariantId"])

                for product in self.json_data['products']:
                    productid = product['id']
                    handle = product['handle']
                    type = product['product_type']
                    if 'Shoe' or 'Footwear' in type:
                        for variant in product['variants']:
                            sku = variant['sku']
                            variantid = variant["id"]
                            if not self.checkIfScraped(productid, variantid):
                                if sku:
                                    if "Type2" in self.ValidSku(sku):
                                        sku = ""
                                        sku = sliced_sku
                                    elif self.ValidSku(sku) == "other":
                                        continue
                                    price = variant['price']
                                    created_at = variant['created_at']
                                    updated_at = variant['updated_at']
                                    productURL, checkoutURL = self.getDirectAndCheckoutLinks(handle, variantid)
                                    size = variant['title']

                                    cursor.execute("""insert into product (release_location,price,created_at,updated_at,retailer,available_sizes,
                                                                               direct_link,auto_checkout_link,stock_code)
                                                                               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                                                   (self.getDomainName(), price, created_at, updated_at, None, size, productURL,
                                                    checkoutURL, sku))
                                    lst = [productid, variantid]
                                    writer.writerow(lst)
                csv_file.close()
                connect.commit()
                connect.close()

        except Exception as e:
            print(e)


############################################################################################
# Connect to Django Model and retrieve the websites
# MAke an API call to the JSON file using requests
# If website status is active, Loop through each Endpoint in the website
# Initialize the class with the endpoint url and Json data for that URL
# Call the ReadData function to loop through every record n the JSON File
# Add 2.5 minutes time delay between url scrapes
############################################################################################
sliced_sku = ''
websites = Website.objects.all()
for website in websites:
    if website.status:
        endpoints = website.endpoint_set.all()
        for endpoint in endpoints:
            url = endpoint.endpoint

            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Mobile Safari/537.36"
            }

            response = requests.get(url, headers=headers)
            json_data = response.json()
            obj = ScrapeShopify(url=url,json_data=json_data)
            obj.readData()
            time.sleep(2.5 * 60)


