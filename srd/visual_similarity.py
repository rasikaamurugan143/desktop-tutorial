import pickle
import imagehash
from PIL import Image
from playwright.sync_api import sync_playwright
import pandas as pd
import os
import time

# -----------------------------
# CREATE REQUIRED FOLDERS
# -----------------------------
os.makedirs("screenshots", exist_ok=True)
os.makedirs("model", exist_ok=True)

# Load TRAINING URLs (from feature_extraction.py split)
print("Loading training URLs...")
try:
    train_urls = pickle.load(open("model/train_urls.pkl", "rb"))
    print(f"Loaded {len(train_urls)} training URLs")
except:
    print("ERROR: train_urls.pkl not found - Run feature_extraction.py first!")
    exit(1)

# Load reference hashes
try:
    ref_hashes = pickle.load(open("model/ref_hashes.pkl", "rb"))
    print("Reference hashes loaded")
except:
    print("ERROR: ref_hashes.pkl not found in model folder")
    ref_hashes = []

# -----------------------------
# CAPTURE SCREENSHOT
# -----------------------------
def capture(url, path):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, timeout=3000)
            page.wait_for_timeout(1000)

            page.screenshot(path=path)

            browser.close()
        return True

    except Exception as e:
        print(f"⚠️ Error loading {url}: {e}")
        return False

# -----------------------------
# IMAGE HASH FUNCTION
# -----------------------------
def get_hash(path):
    try:
        img = Image.open(path)
        return imagehash.phash(img)
    except:
        return None

# -----------------------------
# MAIN FUNCTION
# -----------------------------
def main():
    print("Starting visual similarity computation for training URLs...")
    
    # Use only first 1000 URLs to save time (visual scores are supplementary)
    max_urls = min(1000, len(train_urls))
    subset_urls = train_urls[:max_urls]
    
    print(f"   Processing {len(subset_urls)} training URLs (subset)...")

    scores = []

    for i, url in enumerate(subset_urls):
        print(f"Processing {i+1}/{len(subset_urls)}", end="\r")

        path = f"screenshots/{i}.png"

        # Capture screenshot
        if capture(url, path):
            h = get_hash(path)

            if h and ref_hashes:
                score = max([1 - (h - r) / 64 for r in ref_hashes])
            else:
                score = 0
        else:
            score = 0

        scores.append(score)

        # Prevent system overload
        time.sleep(0.1)

        # Progress update
        if (i + 1) % 100 == 0:
            print(f"Completed {i+1}/{len(subset_urls)}")

    # Save visual scores - pad with zeros for remaining training URLs
    # This ensures alignment with training data
    full_scores = scores + [0] * (len(train_urls) - len(subset_urls))
    
    pickle.dump(full_scores, open("model/visual_scores.pkl", "wb"))
    
    print(f"\nVisual scores saved: {len(full_scores)} scores (padded)")
    print("   File: model/visual_scores.pkl")


# -----------------------------
# RUN SCRIPT
# -----------------------------
if __name__ == "__main__":
    main()