import asyncio
import os
import re
from telethon import TelegramClient, events
from pybit.unified_trading import HTTP
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# ============ TELEGRAM CONFIG ============
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
CHANNEL_ID = int(os.getenv("TELEGRAM_CHANNEL_ID"))

# ============ BYBIT CONFIG ============
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")
TESTNET = os.getenv("TESTNET", "false").lower() == "true"

# ============ TRADING MODE CONFIG ============
# Режими: "MIRROR", "FIXED", "ALL_IN"
TRADING_MODE = os.getenv("TRADING_MODE", "MIRROR").upper()

# За FIXED режим
FIXED_AMOUNT_USDT = float(os.getenv("FIXED_AMOUNT_USDT", "100"))
FIXED_AMOUNT_ETH = float(os.getenv("FIXED_AMOUNT_ETH", "0.04"))

# За ALL_IN режим (процент од балансот да се користи)
ALL_IN_PERCENTAGE = float(os.getenv("ALL_IN_PERCENTAGE", "0.95"))  # 95% од балансот

# Иницијализирај Bybit
bybit = HTTP(
    testnet=TESTNET,
    api_key=BYBIT_API_KEY,
    api_secret=BYBIT_API_SECRET
)

# Иницијализирај Telegram клиент
client = TelegramClient('trading_session', API_ID, API_HASH)

# ============ HELPER FUNCTIONS ============
def get_usdt_balance():
    """Земи USDT баланс од Bybit"""
    try:
        response = bybit.get_wallet_balance(accountType="UNIFIED", coin="USDT")
        balance = float(response['result']['list'][0]['coin'][0]['walletBalance'])
        return balance
    except Exception as e:
        print(f"❌ Error getting USDT balance: {e}")
        return 0.0

def get_eth_balance():
    """Земи ETH баланс од Bybit"""
    try:
        response = bybit.get_wallet_balance(accountType="UNIFIED", coin="ETH")
        balance = float(response['result']['list'][0]['coin'][0]['walletBalance'])
        return balance
    except Exception as e:
        print(f"❌ Error getting ETH balance: {e}")
        return 0.0

def get_eth_price():
    """Земи тековна ETH цена"""
    try:
        response = bybit.get_tickers(category="spot", symbol="ETHUSDT")
        price = float(response['result']['list'][0]['lastPrice'])
        return price
    except Exception as e:
        print(f"❌ Error getting ETH price: {e}")
        return 0.0

# ============ SIGNAL PARSER ============
def parse_signal(message_text):
    """Парсира signal од Telegram порака"""
    try:
        signal = {}
        
        # Signal number
        signal_match = re.search(r'SIGNAL #(\d+)', message_text)
        signal['signal_number'] = int(signal_match.group(1)) if signal_match else 0
        
        # Category
        category_match = re.search(r'Category:\s*(\w+)', message_text)
        signal['category'] = category_match.group(1) if category_match else 'linear'
        
        # Symbol
        symbol_match = re.search(r'Symbol:\s*(\w+)', message_text)
        signal['symbol'] = symbol_match.group(1) if symbol_match else None
        
        # Side
        side_match = re.search(r'Side:\s*(\w+)', message_text)
        signal['side'] = side_match.group(1) if side_match else None
        
        # OrderType
        order_match = re.search(r'OrderType:\s*(\w+)', message_text)
        signal['order_type'] = order_match.group(1) if order_match else 'Market'
        
        # Quantity (од signal)
        qty_match = re.search(r'Quantity:\s*([\d.]+)', message_text)
        signal['signal_qty'] = float(qty_match.group(1)) if qty_match else None
        
        if not signal['symbol'] or not signal['side']:
            return None
            
        return signal
        
    except Exception as e:
        print(f"❌ Parse error: {e}")
        return None

# ============ QUANTITY CALCULATOR ============
def calculate_quantity(signal):
    """
    Пресметај колку да трговува според режимот
    
    MIRROR: Користи ја количината од signal
    FIXED: Користи fixed amount од .env
    ALL_IN: Користи го целиот баланс (или процент)
    """
    
    symbol = signal['symbol']
    side = signal['side']
    signal_qty = signal.get('signal_qty', 0)
    
    print(f"\n{'─'*40}")
    print(f"📊 CALCULATING QUANTITY")
    print(f"   Mode: {TRADING_MODE}")
    print(f"   Side: {side}")
    print(f"   Signal Qty: {signal_qty}")
    
    # ========== MODE 1: MIRROR (исто како сигналот) ==========
    if TRADING_MODE == "MIRROR":
        qty = signal_qty
        print(f"   ✅ Using signal quantity: {qty}")
        return qty
    
    # ========== MODE 2: FIXED (фиксна количина) ==========
    elif TRADING_MODE == "FIXED":
        if side == "Buy":
            # Купуваме ETH за USDT
            eth_price = get_eth_price()
            if eth_price > 0:
                qty = FIXED_AMOUNT_USDT / eth_price
                print(f"   💵 USDT to spend: ${FIXED_AMOUNT_USDT}")
                print(f"   💰 ETH price: ${eth_price:.2f}")
                print(f"   ✅ ETH to buy: {qty:.6f}")
                return qty
            else:
                print(f"   ❌ Could not get ETH price")
                return 0
        
        elif side == "Sell":
            # Продаваме ETH
            qty = FIXED_AMOUNT_ETH
            print(f"   ✅ ETH to sell: {qty:.6f}")
            return qty
    
    # ========== MODE 3: ALL_IN (целиот баланс) ==========
    elif TRADING_MODE == "ALL_IN":
        if side == "Buy":
            # Купуваме ETH - користи го целиот USDT баланс
            usdt_balance = get_usdt_balance()
            usdt_to_use = usdt_balance * ALL_IN_PERCENTAGE
            
            eth_price = get_eth_price()
            if eth_price > 0:
                qty = usdt_to_use / eth_price
                print(f"   💵 USDT balance: ${usdt_balance:.2f}")
                print(f"   💵 USDT to use ({ALL_IN_PERCENTAGE*100}%): ${usdt_to_use:.2f}")
                print(f"   💰 ETH price: ${eth_price:.2f}")
                print(f"   ✅ ETH to buy: {qty:.6f}")
                return qty
            else:
                print(f"   ❌ Could not get ETH price")
                return 0
        
        elif side == "Sell":
            # Продаваме ETH - користи го целиот ETH баланс
            eth_balance = get_eth_balance()
            qty = eth_balance * ALL_IN_PERCENTAGE
            print(f"   💎 ETH balance: {eth_balance:.6f}")
            print(f"   ✅ ETH to sell ({ALL_IN_PERCENTAGE*100}%): {qty:.6f}")
            return qty
    
    print(f"   ❌ Unknown mode or error")
    print(f"{'─'*40}\n")
    return 0

# ============ TRADE EXECUTION ============
def execute_trade(signal):
    """Извршува трговија на Bybit"""
    try:
        # Пресметај ја количината според режимот
        qty = calculate_quantity(signal)
        
        if qty <= 0:
            print(f"❌ Invalid quantity: {qty}")
            return None
        
        print(f"\n{'='*60}")
        print(f"🚀 EXECUTING TRADE #{signal['signal_number']}")
        print(f"{'='*60}")
        print(f"   Symbol: {signal['symbol']}")
        print(f"   Side: {signal['side']}")
        print(f"   Quantity: {qty:.6f}")
        print(f"   Category: {signal['category']}")
        print(f"   Mode: {TRADING_MODE}")
        print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
        
        # Изврши order
        response = bybit.place_order(
            category=signal['category'],
            symbol=signal['symbol'],
            side=signal['side'],
            orderType=signal['order_type'],
            qty=str(qty)
        )
        
        if response['retCode'] == 0:
            order_id = response['result']['orderId']
            print(f"✅ Order placed successfully!")
            print(f"   Order ID: {order_id}")
        else:
            print(f"❌ Order failed: {response['retMsg']}")
            
        print(f"{'='*60}\n")
        return response
        
    except Exception as e:
        print(f"❌ Execution error: {e}")
        return None

# ============ EVENT HANDLER ============
@client.on(events.NewMessage(chats=CHANNEL_ID))
async def handle_new_message(event):
    """Слуша нови пораки од каналот"""
    message = event.message.text
    
    if not message:
        return
    
    print(f"📨 New message from channel")
    
    # Провери дали е signal
    if "SIGNAL #" in message:
        signal = parse_signal(message)
        
        if signal:
            print(f"✅ Valid signal detected!")
            execute_trade(signal)
        else:
            print(f"⚠️ Failed to parse signal")

# ============ MAIN ============
async def main():
    """Стартува listener"""
    print(f"\n{'='*60}")
    print(f"🤖 TRADING SIGNAL LISTENER")
    print(f"{'='*60}")
    print(f"   Trading Mode: {TRADING_MODE}")
    
    if TRADING_MODE == "FIXED":
        print(f"   Fixed USDT: ${FIXED_AMOUNT_USDT}")
        print(f"   Fixed ETH: {FIXED_AMOUNT_ETH}")
    elif TRADING_MODE == "ALL_IN":
        print(f"   All-In %: {ALL_IN_PERCENTAGE*100}%")
    
    print(f"   Channel: {CHANNEL_ID}")
    print(f"   Bybit: {'TESTNET' if TESTNET else 'MAINNET'}")
    print(f"{'='*60}\n")
    
    # Конектирај се на Telegram
    await client.start()
    
    # Земи го твојот Telegram ID
    me = await client.get_me()
    print(f"✅ Logged in as: {me.first_name} (@{me.username})")
    print(f"🎧 Listening for signals...\n")
    
    # Слушај бесконечно
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Stopped by user")
