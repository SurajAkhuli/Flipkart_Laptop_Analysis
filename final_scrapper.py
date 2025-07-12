# Flipkart Final Scraper 
import requests
from lxml import html
import pandas as pd
import time
import random
import re
import os

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 Version/16.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 11; SM-M315F) AppleWebKit/537.36 Chrome/112.0.0.0 Mobile Safari/537.36"
]

data = []

# 1. Multiple Queries
queries = ["hp laptop", "dell laptop", "apple laptop", "asus laptop", "lenevo laptop","acer laptop"]

api_keys = [
                "put your scapper_api account key 1",
                "put your scapper_api account key 2",
                "put your scapper_api account key 3",
                "i used to put 4 key you can any number of key"
    # it's better to  put key in seperate file and import from there by using os lib
            ]
def get_scraperapi_response(url, headers, api_keys):
    for key in api_keys:
        scraper_url = f"https://api.scraperapi.com/?api_key={key}&url={url}"
        try:
            response = requests.get(scraper_url, headers=headers, timeout=15)
            if response.status_code == 200 and len(response.content) > 1000:
                return response  # Success
            elif response.status_code == 429:
                print(f"🔁 API key {key} rate-limited. Trying next key...")
            elif response.status_code == 403:
                print(f"⛔ API key {key} forbidden. Trying next key...")
            else:
                print(f"⚠️ API key {key} returned status {response.status_code}")
        except Exception as e:
            print(f"❌ Error using key {key}: {e}")
    print("❌ All API keys failed.")
    return None



# 2. Page loop with retry and error handling
for query in queries:
    print(f"\n🔍 Scraping query: {query}")
    for page in range(1, 41):
        try:
            print(f"Scraping page {page} of {query}...")
            url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}&page={page}"
            headers = {'User-Agent': random.choice(user_agents)}
            
            # response = requests.get(url, headers=headers, timeout=10)

            response = get_scraperapi_response(url, headers, api_keys)
            if not response:
                print(f"❌ Skipping page {page} for query '{query}' due to failed API.")
                continue


            # if response.status_code != 200:
            #     print(f"Page {page} failed with status {response.status_code}, skipping.")
            #     if response.status_code == 429:
            #         print(f"Rate limit hit on page {page} for query '{query}' — sleeping 30s.")
            #         time.sleep(30)
            #     continue

            tree = html.fromstring(response.content)
            product_blocks = tree.xpath('//div[contains(@class, "cPHDOP col-12-12")]')

            for block in product_blocks:
                try:
                    name = block.xpath('.//div[@class="KzDlHZ"]/text()')
                    name = name[0] if name else None

                    # 3. Skip Accessories
                    if name and any(x in name.lower() for x in ["skin", "sticker", "cover", "stand", "sleeve", "guard"]):
                        continue

                    brand = name.split()[0] if name else None
                    
                    original_price = block.xpath('.//div[@class="Nx9bqj _4b5DiR"]/text()')
                    original_price = original_price[0] if original_price else None

                    mrp = block.xpath('string(.//div[@class="yRaY8j ZYYwLA"])').strip()
                    mrp = mrp if mrp else None

                    discount = block.xpath('.//div[@class="UkUFwK"]/span/text()')
                    if discount:
                        discount = re.search(r'\d+', discount[0])
                        discount = int(discount.group(0)) if discount else None
                    else:
                        discount = None


                    rating = block.xpath('string(.//div[@class="XQDdHH"])').strip()
                    try: rating = float(rating)
                    except: rating = None

                    dataid = block.xpath('.//@data-id')
                    dataid = dataid[0] if dataid else None

                    image_url = block.xpath('.//img[@class="DByuf4"]/@src | .//img[@class="DByuf4"]/@data-src')
                    image_url = image_url[0] if image_url else None

                    rating_review_texts = block.xpath('.//span[@class="Wphh3N"]//span/text()')
                    ratingCount = None
                    reviewsCount = None
                    if len(rating_review_texts) >= 3:
                        rating_text = rating_review_texts[0]
                        reviews_text = rating_review_texts[2]
                        rating_match = re.search(r'[\d,]+', rating_text)
                        reviews_match = re.search(r'[\d,]+', reviews_text)
                        if rating_match:
                            ratingCount = int(rating_match.group(0).replace(',', ''))
                        if reviews_match:
                            reviewsCount = int(reviews_match.group(0).replace(',', ''))

                    assured = "No"
                    assured_div = block.xpath('.//div[contains(@class, "_0CSTHy")]')
                    if assured_div:
                        assured_img = assured_div[0].xpath('.//img')
                        if assured_img:
                            assured = "Yes"

                    href = block.xpath('.//a[@class="CGtC98"]/@href')
                    base_url = "https://www.flipkart.com"
                    product_link = base_url + href[0].split("?")[0] if href and "/p/" in href[0] else None

                    specs = block.xpath('.//ul[@class="G4BRas"]/li/text()')

                    warranty = None
                    processor = None
                    ram = None
                    os = None
                    storage = None
                    display = None
                    gpu = None

                    for spec in specs:
                        spec_lower = spec.lower()
                        if not processor and "processor" in spec_lower:
                            processor = spec
                        elif not ram and "ram" in spec_lower:
                            ram = spec
                        elif not os and "operating system" in spec_lower:
                            os = spec
                        elif not storage and ("ssd" in spec_lower or "hdd" in spec_lower):
                            storage = spec
                        elif not display and "display" in spec_lower:
                            display = spec
                        elif not warranty and "warranty" in spec_lower:
                            warranty = spec
                        elif not gpu and ("graphics" in spec_lower or "nvidia" in spec_lower or "intel uhd" in spec_lower or "radeon" in spec_lower):
                            gpu = spec

                    row_data = {
                        'Product ID': dataid,            
                        'Name': name,                     
                        'Brand Name': brand,             
                        'Processor': processor,         
                        'RAM': ram,                    
                        'Storage': storage,        
                        'Display': display,            
                        'GPU': gpu,                      
                        'OS': os,                       
                        'Warranty year': warranty,      
                        'Original Price': original_price,
                        'MRP': mrp,                    
                        'Discount': discount,           
                        'Rating': rating,                 
                        'Rating Count': ratingCount,     
                        'Reviews Count': reviewsCount,  
                        'Flipkart Assured': assured,      
                        'Product Link': product_link,    
                        'Image Url': image_url          
                    }
                    if row_data['Name'] and row_data['Original Price']:
                        data.append(row_data)
                    else:
                        print("⚠️ Skipping incomplete row")


                except Exception as e:
                    print("⚠️ Error parsing product:", e)

            # 4. Page sleep and 10-page cooldown
            time.sleep(random.uniform(2, 4))
            if page % 10 == 0:
                print("😴 Cooling down after 10 pages...")
                time.sleep(20)

        except Exception as e:
            print(f"❌ Failed page {page} for query '{query}': {e}")
            continue

# 7. Final CSV save
file_name = "flipkart_laptops_cleaned.csv"
df = pd.DataFrame(data)

# if the original file is locked or in use, so your script never crashes during saving. Automatically rename the file
file_base = "flipkart_laptops_cleaned"
file_ext = ".csv"
file_name = file_base + file_ext
counter = 1
# Try saving. If file is locked, append a number and retry.
while True:
    try:
        df.to_csv(file_name, index=False)
        print(f"✅ Saved {len(df)} records to {file_name}")
        break
    except PermissionError:
        file_name = f"{file_base}{counter}{file_ext}"
        counter += 1
        print(f"⚠️ File locked. Trying to save as {file_name}...")

print(f"\n✅ Scraping complete. Saved {len(df)} records to {file_name}")
