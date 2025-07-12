# import requests
# from lxml import html
# import time
# import random

# # 🔑 Your ScraperAPI Key
# SCRAPERAPI_KEY = "2c0772d5b9faf6add92e6006b730b6d0"

# # 👇 Replace with your actual playlist URL
# PLAYLIST_URL = "https://youtube.com/playlist?list=PLGf6Ram2AQh2GpckMjstVH6AaTm0kPfgI"

# # 🎯 Add headers to mimic a real browser
# HEADERS = {
#     "User-Agent": (
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#         "AppleWebKit/537.36 (KHTML, like Gecko) "
#         "Chrome/122.0.0.0 Safari/537.36"
#     ),
#     "Accept-Language": "en-US,en;q=0.9",
# }

# # 🚀 Construct ScraperAPI request URL
# def get_scraperapi_url(target_url):
#     return f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={target_url}&keep_headers=true"

# # 🔍 Extract video titles using lxml
# def get_playlist_titles(playlist_url):
#     try:
#         response = requests.get(get_scraperapi_url(playlist_url), headers=HEADERS, timeout=30)

#         # Check if response is successful
#         if response.status_code != 200:
#             print("Failed to fetch playlist. Status Code:", response.status_code)
#             return []

#         tree = html.fromstring(response.content)

#         # XPath for video titles (used in playlist pages)
#         titles = tree.xpath('//a[@id="video-title"]/text()')

#         # Clean & filter titles
#         cleaned_titles = [title.strip() for title in titles if title.strip()]
#         return cleaned_titles

#     except Exception as e:
#         print("Error occurred:", e)
#         return []

# # 🧪 Call the function
# if __name__ == "__main__":
#     print("Fetching video titles from playlist...\n")
#     titles = get_playlist_titles(PLAYLIST_URL)

#     if not titles:
#         print("No titles found or blocked.")
#     else:
#         for i, title in enumerate(titles, 1):
#             print(f"{i}. {title}")

#         # ⏱ Optional: Delay to avoid rate limiting
#         time.sleep(random.uniform(2, 5))




import yt_dlp

def get_yt_playlist_titles(playlist_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        titles = [entry['title'] for entry in info['entries']]
        return titles

# Use it:
playlist_url = "https://www.youtube.com/playlist?list=PLGf6Ram2AQh2GpckMjstVH6AaTm0kPfgI"
titles = get_yt_playlist_titles(playlist_url)

for i, title in enumerate(titles, 1):
    print(f"{i}. {title}")
