import pymysql  # ✅ The library for connecting to MySQL/MariaDB
import pandas as pd  # ✅ To load your Excel/CSV data

# 1️⃣ Read your dataset
df = pd.read_excel(r"C:\Users\suraj\Desktop\Projects\Flipkart Laptop Analysis\flipkart_laptops_cleaned.xlsx")  
print(f"✅ Loaded {len(df)} rows from the dataset.")

# 2️⃣ Connect to the database
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='project',
    port=3306
)
cursor = conn.cursor()
print("✅ Connected to database.")

# 3️⃣ Example insertion query
insert_query = """
INSERT INTO fp (
    product_id, name, brand_name, processor_name, RAM, storage, display, gpu, os,
    warranty_year, original_price, mrp, discount, rating, rating_count,
    reviews_count, flipkart_assured, product_link, image_url
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,
           %s, %s, %s, %s, %s, %s,
           %s, %s, %s, %s)
"""

# 4️⃣ Loop through your dataset and insert
count = 0
for _, row in df.iterrows():
    cursor.execute(insert_query, (
        str(row['Product ID']),
        str(row['Name']),
        str(row['Brand Name']),
        str(row['Processor']),
        str(row['RAM']),
        str(row['Storage']),
        str(row['Display']),
        str(row['GPU']),
        str(row['OS']),
        str(row['Warranty year']),
        str(row['Original Price']),
        str(row['MRP']),
        float(row['Discount']) if not pd.isnull(row['Discount']) else None,
        float(row['Rating']) if not pd.isnull(row['Rating']) else None,
        int(row['Rating Count']) if not pd.isnull(row['Rating Count']) else None,
        int(row['Reviews Count']) if not pd.isnull(row['Reviews Count']) else None,
        str(row['Flipkart Assured']),
        str(row['Product Link']),
        str(row['Image Url'])
    ))
    count += 1

# 5️⃣ Commit the transaction
conn.commit()
print(f"✅ Done! Inserted {count} rows into 'flipkart_products'.")

# 6️⃣ Close the connections
cursor.close()
conn.close()
print("🔒 Connection closed.")
