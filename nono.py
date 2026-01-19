import os
import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from yt_dlp import YoutubeDL

# بياناتك
api_id = 37500857
api_hash = "0e347130926274ee5f85ff7f4b28968e"
bot_token = "8540206096:AAEwLLfJWLSn13EftKxnLx-iKmzKDcwmSgc"
CHANNEL_USERNAME = "moamen_muslim" # معرف القناة بدون @

app = Client("video_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# دالة التحقق من الاشتراك الإجباري
async def check_subscription(client, message):
    try:
        await client.get_chat_member(CHANNEL_USERNAME, message.from_user.id)
        return True
    except UserNotParticipant:
        await message.reply(
            f"⚠️ **عذراً، يجب عليك الاشتراك في القناة أولاً لاستخدام البوت!**\n\nقناة البوت: @{CHANNEL_USERNAME}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("اضغط هنا للاشتراك ✅", url=f"https://t.me/{CHANNEL_USERNAME}")]
            ])
        )
        return False
    except Exception:
        # في حال حدوث خطأ تقني، نسمح للمستخدم بالمرور مؤقتاً
        return True

# رسالة الترحيب /start
@app.on_message(filters.command("start"))
async def start_message(client, message):
    text = (
        f"مرحباً بك يا {message.from_user.mention} في بوت تحميل الفيديوهات 🎬\n\n"
        "أرسل لي أي رابط فيديو (يوتيوب، تيك توك، انستقرام) وسأقوم بتحميله لك بأعلى جودة.\n\n"
        "⇨𝑶𝒘𝒏𝒆𝒓 : @moamen_designer ⤶"
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("بـوت التـواصـل 💬", url="https://t.me/moamen10001bot")],
        [InlineKeyboardButton("البوت الإسلامي 🕌", url="https://t.me/moamen10002bot")]
    ])
    await message.reply(text, reply_markup=buttons)

# دالة شريط التقدم
async def progress_bar(current, total, message, start_time):
    try:
        if time.time() - start_time < 3:
            return
        percentage = current * 100 / total
        completed = int(percentage / 10)
        bar = "█" * completed + "░" * (10 - completed)
        await message.edit(
            f"⬆️ **جاري الرفع لتيليجرام...**\n"
            f"[{bar}] {percentage:.1f}%\n"
            f"🚀 {(current / (1024*1024)):.1f}MB / {(total / (1024*1024)):.1f}MB"
        )
    except:
        pass

def download_video(url, file_path):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': file_path,
        'quiet': True,
        'merge_output_format': 'mp4',
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# معالجة الروابط
@app.on_message(filters.regex(r'http'))
async def download_and_upload(client, message):
    # تحقق من الاشتراك الإجباري أولاً
    if not await check_subscription(client, message):
        return

    url = message.text
    status = await message.reply("🔍 جاري فحص الرابط...")
    
    file_name = f"video_{message.from_user.id}_{int(time.time())}.mp4"
    file_path = os.path.join(os.getcwd(), file_name)

    try:
        await status.edit("📥 جاري التحميل من المصدر...")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, download_video, url, file_path)

        await status.edit("✅ اكتمل التحميل، جاري الرفع لتيليجرام...")
        
        start_time = time.time()
        await client.send_video(
            chat_id=message.chat.id,
            video=file_path,
            caption=f"🎬 تم التحميل بنجاح!\n🔗 {url}\n\n⇨𝑶𝒘𝒏𝒆𝒓 : @moamen_designer ⤶",
            progress=progress_bar,
            progress_args=(status, start_time)
        )
    except Exception as e:
        await status.edit(f"❌ حدث خطأ: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        await status.delete()

print("✅ البوت يعمل مع الاشتراك الإجباري والأزرار...")
app.run()
