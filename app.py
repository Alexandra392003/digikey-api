from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

app = Flask(__name__)

def get_price_from_digikey(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/google-chrome-stable"  # important pe Render

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except Exception as e:
        return None  # eroare la pornirea driverului

    try:
        driver.get(url)
        time.sleep(5)

        price_element = driver.find_element(
            By.CSS_SELECTOR,
            'td.MuiTableCell-root.MuiTableCell-body.MuiTableCell-alignRight.MuiTableCell-sizeMedium.tss-css-fz7dy5-tableCell.mui-css-115xzy4 span'
        )
        price = price_element.text
    except Exception as e:
        price = None  # Nu întoarcem mesaj de eroare aici
    finally:
        driver.quit()

    return price

@app.route("/")
def home():
    return "API DigiKey este activ!"

@app.route("/digikey", methods=["GET"])
def digikey():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Lipseste parametrul ?url"}), 400

    price = get_price_from_digikey(url)
    if price:
        return jsonify({"price": price})
    else:
        return jsonify({"error": "Pretul nu a putut fi extras"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
