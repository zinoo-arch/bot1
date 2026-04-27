import os
import json
import logging
from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
from telegram.error import TelegramError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")
CHANNELS_FILE = "channels.json"

bot = Bot(token=TOKEN)
app = Application.builder().token(TOKEN).build()

def load_channels():
    if os.path.exists(CHANNELS_FILE):
        with open(CHANNELS_FILE, "r") as f:
            return json.load(f)
    return {"source": [], "target": []}

def save_channels(data):
    with open(CHANNELS_FILE, "w") as f:
        json.dump(data, f, indent=2)

async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channels = load_channels()
    
    if not context.args:
        await update.message.reply_text("لطفا یوزرنیم کانال را ارسال کنید\nمثال: /add @channelname")
        return
    
    channel_id = context.args[0]
    
    if channel_id not in channels["source"]:
        channels["source"].append(channel_id)
        save_channels(channels)
        await update.message.reply_text(f"✅ کانال {channel_id} اضافه شد")
    else:
        await update.message.reply_text(f"⚠️ کانال {channel_id} قبلا اضافه شده است")

async def remove_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channels = load_channels()
    
    if not context.args:
        await update.message.reply_text("لطفا یوزرنیم کانال را ارسال کنید\nمثال: /remove @channelname")
        return
    
    channel_id = context.args[0]
    
    if channel_id in channels["source"]:
        channels["source"].remove(channel_id)
        save_channels(channels)
        await update.message.reply_text(f"✅ کانال {channel_id} حذف شد")
    else:
        await update.message.reply_text(f"⚠️ کانال {channel_id} یافت نشد")

async def set_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channels = load_channels()
    
    if not context.args:
        await update.message.reply_text("لطفا یوزرنیم کانال مقصد را ارسال کنید\nمثال: /target @targetchannel")
        return
    
    target_channel = context.args[0]
    channels["target"] = [target_channel]
    save_channels(channels)
    await update.message.reply_text(f"✅ کانال مقصد {target_channel} تنظیم شد")

async def list_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channels = load_channels()
    
    source_list = "\n".join(channels["source"]) if channels["source"] else "خالی"
    target = channels["target"][0] if channels["target"] else "تنظیم نشده"
    
    text = f"📋 **کانال‌های منبع:**\n{source_list}\n\n🎯 **کانال مقصد:**\n{target}"
    await update.message.reply_text(text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.message
        channels = load_channels()
        
        if not channels["target"]:
            return
        
        target_channel = channels["target"][0]
        
        if message.document or message.photo or message.video:
            await bot.forward_message(
                chat_id=target_channel,
                from_chat_id=message.chat_id,
                message_id=message.message_id
            )
            logger.info(f"فایل منتشر شد ✅")
    
    except TelegramError as e:
        logger.error(f"خطا: {e}")
    except Exception as e:
        logger.error(f"خطا: {e}")

app.add_handler(CommandHandler("add", add_channel))
app.add_handler(CommandHandler("remove", remove_channel))
app.add_handler(CommandHandler("target", set_target))
app.add_handler(CommandHandler("list", list_channels))
app.add_handler(MessageHandler(
    filters.Document | filters.PHOTO | filters.VIDEO,
    handle_message
))

if __name__ == "__main__":
    logger.info("ربات شروع شد ✅")
    app.run_polling()
