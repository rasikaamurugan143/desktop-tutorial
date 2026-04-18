import pandas as pd

# Check the original dataset
df = pd.read_csv('data/phishing_dataset.csv')

# Check some example URLs
legitimate_urls = df[df['label'] == 0]['url'].head(5)
phishing_urls = df[df['label'] == 1]['url'].head(5)

print('URLs labeled as Class 0 (Legitimate):')
for url in legitimate_urls:
    print(f'  {url[:80]}')

print('\nURLs labeled as Class 1 (Phishing):')
for url in phishing_urls:
    print(f'  {url[:80]}')
    
# Check distribution
print(f'\nClass 0 (Legitimate) count: {(df["label"] == 0).sum()}')
print(f'Class 1 (Phishing) count: {(df["label"] == 1).sum()}')
