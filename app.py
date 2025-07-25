from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

app = Flask(__name__)

def get_price_from_digikey(url):
    options = Options()
    options.binary_location = "/usr/bin/google-chrome-stable"  # important pe Render
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except Exception as e:
        print("Eroare la pornirea driverului Chrome:", e)
        return None

    try:
        driver.get(url)

        # Așteaptă până apare elementul cu prețul, maxim 10 secunde
        price_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "td.MuiTableCell-alignRight > span"))
        )
        price = price_element.text

        # Pentru debug, poți salva sursa paginii (optional)
        # with open("page_source.html", "w", encoding="utf-8") as f:
        #     f.write(driver.page_source)

    except Exception as e:
        print("Eroare la extragerea pretului:", e)
        price = None
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
