FROM python:3.9

RUN dpkg --add-architecture i386 && apt-get update && apt-get install -y ffmpeg && apt-get install -y curl && apt-get install -y wine 

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir downloads

RUN wine /Bin/curl.exe --version
RUN wine /Bin/m3u8dl.exe --version

CMD ["python", "main.py"]
