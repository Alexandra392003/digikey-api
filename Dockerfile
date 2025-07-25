FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg ca-certificates fonts-liberation \
    libappindicator3-1 libasound2 libatk-bridge2.0-0 libatk1.0-0 \
    libcups2 libdbus-1-3 libdrm2 libx11-xcb1 libxcomposite1 libxdamage1 \
    libxrandr2 libgbm1 libgtk-3-0 libnss3 libxss1 libxshmfence1 libxext6 \
    libxfixes3 libxi6 libxtst6 \
    chromium chromium-driver

ENV CHROME_BIN="/usr/bin/google-chrome"
ENV PATH="$PATH:/usr/bin"

COPY . /app
WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "app.py"]
