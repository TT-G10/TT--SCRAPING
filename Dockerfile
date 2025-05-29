FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install basic dependencies
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg ca-certificates \
    fonts-liberation libasound2 libatk-bridge2.0-0 \
    libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 \
    libnspr4 libnss3 libx11-xcb1 libxcomposite1 \
    libxdamage1 libxrandr2 xdg-utils \
    libu2f-udev libvulkan1 libxcb-dri3-0 libxshmfence1 \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

# ✅ Install Chrome & ChromeDriver v137 from the official Chrome-for-Testing archive
RUN mkdir -p /opt/chrome && \
    wget -q https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/137.0.7151.55/linux64/chrome-linux64.zip && \
    unzip chrome-linux64.zip && \
    mv chrome-linux64 /opt/chrome/chrome && \
    ln -s /opt/chrome/chrome/chrome /usr/bin/google-chrome && \
    rm chrome-linux64.zip

RUN mkdir -p /opt/chromedriver && \
    wget -q https://storage.googleapis.com/chrome-for-testing-public/137.0.7151.55/linux64/chromedriver-linux64.zip && \
    unzip chromedriver-linux64.zip && \
    mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf chromedriver-linux64.zip chromedriver-linux64

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app
COPY ./app ./app

# Runtime environment
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# Expose port for Azure App Service
EXPOSE 80

# Run scraper
CMD ["python", "app/main.py"]

