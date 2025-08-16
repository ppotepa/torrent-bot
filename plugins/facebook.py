import os
import yt_dlp

BASE_DIR = "downloads"

def run(bot, message, folder, url, mode="video"):
    try:
        target_dir = os.path.join(BASE_DIR, folder) if folder else BASE_DIR
        os.makedirs(target_dir, exist_ok=True)

        bot.reply_to(
            message,
            f"📘 Facebook detected!\n📂 Folder: {folder or 'root'}\n🔗 {url}\n🎛 Mode: {mode}"
        )

        if mode == "audio":
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{target_dir}/%(title)s.%(ext)s',
                'noplaylist': True,
                'quiet': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '0',  # keep best
                }],
            }
        else:  # video
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': f'{target_dir}/%(title)s.%(ext)s',
                'noplaylist': True,
                'quiet': True,
                'merge_output_format': 'mp4',
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # adjust filename if audio mode converted
        if mode == "audio" and not filename.endswith(".mp3"):
            filename = os.path.splitext(filename)[0] + ".mp3"

        if os.path.exists(filename):
            with open(filename, "rb") as f:
                if mode == "audio":
                    bot.send_audio(message.chat.id, f, caption=f"✅ Saved to {folder or 'root'} (audio)")
                else:
                    bot.send_video(message.chat.id, f, caption=f"✅ Saved to {folder or 'root'} (video)")
        else:
            bot.reply_to(message, "❌ Download failed: file not found.")

    except Exception as e:
        bot.reply_to(message, f"❌ Facebook error: {e}")
