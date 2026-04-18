from playwright.sync_api import sync_playwright
from PIL import Image
import imagehash
import pickle
import os

# Websites list
reference_urls = [
    "https://www.google.com",
    "https://accounts.google.com",
    "https://www.facebook.com",
    "https://www.instagram.com",
    "https://login.microsoftonline.com",
    "https://www.apple.com",
    "https://www.onlinesbi.sbi",
    "https://www.hdfcbank.com",
    "https://www.icicibank.com",
    "https://www.axisbank.com",
    "https://www.paypal.com",
    "https://paytm.com",
    "https://www.phonepe.com",
    "https://pay.google.com",
    "https://www.amazon.in",
    "https://www.flipkart.com",
    "https://mail.google.com",
    "https://outlook.live.com",
    "https://login.yahoo.com",
    "https://www.dropbox.com/login"
]

# Create folder
os.makedirs("visual/ref_images", exist_ok=True)

def capture(url, path):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=10000)
            page.wait_for_timeout(2000)
            page.screenshot(path=path)
            browser.close()
        return True
    except:
        print("Failed:", url)
        return False

hashes = []

for i, url in enumerate(reference_urls):
    print("Opening:", url)

    path = f"visual/ref_images/img_{i}.png"

    if capture(url, path):
        img = Image.open(path)
        h = imagehash.phash(img)
        hashes.append(h)

# Save file
with open("visual/ref_hashes.pkl", "wb") as f:
    pickle.dump(hashes, f)

print("✅ Done! File created")