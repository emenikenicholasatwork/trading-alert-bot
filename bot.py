import os
import aiohttp
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, Application, MessageHandler, ConversationHandler, filters

load_dotenv()
BOT_TOKEN=os.getenv("BOT_TOKEN")
ALPHA_VANTAGE_API_KEY=os.getenv("ALPHA_VANTAGE_API_KEY")
SET_PAIR=1

async def start (update: Update, context: ContextTypes.DEFAULT_TYPE):
     keyboard = [
         [
             InlineKeyboardButton("Set Alert", callback_data='set_alert'),
             InlineKeyboardButton("View Alerts", callback_data='view_alerts')
         ],
         [
             InlineKeyboardButton("Delete Alert", callback_data='delete_alert'),
         ]
     ]
     reply_markup = InlineKeyboardMarkup(keyboard)
     await update.message.reply_text("👋 Hello! I’m your Alert bot.\nI will keep you updated on various price levels.", reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Commands:\n/setalert\n/alerts\n/deletealert")

async def set_alert(udpate: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Cancel", callback_data='cancel')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await udpate.effective_chat.send_message(text="Enter Currency pair e.g XAU/USD =>", reply_markup=reply_markup, parse_mode="Markdown")
    return SET_PAIR

async def handle_currency_pair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pair = update.message.text.strip().upper()
    await update.message.reply_text(f"✅ Alert set for `{pair}`", parse_mode="Markdown")
    return ConversationHandler.END

async def cancle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("Operation Cancel")
    return ConversationHandler.END

async def get_asset_price(pair: str):
    base, quote = pair.split('/')
    url=f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={base}&to_currency={quote}&apikey={ALPHA_VANTAGE_API_KEY}"

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'set_alert':
        await query.delete_message()
        await set_alert(update, context)
    elif query.data == 'view_alerts':
        await query.delete_message()
        await query.edit_message_text("You chose: 🔔 View Alerts")
    elif query.data == 'cancel':
        await query.delete_message()
        await query.edit_message_text("Operation canceled.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    conv_handler = ConversationHandler(entry_points=[CallbackQueryHandler(set_alert,pattern='^set_alert$')],
                                       states={
                                           SET_PAIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_currency_pair)],
                                       },
                                       fallbacks=[CallbackQueryHandler(cancle, pattern='^cancel$')],)
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(button_handler))


    print("🤖 Bot is running...")
    app.run_polling()