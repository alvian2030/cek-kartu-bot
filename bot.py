from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os

TOKEN = os.getenv("BOT_TOKEN")

def luhn_check(card_number):
    total = 0
    reverse_digits = card_number[::-1]
    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0

def get_bin_info(card_number):
    bin_number = card_number[:6]
    try:
        response = requests.get(f'https://lookup.binlist.net/{bin_number}')
        if response.status_code == 200:
            data = response.json()
            return f"""
💳 BIN Info:
Bank: {data.get('bank', {}).get('name', 'Unknown')}
Brand: {data.get('scheme', 'Unknown').title()}
Type: {data.get('type', 'Unknown').title()}
Country: {data.get('country', {}).get('name', 'Unknown')}
"""
        else:
            return "🔍 BIN info tidak ditemukan."
    except:
        return "⚠️ Gagal mengambil data BIN."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Selamat datang! Kirim nomor kartu kredit (tanpa spasi) untuk dicek validitas dan info BIN-nya.")

async def check_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    card = update.message.text.strip().replace(" ", "")
    if not card.isdigit() or len(card) < 12:
        await update.message.reply_text("❌ Nomor tidak valid. Harap masukkan nomor kartu (hanya angka).")
        return

    result = "✅ Nomor valid (Lulus Luhn Check)" if luhn_check(card) else "❌ Nomor tidak valid (Gagal Luhn Check)"
    bin_info = get_bin_info(card)
    await update.message.reply_text(f"{result}\n{bin_info}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_card))
    app.run_polling()

if __name__ == "__main__":
    main()
