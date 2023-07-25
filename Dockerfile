 # Use the official Python base image
FROM python:3.9-slim

# Install required system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    nodejs \
    npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up Viurr
RUN npm install -g viurr

# Copy the Python bot script and requirements.txt to the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the Python bot
CMD ["python", "main.py"]



#FROM python:3.9

#RUN dpkg --add-architecture i386 && apt-get update && apt-get install -y ffmpeg && apt-get install -y curl && apt-get install -y wine 

#COPY . .

#RUN pip install --no-cache-dir -r requirements.txt

#RUN mkdir downloads

#CMD ["python", "main.py"]
