FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg ca-certificates \
    fonts-liberation libappindicator3-1 libasound2 \
    libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 \
    libgdk-pixbuf2.0-0 libnspr4 libnss3 libx11-xcb1 \
    libxcomposite1 libxdamage1 libxrandr2 xdg-utils \
    libu2f-udev libvulkan1 libxcb-dri3-0 libxshmfence1 \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Chrome 137
RUN wget -q https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_137.0.7151.55-1_amd64.deb && \
    apt install -y ./google-chrome-stable_137.0.7151.55-1_amd64.deb && rm ./google-chrome-stable_137.0.7151.55-1_amd64.deb

# Install ChromeDriver 137 (exact match)
RUN wget -q https://storage.googleapis.com/chrome-for-testing-public/137.0.7151.55/linux64/chromedriver-linux64.zip && \
    unzip chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf chromedriver-linux64.zip chromedriver-linux64

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Add app files
COPY ./app ./app

# Runtime settings
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

EXPOSE 80

CMD ["python", "app/main.py"]


# Start your script
CMD ["python", "app/main.py"]
