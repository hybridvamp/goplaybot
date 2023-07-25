FROM python:3.9

RUN dpkg --add-architecture i386 && apt-get update && apt-get install -y ffmpeg && apt-get install -y curl && apt-get install -y wine 

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir downloads

CMD ["python", "main.py"]
