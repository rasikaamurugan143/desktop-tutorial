import pickle
import pandas as pd
import numpy as np
from scipy.sparse import hstack
import re
from urllib.parse import urlparse

# visual
from PIL import Image
import imagehash
from playwright.sync_api import sync_playwright

# -----------------------------
# LOAD FILES
# -----------------------------
model = pickle.load(open("model/final_model.pkl", "rb"))
tfidf = pickle.load(open("model/tfidf.pkl", "rb"))
ref_hashes = pickle.load(open("model/ref_hashes.pkl", "rb"))

# -----------------------------
# RULES
# -----------------------------
LEGITIMATE_DOMAINS = [
    # Tech Giants
    'google.com', 'www.google.com', 'accounts.google.com', 'mail.google.com', 'drive.google.com', 'docs.google.com',
    'amazon.com', 'www.amazon.com', 'www.amazon.in', 'aws.amazon.com',
    'facebook.com', 'www.facebook.com', 'm.facebook.com',
    'microsoft.com', 'www.microsoft.com', 'login.microsoftonline.com', 'microsoftonline.com', 'office.com', 'outlook.com',
    'apple.com', 'www.apple.com', 'icloud.com', 'developer.apple.com',
    'adobe.com', 'www.adobe.com', 'creative.adobe.com',
    
    # Social Media & Communication
    'youtube.com', 'www.youtube.com',
    'twitter.com', 'www.twitter.com', 'mobile.twitter.com',
    'instagram.com', 'www.instagram.com',
    'linkedin.com', 'www.linkedin.com',
    'reddit.com', 'www.reddit.com', 'old.reddit.com',
    'pinterest.com', 'www.pinterest.com',
    'snapchat.com', 'www.snapchat.com',
    'tiktok.com', 'www.tiktok.com',
    'whatsapp.com', 'web.whatsapp.com',
    'discord.com', 'www.discord.com',
    'slack.com', 'www.slack.com',
    'zoom.us', 'www.zoom.us',
    'teams.microsoft.com',
    
    # E-commerce & Shopping
    'ebay.com', 'www.ebay.com',
    'walmart.com', 'www.walmart.com',
    'target.com', 'www.target.com',
    'bestbuy.com', 'www.bestbuy.com',
    'costco.com', 'www.costco.com',
    'etsy.com', 'www.etsy.com',
    'shopify.com', 'www.shopify.com',
    
    # Financial Services
    'paypal.com', 'www.paypal.com',
    'chase.com', 'www.chase.com', 'secure.chase.com',
    'bankofamerica.com', 'www.bankofamerica.com', 'secure.bankofamerica.com',
    'wellsfargo.com', 'www.wellsfargo.com', 'online.wellsfargo.com',
    'citibank.com', 'www.citibank.com', 'online.citi.com',
    'capitalone.com', 'www.capitalone.com', 'verified.capitalone.com',
    'discover.com', 'www.discover.com',
    'americanexpress.com', 'www.americanexpress.com',
    
    # Indian Banking
    'onlinesbi.sbi', 'www.onlinesbi.sbi', 'retail.onlinesbi.sbi', 'bank.sbi',
    'icicibank.com', 'www.icicibank.com', 'online.icicibank.com',
    'hdfcbank.com', 'www.hdfcbank.com', 'netbanking.hdfcbank.com',
    'axisbank.com', 'www.axisbank.com', 'retail.axisbank.co.in',
    'kotak.com', 'www.kotak.com', 'netbanking.kotak.com',
    'pnbindia.in', 'www.pnbindia.in', 'netpnb.com',
    'unionbankofindia.co.in', 'www.unionbankofindia.co.in',
    'canarabank.in', 'www.canarabank.in',
    
    # Government & Official
    'india.gov.in', 'www.india.gov.in',
    'uidai.gov.in', 'www.uidai.gov.in', 'eaadhaar.uidai.gov.in',
    'incometax.gov.in', 'www.incometax.gov.in', 'e-filing.incometax.gov.in',
    'rbi.org.in', 'www.rbi.org.in', 'rbidocs.rbi.org.in',
    'usa.gov', 'www.usa.gov',
    'gov.uk', 'www.gov.uk',
    'canada.ca', 'www.canada.ca',
    'australia.gov.au', 'www.australia.gov.au',
    
    # Educational
    'harvard.edu', 'www.harvard.edu',
    'mit.edu', 'www.mit.edu',
    'stanford.edu', 'www.stanford.edu',
    'berkeley.edu', 'www.berkeley.edu',
    'coursera.org', 'www.coursera.org',
    'udemy.com', 'www.udemy.com',
    'khanacademy.org', 'www.khanacademy.org',
    
    # News & Media
    'cnn.com', 'www.cnn.com',
    'bbc.com', 'www.bbc.com', 'bbc.co.uk',
    'nytimes.com', 'www.nytimes.com',
    'washingtonpost.com', 'www.washingtonpost.com',
    'reuters.com', 'www.reuters.com',
    'bloomberg.com', 'www.bloomberg.com',
    'wsj.com', 'www.wsj.com',
    
    # Cloud & Storage
    'dropbox.com', 'www.dropbox.com',
    'onedrive.com', 'www.onedrive.com',
    'box.com', 'www.box.com',
    'mega.nz', 'www.mega.nz',
    'pcloud.com', 'www.pcloud.com',
    
    # Development & Tools
    'github.com', 'www.github.com',
    'stackoverflow.com', 'www.stackoverflow.com',
    'gitlab.com', 'www.gitlab.com',
    'bitbucket.org', 'www.bitbucket.org',
    'docker.com', 'www.docker.com',
    'kubernetes.io', 'www.kubernetes.io',
    
    # Search Engines
    'bing.com', 'www.bing.com',
    'yahoo.com', 'www.yahoo.com', 'search.yahoo.com',
    'duckduckgo.com', 'www.duckduckgo.com',
    'baidu.com', 'www.baidu.com',
    
    # Other Trusted Sites
    'wikipedia.org', 'www.wikipedia.org', 'en.wikipedia.org',
    'mozilla.org', 'www.mozilla.org', 'firefox.com',
    'opera.com', 'www.opera.com',
    'chrome.google.com',
    'support.google.com',
    'support.microsoft.com',
    'support.apple.com',
]

LEGITIMATE_PATTERNS = [
    # Common legitimate authentication patterns
    '/signin', '/sign-in', '/login', '/log-in', '/auth', '/authenticate', '/authorization',
    '/oauth', '/sso', '/single-sign-on', '/two-factor', '/2fa', '/mfa',
    '/password', '/reset-password', '/forgot-password', '/change-password',
    '/register', '/signup', '/sign-up', '/create-account',
    '/verify', '/verification', '/email-verify', '/phone-verify',
    '/account', '/my-account', '/profile', '/settings', '/preferences',
    '/dashboard', '/home', '/welcome',
    # Common legitimate e-commerce patterns
    '/cart', '/checkout', '/payment', '/billing', '/shipping', '/order',
    '/product', '/item', '/search', '/category', '/store',
    # Common legitimate support patterns
    '/support', '/help', '/contact', '/faq', '/knowledge-base',
    '/ticket', '/case', '/incident', '/request',
    # Common legitimate API patterns
    '/api', '/v1', '/v2', '/v3', '/graphql', '/rest',
    # Common legitimate media patterns
    '/image', '/photo', '/video', '/audio', '/download', '/upload',
    '/stream', '/live', '/broadcast',
]

PHISHING_PATTERNS = [
    # Suspicious TLDs (expanded)
    '.xyz', '.tk', '.ml', '.ga', '.cf', '.gq', '.top', '.club', '.online', '.site', '.work', '.space', '.fun', '.icu',
    '.cn', '.ru', '.br', '.mx', '.ar', '.co', '.info', '.biz', '.pro', '.cc', '.ws', '.me', '.tv', '.in', '.pk',
    
    # Account/Login patterns (expanded)
    '-account', 'login-security', 'verify-account', 'bank-update', 'secure-login', 'account-verify', 
    'paypal-login', 'google-login', 'facebook-login', 'amazon-login', 'microsoft-login',
    'apple-login', 'netflix-login', 'instagram-login', 'twitter-login', 'linkedin-login',
    
    # Zero-day patterns (expanded typosquatting)
    'g00gle', 'go0gle', 'g0ogle', 'goog1e', 'g00g1e', 'g0og1e', 'g00g13', 'g00gl3',  # Google variations
    'faceb00k', 'f4ceb00k', 'fac3b00k', 'f4c3b00k',  # Facebook variations
    'amaz0n', '4mazon', 'amaz0n-login', '4m4z0n',  # Amazon variations
    'payp4l', 'p4ypal', 'paypa1', 'p4ypa1',  # PayPal variations
    'm1crosoft', 'micr0soft', 'm1cr0s0ft',  # Microsoft variations
    'y0utube', 'youtub3', 'y0utub3',  # YouTube variations
    '1nstagram', 'inst4gram', '1nst4gr4m',  # Instagram variations
    
    # Suspicious subdomains (expanded)
    'secure.', 'login.', 'verify.', 'account.', 'update.', 'password.', 'bank.', 'auth.', 'signin.', 'portal.',
    'admin.', 'support.', 'help.', 'service.', 'billing.', 'payment.', 'checkout.', 'confirm.', 'validate.',
    
    # Path patterns (expanded)
    '/login', '/verify', '/secure', '/account', '/update', '/password', '/signin', '/auth', '/admin', '/portal',
    '/login.php', '/signin.php', '/verify.php', '/update.php', '/secure.php', '/account.php', '/auth.php',
    '/login.asp', '/signin.asp', '/verify.asp', '/update.asp', '/secure.asp', '/account.asp', '/auth.asp',
    '/login.html', '/signin.html', '/verify.html', '/update.html', '/secure.html', '/account.html', '/auth.html',
    
    # Query patterns (expanded)
    '?login', '?verify', '?secure', '?account', '?update', '?password', '?email', '?user', '?username',
    '?signin', '?auth', '?admin', '?portal', '?billing', '?payment', '?checkout', '?confirm', '?validate',
    'login=', 'verify=', 'secure=', 'account=', 'update=', 'password=', 'email=', 'user=', 'username=',
    
    # Query continuations
    'login&', 'verify&', 'secure&', 'account&', 'update&', 'password&', 'email&', 'user&', 'username&',
    
    # Direct indicators (expanded)
    'phish', 'scam', 'fake', 'test', 'demo', 'spam', 'fraud', 'hack', 'virus', 'malware', 'trojan',
    'suspicious', 'warning', 'alert', 'notification', 'message', 'important', 'urgent', 'action',
    
    # URL shorteners (expanded)
    'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'bitly.com', 'tiny.cc', 'is.gd', 'v.gd', 'ow.ly', 'buff.ly',
    'adf.ly', 'bc.vc', 'shorte.st', 'tinyurl', 'bit.do', 'mcaf.ee', 'rebrand.ly', 'bl.ink',
    
    # URL encoding (suspicious patterns)
    '%20', '%2F', '%3D', '%3F', '%22', '%27', '%3C', '%3E', '%28', '%29', '%5B', '%5D', '%7B', '%7D',
    '%40', '%23', '%24', '%25', '%5E', '%26', '%2A', '%2B', '%7C', '%5C',
    
    # Private/suspicious IP ranges
    '192.168.', '10.0.', '172.', '127.0.0.', 'localhost', '127.0.0.1', '0.0.0.0',
    
    # Protocol handlers (suspicious)
    'javascript:', 'data:', 'vbscript:', 'file:', 'ftp:', 'mailto:', 'tel:', 'sms:',
    
    # JavaScript events in URLs
    'onclick', 'onload', 'onmouseover', 'onsubmit', 'onchange', 'onfocus', 'onblur', 'onkeyup', 'onkeydown',
    
    # Common phishing keywords
    'free', 'win', 'prize', 'lottery', 'gift', 'reward', 'bonus', 'offer', 'deal', 'discount', 'sale',
    'covid', 'corona', 'virus', 'pandemic', 'vaccine', 'mask', 'quarantine', 'lockdown',
    'package', 'delivery', 'tracking', 'shipping', 'order', 'invoice', 'bill', 'payment', 'refund',
    'bank', 'credit', 'debit', 'card', 'account', 'balance', 'transaction', 'transfer', 'deposit',
    'suspend', 'disable', 'block', 'lock', 'restrict', 'limit', 'expire', 'invalid', 'error',
    'verify', 'confirm', 'validate', 'authenticate', 'authorize', 'approve', 'accept', 'agree',
    'click', 'here', 'now', 'immediately', 'urgent', 'important', 'critical', 'emergency',
    
    # More zero-day patterns
    'security', 'secure', 'protected', 'encrypted', 'ssl', 'https', 'certificate', 'trust', 'safe',
    'official', 'legitimate', 'genuine', 'authentic', 'real', 'original', 'verified', 'certified',
    
    # Emerging zero-day threats (2024-2026)
    # Cryptocurrency & NFT scams
    'crypto', 'bitcoin', 'ethereum', 'wallet', 'blockchain', 'nft', 'metamask', 'coinbase', 'binance',
    'defi', 'yield', 'staking', 'airdrop', 'mining', 'exchange', 'trading', 'portfolio', 'ledger',
    'trezor', 'coldwallet', 'hotwallet', 'seedphrase', 'privatekey', 'mnemonic', 'web3', 'dapp',
    
    # AI/ML phishing
    'chatgpt', 'gpt', 'openai', 'anthropic', 'claude', 'bard', 'gemini', 'midjourney', 'dalle',
    'stable-diffusion', 'ai-assistant', 'machine-learning', 'deep-learning', 'neural-network',
    
    # New social platforms
    'tiktok-shop', 'threads', 'bluesky', 'mastodon', 'truth-social', 'rumble', 'parler',
    
    # Government & benefit scams
    'stimulus', 'relief', 'unemployment', 'benefit', 'irs-refund', 'tax-return', 'social-security',
    'medicare', 'medicaid', 'obamacare', 'affordable-care', 'health-insurance', 'pension',
    
    # Remote work scams
    'remote-job', 'work-from-home', 'freelance', 'gig-economy', 'side-hustle', 'passive-income',
    'zoom-meeting', 'teams-meeting', 'slack-invite', 'discord-server', 'vpn-access',
    
    # Supply chain & vendor scams
    'vendor-portal', 'supplier-login', 'procurement', 'invoice-payment', 'po-number', 'purchase-order',
    'logistics', 'shipping-update', 'tracking-number', 'fedex-alert', 'ups-notification',
    
    # New suspicious TLDs (2024+)
    '.app', '.dev', '.io', '.ai', '.co', '.tech', '.digital', '.network', '.cloud', '.store', '.shop',
    '.blog', '.news', '.media', '.agency', '.studio', '.design', '.art', '.photo', '.video', '.music',
    '.game', '.play', '.live', '.stream', '.chat', '.social', '.community', '.group', '.team', '.club',
    
    # More typosquatting variations
    'g00g1e', 'g0og1e', 'googIe', 'g00gle', 'g0ogle', 'googl3', 'g00gl3', 'g0ogl3',
    'f4cebook', 'faceb0ok', 'f4ceb0ok', 'fac3book', 'f4c3book', 'facebo0k', 'f4cebo0k',
    '4m4zon', 'amaz0n', '4maz0n', 'amaz0n', '4mazon', 'amaz0n-prime', '4mazon-prime',
    'p4ypal', 'payp41', 'p4yp41', 'paypaI', 'p4ypaI', 'paypal-secure', 'p4ypal-secure',
    'm1cr0s0ft', 'micr0s0ft', 'm1cros0ft', 'micros0ft', 'm1crosoft', 'microsoft-365',
    'appl3', '4pple', 'appIe', '4ppIe', 'apple-id', '4pple-id', 'icloud-login', '1cloud-login',
    'n3tflix', 'netfIix', 'n3tfIix', 'netflix-account', 'n3tflix-account',
    '1nstagr4m', 'inst4gr4m', '1nsta', 'insta-login', '1nsta-login',
    'tw1tter', 'tw1tt3r', 't-witter', 'twitter-verify', 'tw1tter-verify',
    'y0utub3', 'youtub3', 'y0u-tub3', 'youtube-channel', 'y0utube-channel',
    'l1nkedin', 'link3din', 'l1nk3din', 'linkedin-profile', 'l1nkedin-profile',
    
    # New URL shorteners (2024+)
    'cutt.ly', 'shorturl.at', 'tiny.one', 'urlr.me', 'lnkd.in', 'bit.ly', 'tinyurl.com',
    'linktr.ee', 'bio.fm', 'campsite.bio', 'milkshake.app', 'flowcode.com',
    
    # Emerging brand impersonations
    'shopify-store', 'stripe-payment', 'square-pos', 'venmo-send', 'cashapp-receive',
    'zelle-transfer', 'wise-money', 'revolut-bank', 'n26-account', 'monzo-login',
    'starling-bank', 'chime-account', 'vanguard-invest', 'robinhood-trade', 'webull-stock',
    'etoro-trading', 'plus500-invest', 'ig-markets', 'avatrade-login',
    
    # Cloud service scams
    'aws-console', 'azure-portal', 'gcp-cloud', 'digitalocean-droplet', 'linode-server',
    'heroku-app', 'vercel-deploy', 'netlify-site', 'github-pages', 'gitlab-ci',
    
    # Gaming & esports scams
    'steam-trade', 'epic-games', 'ubisoft-connect', 'ea-origin', 'battlenet-login',
    'riot-games', 'valorant-account', 'league-legends', 'dota2-trade', 'csgo-skin',
    'fortnite-vbucks', 'minecraft-server', 'roblox-robux', 'genshin-impact',
    
    # Education & learning scams
    'coursera-cert', 'udemy-course', 'edx-degree', 'khan-academy', 'duolingo-plus',
    'skillshare-premium', 'masterclass-access', 'teachable-course', 'thinkific-login',
    
    # Health & wellness scams
    'fitbit-sync', 'myfitnesspal', 'strava-account', 'peloton-class', 'zwift-ride',
    'headspace-meditation', 'calm-app', 'noom-weight', 'weight-watchers',
    
    # Travel & booking scams
    'booking-com', 'airbnb-host', 'expedia-deal', 'tripadvisor-review', 'kayak-flight',
    'hotels-com', 'agoda-booking', 'vrbo-rental', 'getyourguide-tour',
    
    # Food delivery scams
    'doordash-order', 'ubereats-delivery', 'grubhub-pickup', 'postmates-food',
    'instacart-grocery', 'seamless-dine', 'deliveroo-meal',
    
    # Ride sharing scams
    'uber-ride', 'lyft-trip', 'bolt-drive', 'didi-chuxing', 'grab-taxi',
    
    # Dating app scams
    'tinder-match', 'bumble-date', 'hinge-profile', 'okcupid-account', 'match-com',
    'plentyoffish', 'zoosk-dating', 'eharmony-love', 'chemistry-com',
    
    # Real estate scams
    'zillow-offer', 'realtor-com', 'redfin-listing', 'apartments-com', 'craigslist-rent',
    'airbnb-guest', 'vrbo-owner', 'booking-com', 'hotels-com',
    
    # Insurance scams
    'geico-quote', 'progressive-policy', 'statefarm-claim', 'allstate-agent',
    'farmers-insurance', 'nationwide-coverage', 'liberty-mutual',
    
    # Utility scams
    'comcast-bill', 'verizon-account', 'att-service', 'tmobile-plan', 'spectrum-internet',
    'cox-cable', 'centurylink-fiber', 'earthlink-email', 'aol-mail',
    
    # More direct scam indicators
    'congratulations', 'winner', 'selected', 'chosen', 'lucky', 'fortunate',
    'exclusive', 'limited-time', 'time-sensitive', 'act-now', 'dont-miss',
    'last-chance', 'final-notice', 'deadline', 'expires-soon', 'ending-soon',
    'claim-now', 'redeem', 'collect', 'pickup', 'available-now',
]

# -----------------------------
# URL FEATURES
# -----------------------------
def extract_url_features(url):
    return [
        len(url),
        url.count('.'),
        url.count('-'),
        url.count('@'),
        url.count('/'),
        url.count('?'),
        url.count('='),
        1 if "https" in url else 0,
        1 if re.match(r"\d+\.\d+\.\d+\.\d+", url) else 0,
        int(any(word in url.lower() for word in [
            "login", "verify", "bank", "secure", "account", "update"
        ]))
    ]

# -----------------------------
# VISUAL SIMILARITY
# -----------------------------
def capture(url, path="temp.png"):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=6000)
            page.wait_for_timeout(2000)
            page.screenshot(path=path)
            browser.close()
        return True
    except:
        return False

def get_visual_score(url):
    try:
        if capture(url):
            h = imagehash.phash(Image.open("temp.png"))
            score = max([1 - (h - r)/64 for r in ref_hashes])
            return score
    except:
        pass
    return 0

# -----------------------------
# PREDICT FUNCTION
# -----------------------------
def predict_url(url, debug=False):
    # Extract domain
    domain = urlparse(url).netloc.lower()
    
    # Rule-based checks
    if domain in LEGITIMATE_DOMAINS:
        return "✅ Legitimate (Confidence: 0.95)"
    
    # Check for legitimate patterns - if URL contains legitimate patterns, be more lenient
    url_lower = url.lower()
    has_legitimate_patterns = any(pattern in url_lower for pattern in LEGITIMATE_PATTERNS)
    
    # Check for zero-day phishing patterns
    has_phishing_patterns = any(pattern in url_lower for pattern in PHISHING_PATTERNS)
    
    # If URL has legitimate patterns but no strong phishing indicators, don't flag as phishing
    if has_legitimate_patterns and not has_phishing_patterns:
        # Additional checks for suspicious domains even with legitimate patterns
        suspicious_indicators = 0
        
        # Check for domains with numbers (common typosquatting)
        if re.search(r'\d', domain) and not domain.replace('.', '').isdigit():
            suspicious_indicators += 1
        
        # Check for excessive hyphens in domain
        if domain.count('-') > 2:
            suspicious_indicators += 1
        
        # Check for mixed case in domain (suspicious)
        if domain != domain.lower() and domain != domain.upper():
            suspicious_indicators += 1
        
        # Check for very long domains
        if len(domain) > 50:
            suspicious_indicators += 1
        
        # Check for suspicious TLDs
        suspicious_tlds = ['.xyz', '.tk', '.ml', '.ga', '.cf', '.gq', '.top', '.club', '.online', '.site']
        if any(domain.endswith(tld) for tld in suspicious_tlds):
            suspicious_indicators += 1
        
        # Only flag as phishing if multiple suspicious indicators
        if suspicious_indicators >= 2:
            return "🚨 Phishing (Confidence: 0.95)"
        else:
            return "✅ Legitimate (Confidence: 0.80)"  # Lower confidence since domain is unknown
    
    # If phishing patterns found, flag as phishing
    if has_phishing_patterns:
        return "🚨 Phishing (Confidence: 0.95)"
    
    # Additional zero-day checks
    # Check for domains with numbers (common typosquatting)
    if re.search(r'\d', domain) and not domain.replace('.', '').isdigit():  # Has numbers but not pure IP
        return "🚨 Phishing (Confidence: 0.95)"
    
    # Check for excessive hyphens in domain
    if domain.count('-') > 2:
        return "🚨 Phishing (Confidence: 0.95)"
    
    # Check for mixed case in domain (suspicious)
    if domain != domain.lower() and domain != domain.upper():
        return "🚨 Phishing (Confidence: 0.95)"
    
    # Check for very long domains
    if len(domain) > 50:
        return "🚨 Phishing (Confidence: 0.95)"
    
    # Additional zero-day checks
    # Check for URLs with multiple suspicious keywords
    suspicious_keywords = ['phish', 'scam', 'fake', 'fraud', 'hack', 'virus', 'malware', 'trojan', 
                          'suspicious', 'warning', 'alert', 'urgent', 'prize', 'lottery', 'winner',
                          'free-money', 'bitcoin-scam', 'crypto-scam', 'login', 'verify', 'secure', 'account']
    keyword_count = sum(1 for keyword in suspicious_keywords if keyword in url_lower)
    if keyword_count >= 3:
        return "🚨 Phishing (Confidence: 0.95)"
    
    # Check for extremely long URLs (often used in phishing)
    if len(url) > 200:
        return "🚨 Phishing (Confidence: 0.95)"
    
    # Check for URLs with many special characters
    special_chars = url.count('@') + url.count('?') + url.count('&') + url.count('=') + url.count('%')
    if special_chars > 10:
        return "🚨 Phishing (Confidence: 0.95)"
    
    # Check for domains that look like email addresses
    if '@' in domain:
        return "🚨 Phishing (Confidence: 0.95)"
    
    # TF-IDF
    X_tfidf = tfidf.transform([url])

    # URL features
    url_feat = np.array([extract_url_features(url)])

    # Combine base
    X_base = hstack([X_tfidf, url_feat])

    # Visual similarity score
    score = get_visual_score(url)
    visual_features = np.array([[score]])

    # Combine all
    X_final = hstack([X_base, visual_features])

    # Convert to CSR format
    X_final = X_final.tocsr()

    expected = model.n_features_in_
    current = X_final.shape[1]

    if current < expected:
        diff = expected - current
        X_final = hstack([X_final, np.zeros((1, diff))])
    elif current > expected:
        X_final = X_final[:, :expected]

    if debug:
        print(f"X_tfidf: {X_tfidf.shape}, url_feat: {url_feat.shape}, visual: {visual_features.shape}")
        print(f"Expected features: {expected}, Got: {current}")

    # PREDICTION 
    proba = model.predict_proba(X_final)[0]
    prob_class0 = proba[0]    # Class 0 (Legitimate)
    prob_class1 = proba[1]    # Class 1 (Phishing)
    
    if debug:
        print(f"Class 0: {prob_class0:.4f}, Class 1: {prob_class1:.4f}")
    
    # Use 0.85 threshold (requires 85% confidence for phishing)
    if prob_class1 >= 0.85:
        return f"🚨 Phishing (Confidence: {prob_class1:.2f})"
    else:
        return f"✅ Legitimate (Confidence: {prob_class0:.2f})"

# -----------------------------
# MAIN LOOP
# -----------------------------
if __name__ == "__main__":
    print("\n🔍 PHISHING URL DETECTOR")
    print("=" * 35)

    while True:
        url = input("\nEnter URL (or type 'exit'): ")

        if url.lower() == "exit":
            print("👋 Exiting...")
            break

        result = predict_url(url)
        print("Result:", result)