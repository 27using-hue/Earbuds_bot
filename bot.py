import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from groq import Groq

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)

PRODUCTS = """
Boat Airdopes 141 – ₹1,299
Noise Buds VS104 – ₹1,499
Boult Audio AirBass Z40 – ₹1,399
Realme Buds Q2 – ₹2,499
Redmi Earbuds 3 Lite – ₹1,799
pTron Bassbuds Jade – ₹1,099
Zebronics Zeb-Sound Bomb 1 – ₹1,299
Skullcandy Dime 2 – ₹2,799
Oppo Enco Buds 2 – ₹1,999
OnePlus Nord Buds CE – ₹2,299
JBL Wave 100TWS – ₹2,999
Sony WF-C500 – ₹4,999
Samsung Galaxy Buds Live – ₹5,999
Boat Airdopes 441 Pro – ₹2,499
Noise Air Buds Pro – ₹2,799
Boult Audio ProBass X1 – ₹1,599
Realme Buds Air 3 Neo – ₹2,999
Redmi Buds 4 Active – ₹1,399
pTron Bassbuds Duo – ₹1,199
Wings Phantom 210 – ₹1,499
Fire-Boltt Ninja Buds 601 – ₹1,299
Ambrane Dots Slay – ₹1,199
Mivi DuoPods A350 – ₹1,799
Crossbeats Pebble – ₹3,499
Soundcore Life Note E – ₹2,999
JBL Tune 230NC – ₹6,999
Sony WF-XB700 – ₹7,999
Samsung Galaxy Buds 2 – ₹8,999
OnePlus Buds Z2 – ₹4,999
Oppo Enco Air 3 Pro – ₹9,999
"""

SYSTEM_PROMPT = f"""Tu ek friendly aur helpful sales agent hai "EarBuds Shop" ka.
Tu Hinglish mein baat karta hai — Hindi aur English ka mix, jaise dosti mein bolta hai.
Kabhi formal mat ban, always casual aur warm reh.

PRODUCT CATALOG:
{PRODUCTS}

TERA KAAM:
1. Customer ki zaroorat samjh — budget, use case (gym, office, gaming, music), brand preference
2. Best 2-3 options suggest kar
3. Price compare kar agar pooche
4. Order karne mein help kar — bata ke "Order karne ke liye apna address aur UPI/COD preference bhejo"

TONE RULES:
- Hinglish mein baat kar: "Bhai kya budget hai?", "Yaar ye wala best hai!", "Ekdum sahi choice!"
- Emojis freely use kar: 🎧 🔥 💯 😎 ✅
- Short punchy messages — Telegram style
- Never robotic mat ban

IMPORTANT:
- Sirf catalog ke products suggest karo
- Budget under 2000 → budget options dikhao
- ANC maange → JBL Tune 230NC, Samsung Galaxy Buds 2, OnePlus Buds Z2 suggest karo
- Bass chahiye → Boat, Boult, Sony WF-XB700, JBL suggest karo
- Premium → Sony, Samsung, JBL, Oppo Enco Air 3 Pro
- Har message ke end mein helpful next step guide karo
- Max 4-5 lines, Telegram style
"""

# Store conversation history per user
user_histories = {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_msg = update.message.text

    if user_id not in user_histories:
        user_histories[user_id] = []

    user_histories[user_id].append({
        "role": "user",
        "content": user_msg
    })

    # Keep only last 10 messages to save memory
    if len(user_histories[user_id]) > 10:
        user_histories[user_id] = user_histories[user_id][-10:]

    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *user_histories[user_id]
            ],
            max_tokens=500,
            temperature=0.7
        )

        reply = response.choices[0].message.content

        user_histories[user_id].append({
            "role": "assistant",
            "content": reply
        })

        await update.message.reply_text(reply)

    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text("Ek second bhai, kuch issue aa gaya 😅 Dobara try karo!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Heyyy! 👋 Swagat hai *EarBuds Shop* mein! 🎧🔥\n\n"
        "Main hun tera personal earbuds advisor 😎\n"
        "Bata bhai — kya dhundh raha hai? Budget kitna hai? 💰",
        parse_mode="Markdown"
    )

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    from telegram.ext import CommandHandler
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot chal raha hai! 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()
