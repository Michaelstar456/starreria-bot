# Starreria Restock Bot

Monitors Pokémon card sites and sends Discord alerts when items restock.

## Setup Instructions

### Step 1 — Create Discord Webhook
1. Open your Discord server
2. Go to the channel you want alerts in
3. Click ⚙️ Edit Channel → Integrations → Webhooks
4. Click "New Webhook"
5. Name it "Restock Bot"
6. Copy the webhook URL

### Step 2 — Deploy to Railway
1. Create account at railway.app
2. Click "New Project"
3. Click "Deploy from GitHub repo"
4. Upload these files to a GitHub repo first
5. Select your repo
6. Railway auto-detects Python

### Step 3 — Add Webhook URL
1. In Railway, go to your project
2. Click "Variables"
3. Add new variable:
   - Name: DISCORD_WEBHOOK
   - Value: (paste your webhook URL)
4. Railway restarts automatically

### Step 4 — Deploy
1. Click Deploy
2. Bot starts automatically
3. Check Discord for startup message

## Adding New Sites
Open bot.py and add to the SITES dictionary:

```python
"Site Name": {
    "url": "https://website.com/product-page",
    "check_text": "Add to Basket",  # Text when IN STOCK
    "out_text": "Out of Stock",      # Text when OUT OF STOCK
    "in_stock": False,
    "last_checked": None
}
```

## How to find check_text
1. Visit the product page
2. Right click → Inspect Element
3. Find the Add to Cart/Basket button
4. Copy the exact button text
5. Paste into check_text

## Sites Currently Monitored
- Chaos Cards — Pitch Black Ex
- Chaos Cards — Stellar Miracle
- Chaos Cards — Abyss Eye
- Pokemon Center UK Queue
- Total Cards
- Big Orbit Cards
