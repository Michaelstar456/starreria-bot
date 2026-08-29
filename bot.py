import cloudscraper
import time
import schedule
import os
from datetime import datetime
import requests

# ============================================================
# CONFIGURATION — EDIT THESE
# ============================================================

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "YOUR_WEBHOOK_URL_HERE")

SITES = {
    "🃏 Chaos Cards — Pitch Black Booster Bundle": {
        "url": "https://www.chaoscards.co.uk/prod/booster-packs-pokemon/pokemon-mega-evolution-pitch-black-booster-bundle",
        "in_stock_text": "Add to Basket",
        "out_stock_text": "Out of Stock",
        "in_stock": False,
    },
    "🃏 Chaos Cards — Pitch Black Booster Box": {
        "url": "https://www.chaoscards.co.uk/prod/booster-boxes-pokemon/pokemon-mega-evolution-pitch-black-booster-box-36-packs",
        "in_stock_text": "Add to Basket",
        "out_stock_text": "Out of Stock",
        "in_stock": False,
    },
    "🃏 Chaos Cards — Pitch Black Elite Trainer Box": {
        "url": "https://www.chaoscards.co.uk/prod/elite-trainer-boxes-pokemon/pokemon-mega-evolution-pitch-black-elite-trainer-box",
        "in_stock_text": "Add to Basket",
        "out_stock_text": "Out of Stock",
        "in_stock": False,
    },
    "🃏 Chaos Cards — Pitch Black Booster Pack": {
        "url": "https://www.chaoscards.co.uk/prod/booster-packs-pokemon/pokemon-mega-evolution-pitch-black-booster-pack-10-cards",
        "in_stock_text": "Add to Basket",
        "out_stock_text": "Out of Stock",
        "in_stock": False,
    },
    "🃏 Chaos Cards — Chaos Rising Booster Pack": {
        "url": "https://www.chaoscards.co.uk/prod/booster-packs-pokemon/pokemon-mega-evolution-chaos-rising-booster-pack-10-cards",
        "in_stock_text": "Add to Basket",
        "out_stock_text": "Out of Stock",
        "in_stock": False,
    },
    "🃏 Chaos Cards — Chaos Rising Booster Bundle": {
        "url": "https://www.chaoscards.co.uk/prod/booster-packs-pokemon/pokemon-mega-evolution-chaos-rising-booster-bundle",
        "in_stock_text": "Add to Basket",
        "out_stock_text": "Out of Stock",
        "in_stock": False,
    },
    "🃏 Chaos Cards — Chaos Rising Elite Trainer Box": {
        "url": "https://www.chaoscards.co.uk/prod/elite-trainer-boxes-pokemon/pokemon-mega-evolution-chaos-rising-elite-trainer-box",
        "in_stock_text": "Add to Basket",
        "out_stock_text": "Out of Stock",
        "in_stock": False,
    },
    "🃏 Chaos Cards — Chaos Rising Booster Box": {
        "url": "https://www.chaoscards.co.uk/prod/booster-boxes-pokemon/pokemon-mega-evolution-chaos-rising-booster-box-36-packs",
        "in_stock_text": "Add to Basket",
        "out_stock_text": "Out of Stock",
        "in_stock": False,
    },
    "🎮 Pokemon Center UK": {
        "url": "https://www.pokemoncenter.com/en-gb",
        "in_stock_text": "Add to Cart",
        "out_stock_text": None,
        "in_stock": False,
    },
}

# ============================================================
# DISCORD FUNCTIONS
# ============================================================

def send_discord_message(content):
    """Send a message to Discord webhook"""
    try:
        response = requests.post(
            DISCORD_WEBHOOK,
            json={"content": content},
            timeout=10
        )
        if response.status_code == 204:
            print(f"✅ Discord message sent")
        else:
            print(f"❌ Discord error: {response.status_code} — {response.text}")
    except Exception as e:
        print(f"❌ Discord failed: {e}")

def send_restock_alert(site_name, url):
    send_discord_message(
        f"@everyone\n"
        f"🚨 **RESTOCK ALERT** 🚨\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"**{site_name}**\n"
        f"✅ Back in stock!\n"
        f"🔗 {url}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ Be quick — these sell fast!"
    )

def send_startup_message():
    sites_list = "\n".join([f"• {name}" for name in SITES.keys()])
    send_discord_message(
        f"🤖 **Starreria Restock Bot Online**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ Monitoring {len(SITES)} sites\n"
        f"⏰ Checking every 5 minutes\n"
        f"📅 Started: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"**Sites monitored:**\n{sites_list}"
    )

def send_daily_status():
    status_lines = "\n".join([
        f"{'✅' if data['in_stock'] else '❌'} {name}"
        for name, data in SITES.items()
    ])
    send_discord_message(
        f"💚 **Daily Status Update**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{status_lines}"
    )

# ============================================================
# CHECKING FUNCTIONS
# ============================================================

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'mobile': False
    }
)

def check_site(site_name, site_data):
    try:
        response = scraper.get(site_data["url"], timeout=20)
        now = datetime.now().strftime('%H:%M:%S')
        page_text = response.text

        # Determine stock status
        is_in_stock = site_data["in_stock_text"] in page_text
        if site_data["out_stock_text"] and site_data["out_stock_text"] in page_text:
            is_in_stock = False

        status = "✅ IN STOCK" if is_in_stock else "❌ Out of Stock"
        print(f"[{now}] {site_name}: {status}")

        # Only alert on change from out of stock to in stock
        if is_in_stock and not site_data["in_stock"]:
            site_data["in_stock"] = True
            send_restock_alert(site_name, site_data["url"])
        elif not is_in_stock and site_data["in_stock"]:
            site_data["in_stock"] = False

    except Exception as e:
        print(f"⚠️ Error checking {site_name}: {e}")

def check_all_sites():
    print(f"\n{'='*50}")
    print(f"🔍 Checking all sites — {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*50}")
    for site_name, site_data in SITES.items():
        check_site(site_name, site_data)
        time.sleep(5)

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("🤖 Starreria Restock Bot Starting...")

    if DISCORD_WEBHOOK == "YOUR_WEBHOOK_URL_HERE":
        print("❌ ERROR: Please set your DISCORD_WEBHOOK environment variable!")
        exit(1)

    send_startup_message()
    check_all_sites()

    schedule.every(5).minutes.do(check_all_sites)
    schedule.every().day.at("09:00").do(send_daily_status)

    print("\n✅ Bot running — checking every 5 minutes")

    while True:
        schedule.run_pending()
        time.sleep(1)
