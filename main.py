# (C) HYBRID - https://github.com/hybridvamp
import os
import requests
import logging
import subprocess
import asyncio
import youtube_dl

from pyrogram import Client, filters
from pyrogram.types import Message


API_ID = int(os.environ.get('API_ID'))
API_HASH = os.environ.get('API_HASH')
BOT_TOKEN = os.environ.get('BOT_TOKEN')

logging.basicConfig(level=logging.ERROR)
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR) 

app = Client(
    "goplaybot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


async def download_viu_video(link: str, quality: str, file_name: str) -> str:
    ydl_opts = {
        'format': f'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4][height<={quality}]/best',  # Download the specified quality mp4 video
        'outtmpl': '%(title)s.%(ext)s',  # Output file template (filename)
        'merge_output_format': 'mkv',  # Merge audio and video into mkv format
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',  # Convert the merged mkv to mp4
        }],
        'quiet': True,
    }

    loop = asyncio.get_event_loop()
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = await loop.run_in_executor(None, lambda: ydl.extract_info(link, download=True))
        downloaded_file = ydl.prepare_filename(info_dict)

    renamed_file = f"{file_name}.mp4"
    os.rename(downloaded_file, renamed_file)

    return renamed_file


@app.on_message(filters.command("start"))
async def start_command(_, message: Message):
    await message.reply_text("Hello! Send me a Viu video link, quality (e.g., 480p), and the desired file name "
                              "separated by spaces, and I'll download, rename, and send it back to you!\n\n"
                              "Example: `<link> 480p my_video`")


@app.on_message(filters.text & filters.regex(r"https:\/\/www\.viu\.com\/.*\s+\d+p\s+\S+"))
async def viu_video_link_handler(_, message: Message):
    parts = message.text.strip().split()
    video_link, quality, file_name = parts[0], parts[1], "_".join(parts[2:])

    try:
        video_file = await download_viu_video(video_link, quality, file_name)
        _, video_title = os.path.split(video_file)

        await message.reply_video(video_file, caption=f"Here's the video: {video_title}")

        os.remove(video_file)
    except Exception as e:
        await message.reply_text(f"Sorry, I couldn't download and send the video.\nError: {e}")
        print(e)


# Start the bot
if __name__ == "__main__":
    app.run()






"""
import os
import requests
import logging
import subprocess

from tqdm import tqdm
from pyromod import listen
from pyrogram import Client, filters
import shutil
import ffmpeg

API_ID = int(os.environ.get('API_ID'))
API_HASH = os.environ.get('API_HASH')
BOT_TOKEN = os.environ.get('BOT_TOKEN')

logging.basicConfig(level=logging.ERROR)
log = logging.getLogger(__name__)
log.setLevel(logging.ERROR) 

app = Client(
    "goplaybot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

used_download_codes = set()

@app.on_message(filters.command("start"))
async def start_command(_, message):
    await message.reply_text("Welcome! use /upload command to start the process")


@app.on_message(filters.command("download"))
async def download_file(_, message):
    chat_id = message.chat.id

    # Ask for the download code
    dcode_msg = await app.ask(chat_id, "Enter the download code:", filters=filters.text)
    dcode = dcode_msg.text.strip()

    # Ask for the resolution
    resolution_msg = await app.ask(chat_id, "Enter Resolution (Example: 1080p, 720p, 480p, 360p):", filters=filters.text)
    resolution = resolution_msg.text.strip()

    # Ask for the file format
    format_msg = await app.ask(chat_id, "Enter File Format (mp4, mkv):", filters=filters.text)
    format_str = format_msg.text.strip().lower()

    # Ask for the filename
    filename_msg = await app.ask(chat_id, "Enter Filename:", filters=filters.text)
    filename = filename_msg.text.strip()

    # Start downloading the video file using curl and m3u8dl
    curl_cmd = f'Bin/curl -k -sS "https://goplay.pw/?dcode={dcode}"'
    for line in subprocess.Popen(curl_cmd, shell=True, stdout=subprocess.PIPE).stdout:
        key = line.decode("utf-8").strip()

    if key:
        mode = 3
    else:
        mode = 2

    m3u8dl_cmd = f'Bin/m3u8dl "https://goplay.pw/?dcode={dcode}&quality={resolution}&downloadmp4vid={mode}" --enableDelAfterDone --saveName "{filename}"'
    subprocess.run(m3u8dl_cmd, shell=True)

    # Check if the downloaded file is valid before processing with ffmpeg
    downloaded_file_path = f'Downloads/{filename}.ts' if format_str == "mp4" else f'Downloads/{filename}.mkv'
    try:
        ffmpeg_cmd = ['ffmpeg', '-i', downloaded_file_path, '-t', '10', '-f', 'null', '-']
        subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        await message.reply("Invalid file format. Please try again with a valid video file.")
        os.remove(downloaded_file_path)
        return

    # Process the video file with ffmpeg and mp4decrypt if needed
    if format_str == "mkv":
        srt_file_path = f'Downloads/{filename}.srt'
        if key:
            audio_file_path = f'Downloads/{filename}(Audio)_.aac'
            subprocess.run(['mp4decrypt', '--key', key, f'Downloads/{filename}.ts', audio_file_path])
        else:
            audio_file_path = f'Downloads/{filename}(Audio).aac'

        subprocess.run(['ffmpeg', '-i', downloaded_file_path, '-i', audio_file_path, '-i', srt_file_path, '-metadata', 'title=' + filename, '-c', 'copy', '-disposition:s:0', 'default', f'Downloads/{filename}.mkv'])

        # Clean up temporary files
        os.remove(downloaded_file_path)
        os.remove(audio_file_path)
        os.remove(srt_file_path)

    else:  # Format is mp4
        if key:
            audio_file_path = f'Downloads/{filename}(Audio)_.aac'
            subprocess.run(['mp4decrypt', '--key', key, f'Downloads/{filename}.ts', audio_file_path])
        else:
            audio_file_path = f'Downloads/{filename}(Audio).aac'

        subprocess.run(['ffmpeg', '-i', downloaded_file_path, '-i', audio_file_path, '-metadata', 'title=' + filename, '-c', 'copy', f'Downloads/{filename}.mp4'])

        # Clean up temporary files
        os.remove(downloaded_file_path)
        os.remove(audio_file_path)

    await message.reply("Download and processing completed successfully.")


@app.on_message(filters.command("cancel"))
async def cancel_download(_, message):
    # Implement cancellation logic if needed
    await message.reply("Download cancelled successfully.")



@app.on_message(filters.command("upload"))
async def download_file(_, message):
    chat_id = str(message.from_user.id)
    user_id = message.from_user.id

    dcode_msg = await app.ask(chat_id, "Enter the download code:", filters=filters.text)
    if await cancelled(dcode_msg):
        return
    dcode = dcode_msg.text

    if dcode in used_download_codes:
        await message.reply_text("This download code has already been used. Please try another code.")
        return
    else:
        used_download_codes.add(dcode)

    resolution_msg = await app.ask(chat_id, "Enter the resolution (e.g., 1080p, 720p, 480p, 360p):", filters=filters.text)
    if await cancelled(resolution_msg):
        return
    resolution = resolution_msg.text

    format_msg = await app.ask(chat_id, "Enter the file format (e.g., mp4, mkv (if you need softcoded subtitles)):", filters=filters.text)
    if await cancelled(format_msg):
        return
    file_format = format_msg.text

    filename_msg = await app.ask(chat_id, "Enter the filename:", filters=filters.text)
    if await cancelled(filename_msg):
        return
    filename = filename_msg.text

    await message.reply_text("Downloading the file... Please wait...")

    # Simulate file download using requests library with progress bar
    download_url = f"https://goplay.pw/?dcode={dcode}&quality={resolution}&downloadmp4vid=2"
    response = requests.get(download_url, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024  # 1 Kibibyte

    downloaded_file_path = f"downloads/{filename}.ts"
    progress_bar = tqdm(total=total_size, unit="iB", unit_scale=True, desc="Downloading")
    with open(downloaded_file_path, "wb") as f:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            f.write(data)
    progress_bar.close()

    # Check if download completed successfully
    if os.path.getsize(downloaded_file_path) < total_size:
        await message.reply_text("Download failed. Please try again.")
        os.remove(downloaded_file_path)
        return

    await message.reply_text("Processing the file... Please wait...")

    # Check if the downloaded file is valid before processing with ffmpeg
    try:
        with open(downloaded_file_path, "rb") as f:
            ffmpeg.probe(f, timeout=10)
    except ffmpeg.Error as e:
        log.error(f"Error while probing file with FFmpeg: {e}")
        await message.reply_text("Invalid file format. Please try again with a valid video file.")
        os.remove(downloaded_file_path)
        return

    # Simulate file processing using ffmpeg-python with progress bar
    processed_file_path = f"downloads/{filename}.mkv"
    try:
        cmd = (
            f'ffmpeg -i "{downloaded_file_path}" -c copy "{processed_file_path}"'
        )
        ffmpeg.run(cmd, capture_stderr=True, input=None, capture_stdout=True)
    except ffmpeg.Error as e:
        log.error(f"Error during ffmpeg processing: {e}")
        await message.reply_text("File processing failed!")
        os.remove(downloaded_file_path)
        return

    # Sending the processed file back to the user with progress bar
    if os.path.exists(processed_file_path):
        await message.reply_text("Uploading the processed file...")
        progress_bar = tqdm(total=os.path.getsize(processed_file_path), unit="iB", unit_scale=True, desc="Uploading")
        with open(processed_file_path, "rb") as f:
            await app.send_document(
                user_id,
                document=f,
                caption="Here is your processed file!",
                progress_callback=lambda current, total: progress_bar.update(current),
            )
        progress_bar.close()
    else:
        await message.reply_text("File processing failed!")

    # Delete downloaded files from the server directory
    os.remove(downloaded_file_path)
    if os.path.exists(processed_file_path):
        os.remove(processed_file_path)

    await message.reply_text("File processing completed successfully!")



async def cancelled(msg):
    if "/cancel" in msg.text:
        await msg.reply("Cancelled the Process!")
        return True
    elif "/restart" in msg.text:
        await msg.reply("Restarted the Bot!")
        return True
    elif msg.text.startswith("/"):
        await msg.reply("Cancelled the generation process!", quote=True)
        return True
    else:
        return False

if __name__ == "__main__":
    # Create a downloads directory if it doesn't exist
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    log.info("Bot started")
    app.run()
"""