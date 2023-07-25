FROM python:3.9

RUN apt-get update && apt-get install -y ffmpeg && apt-get install -y curl

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir downloads

RUN chmod +x /app/Bin/curl /app/Bin/m3u8dl

CMD ["python", "main.py"]
