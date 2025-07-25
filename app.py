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
    options.binary_location = "/usr/bin/google-chrome"  # mai sigur decât google-chrome-stable
    options.add_argument("--headless=new")  # mai bun pentru Chrome modern
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except Exception as e:
        print("❌ Eroare la pornirea ChromeDriver:", e)
        return None

    try:
        driver.get(url)

        # Așteaptă elementele de preț
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "td.MuiTableCell-root span"))
        )

        # Găsește toate prețurile disponibile
        price_elements = driver.find_elements(By.CSS_SELECTOR, "td.MuiTableCell-root span")

        prices = [el.text for el in price_elements if el.text.strip().endswith("$") or "Lei" in el.text]

        if prices:
            return prices[0]  # returnează primul preț găsit
        else:
            print("⚠️ Nu s-au găsit prețuri în pagină.")
            return None

    except Exception as e:
        print("❌ Eroare la extragerea prețului:", e)
        return None
    finally:
        driver.quit()


@app.route("/")
def home():
    return "✅ Digi-Key Price Scraper este activ!"

@app.route("/digikey", methods=["GET"])
def digikey():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Lipsește parametrul ?url"}), 400

    price = get_price_from_digikey(url)
    if price:
        return jsonify({"price": price})
    else:
        return jsonify({"error": "Prețul nu a putut fi extras"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
