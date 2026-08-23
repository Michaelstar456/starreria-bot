import requests
from bs4 import BeautifulSoup
import time
import schedule
import os
from datetime import datetime

# ============================================================
# CONFIGURATION — EDIT THESE
# ============================================================

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "YOUR_WEBHOOK_URL_HERE")

# Add or remove sites here
# "check_text" = text that appears on page WHEN IN STOCK
# "out_text" = text that appears WHEN OUT OF STOCK (optional)

SITES = {
    "🃏 Chaos Cards — Pitch Black Ex Box": {
        "url": "https://www.chaoscards.co.uk/prod/pokemon-tcg-pitch-black-ex-booster-box-japanese",
        "check_text": "Add to Basket",
        "out_text": "Out of Stock",
        "in_stock": False,
        "last_checked": None
    },
    "🃏 Chaos Cards — Stellar Miracle Box": {
        "url": "https://www.chaoscards.co.uk/prod/pokemon-tcg-stellar-miracle-booster-box-japanese",
        "check_text": "Add to Basket",
        "out_text": "Out of Stock",
        "in_stock": False,
        "last_checked": None
    },
    "🃏 Chaos Cards — Abyss Eye Box": {
        "url": "https://www.chaoscards.co.uk/prod/pokemon-tcg-abyss-eye-booster-box-japanese",
        "check_text": "Add to Basket",
        "out_text": "Out of Stock",
        "in_stock": False,
        "last_checked": None
    },
    "🎮 Pokemon Center UK — Queue": {
        "url": "https://www.pokemoncenter.com/en-gb",
        "check_text": "Join Queue",
        "out_text": None,
        "in_stock": False,
        "last_checked": None
    },
    "🃏 Total Cards — Booster Boxes": {
        "url": "https://www.totalcards.net/catalogsearch/result/?q=pokemon+booster+box+japanese",
        "check_text": "Add to Cart",
        "out_text": "Out of Stock",
        "in_stock": False,
        "last_checked": None
    },
    "🃏 Big Orbit Cards": {
        "url": "https://www.bigorbitcards.co.uk/collections/pokemon-booster-boxes",
        "check_text": "Add to cart",
        "out_text": "Sold out",
        "in_stock": False,
        "last_checked": None
    }
}

# ============================================================
# BOT FUNCTIONS
# ============================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def send_discord_alert(site_name, url, back_in_stock=True):
    if back_in_stock:
        message = {
            "content": (
                f"@everyone\n"
                f"🚨 **RESTOCK ALERT** 🚨\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"**{site_name}**\n"
                f"✅ Back in stock!\n"
                f"🔗 {url}\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"⚡ Be quick — these sell fast!"
            )
        }
    else:
        message = {
            "content": (
                f"📢 **STOCK UPDATE**\n"
                f"**{site_name}** is now out of stock."
            )
        }
    
    try:
        response = requests.post(DISCORD_WEBHOOK, json=message)
        if response.status_code == 204:
            print(f"✅ Discord alert sent for {site_name}")
        else:
            print(f"❌ Discord alert failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to send Discord alert: {e}")

def send_startup_message():
    message = {
        "content": (
            f"🤖 **Starreria Restock Bot Online**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ Monitoring {len(SITES)} sites\n"
            f"⏰ Checking every 5 minutes\n"
            f"📅 Started: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Sites being monitored:\n" +
            "\n".join([f"• {name}" for name in SITES.keys()])
        )
    }
    try:
        requests.post(DISCORD_WEBHOOK, json=message)
        print("✅ Startup message sent to Discord")
    except Exception as e:
        print(f"❌ Failed to send startup message: {e}")

def check_site(site_name, site_data):
    try:
        response = requests.get(
            site_data["url"],
            headers=HEADERS,
            timeout=15
        )
        
        now = datetime.now().strftime('%H:%M:%S')
        site_data["last_checked"] = now
        
        page_text = response.text
        is_in_stock = site_data["check_text"] in page_text
        
        # Check if out of stock text overrides
        if site_data["out_text"] and site_data["out_text"] in page_text:
            is_in_stock = False
        
        print(f"[{now}] {site_name}: {'✅ IN STOCK' if is_in_stock else '❌ Out of Stock'}")
        
        # Only alert on STATUS CHANGE — no spam
        if is_in_stock and not site_data["in_stock"]:
            # Was out of stock, now in stock — ALERT
            site_data["in_stock"] = True
            send_discord_alert(site_name, site_data["url"], back_in_stock=True)
            
        elif not is_in_stock and site_data["in_stock"]:
            # Was in stock, now out of stock
            site_data["in_stock"] = False
            print(f"📦 {site_name} is now out of stock")

    except requests.exceptions.Timeout:
        print(f"⚠️ Timeout checking {site_name}")
    except requests.exceptions.ConnectionError:
        print(f"⚠️ Connection error checking {site_name}")
    except Exception as e:
        print(f"⚠️ Error checking {site_name}: {e}")

def check_all_sites():
    print(f"\n{'='*50}")
    print(f"🔍 Running checks at {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*50}")
    
    for site_name, site_data in SITES.items():
        check_site(site_name, site_data)
        time.sleep(5)  # 5 second gap between sites — respectful crawling

def send_status_update():
    # Sends a daily status update to Discord so you know bot is alive
    message = {
        "content": (
            f"💚 **Bot Status Update**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ Bot is running normally\n"
            f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
            f"🔍 Monitoring {len(SITES)} sites every 5 minutes\n"
            f"━━━━━━━━━━━━━━━━━━━━\n" +
            "\n".join([
                f"{'✅' if data['in_stock'] else '❌'} {name}"
                for name, data in SITES.items()
            ])
        )
    }
    try:
        requests.post(DISCORD_WEBHOOK, json=message)
        print("✅ Daily status update sent")
    except Exception as e:
        print(f"❌ Failed to send status update: {e}")

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("🤖 Starreria Restock Bot Starting...")
    print(f"📡 Monitoring {len(SITES)} sites")
    print(f"⏰ Check interval: 5 minutes")
    
    # Send startup message to Discord
    send_startup_message()
    
    # Run first check immediately
    check_all_sites()
    
    # Schedule checks every 5 minutes
    schedule.every(5).minutes.do(check_all_sites)
    
    # Daily status update at 9am
    schedule.every().day.at("09:00").do(send_status_update)
    
    print("\n✅ Bot is running — press CTRL+C to stop")
    
    while True:
        schedule.run_pending()
        time.sleep(1)
