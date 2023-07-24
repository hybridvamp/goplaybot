# (C) HYBRID - https://github.com/hybridvamp

import os
import requests
import logging

from pyromod import listen
from pyrogram import Client, filters

API_ID = int(os.environ.get('API_ID'))
API_HASH = os.environ.get('API_HASH')
BOT_TOKEN = os.environ.get('BOT_TOKEN')

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = Client(
    "goplaybot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start"))
async def start_command(_, message):
    await message.reply_text("Welcome! use /upload command to start the process")

@app.on_message(filters.command("upload"))
async def download_file(_, message):
    chat_id = str(message.from_user.id)
    user_id = message.from_user.id

    dcode_msg = await app.ask(chat_id, "Enter the download code:", filters=filters.text)
    if await cancelled(dcode_msg):
        return
    dcode = dcode_msg.text

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

    # Simulate file download using requests library
    download_url = f"https://goplay.pw/?dcode={dcode}&quality={resolution}&downloadmp4vid=2"
    response = requests.get(download_url)
    downloaded_file_path = f"downloads/{filename}.ts"
    with open(downloaded_file_path, "wb") as f:
        f.write(response.content)

    await message.reply_text("Processing the file... Please wait...")

    # Simulate file processing using ffmpeg-python
    processed_file_path = f"downloads/{filename}.mkv"
    try:
        cmd = (
            f'ffmpeg -i "{downloaded_file_path}" -c copy "{processed_file_path}"'
        )
        os.system(cmd)
    except Exception as e:
        log.error(f"Error during ffmpeg processing: {e}")

    # Sending the processed file back to the user
    if os.path.exists(processed_file_path):
        await app.send_document(
            user_id,
            document=processed_file_path,
            caption="Here is your processed file!",
        )
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

    app.run()
