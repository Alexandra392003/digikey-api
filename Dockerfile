# Imagine de bază cu Python 3.11
FROM python:3.11-slim

# Instalăm dependențele sistemului necesare
RUN apt-get update && apt-get install -y \
    wget gnupg curl unzip ca-certificates \
    fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 libatk1.0-0 \
    libcups2 libdbus-1-3 libdrm2 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 \
    libgbm1 libgtk-3-0 libnss3 libxss1 lsb-release xdg-utils --no-install-recommends

# Adăugăm cheia și repository-ul oficial Chrome
RUN curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Instalăm Google Chrome
RUN apt-get update && apt-get install -y google-chrome-stable

# Setăm directorul de lucru
WORKDIR /app

# Copiem fișierele aplicației în container
COPY . .

# Instalăm pachetele Python
RUN pip install --no-cache-dir -r requirements.txt

# Expunem portul aplicației Flask
EXPOSE 8080

# Pornim aplicația Flask
CMD ["python", "app.py"]
