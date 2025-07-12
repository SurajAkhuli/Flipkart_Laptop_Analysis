import requests
from lxml import html
import pandas as pd
import time
import random
import re

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 Version/16.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 11; SM-M315F) AppleWebKit/537.36 Chrome/112.0.0.0 Mobile Safari/537.36"
]

data = []

for page in range(1, 3):
    print(f"Scraping page {page}...")
    url = f"https://www.flipkart.com/search?q=laptop&page={page}"
    
    headers = {
        'User-Agent': random.choice(user_agents)
    }

    response = requests.get(url, headers=headers)
    # with open(f"page_{page}.html", "wb") as f:
    #     f.write(response.content)

    if response.status_code != 200:
        print(f"Failed to fetch page {page} with status {response.status_code}")
        continue

    tree = html.fromstring(response.content)
    product_blocks = tree.xpath('//div[contains(@class, "cPHDOP col-12-12")]')


    for block in product_blocks:
        try:
            name = block.xpath('.//div[@class="KzDlHZ"]/text()')
            name = name[0] if name else None
            
            brand = name.split()[0] if name else None

            price = block.xpath('.//div[@class="yRaY8j ZYYwLA"]/text()')
            price = price[0] if price else None
            
            original_price = block.xpath('.//div[@class="Nx9bqj _4b5DiR"]/text()')
            original_price = original_price[0] if original_price else None

            discount = block.xpath('.//div[@class="UkUFwK"]/text()')
            discount = discount[0] if discount else None
            
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

                # Extract only digits
                rating_match = re.search(r'[\d,]+', rating_text)
                reviews_match = re.search(r'[\d,]+', reviews_text)

                if rating_match:
                    ratingCount = int(rating_match.group(0).replace(',', ''))  # => 1470
                if reviews_match:
                    reviewsCount = int(reviews_match.group(0).replace(',', ''))  # => 168
                    
                    
            assured = "No"  # default
            assured_div = tree.xpath('.//div[contains(@class, "_0CSTHy")]')
            if assured_div:
                assured_img = assured_div[0].xpath('.//img')
                if assured_img:
                    assured = "Yes"
            
                    
            href = block.xpath('.//a[@class="CGtC98"]/@href')
            base_url = "https://www.flipkart.com"
            if href and "/p/" in href[0]:
                clean_href = href[0].split("?")[0]  # strip tracking junk
                product_link = base_url + clean_href
            else:
                product_link = None


            specs = block.xpath('.//ul[@class="G4BRas"]/li/text()')
            # processor = specs[0] if len(specs) > 0 else None
            # ram = specs[1] if len(specs) > 1 else None
            # os = specs[2] if len(specs) > 2 else None
            # storage = specs[3] if len(specs) > 3 else None
            # display = specs[4] if len(specs) > 4 else None
            # if len(specs)>6 :
            #     warranty = specs[6] if len(specs) > 6 else None #specially for Expensive(Apple)laptop
            # else : warranty = specs[5] if len(specs) > 5 else None
            
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


            data.append({
                'Name': name,
                'Product ID': dataid,
                'Brand Name': brand,
                'Price': price,
                'Original Price': original_price,
                'Discount': discount,
                'Rating': rating,
                'Rating Count': ratingCount,
                'Reviews Count': reviewsCount,
                'Processor': processor,
                'RAM': ram,
                'Storage': storage,
                'Display': display,
                'OS': os,
                'Warranty year': warranty,
                'GPU': gpu,
                'Product Link': product_link,
                'Image Url' : image_url,
                'Flipkart Assured': assured
            })
        except Exception as e:
            print("Error parsing product:", e)

    time.sleep(random.randint(2, 4))  # Random delay between 2–4 seconds

# Save to CSV
df = pd.DataFrame(data)
df.to_csv("flipkart_laptops.csv", index=False)
print(f"Saved {len(df)} rows to flipkart_laptops.csv")



########## Let me know if you want to auto-split and save after every 10 pages, or handle retry for failed pages (e.g., 429, 403).  ##############