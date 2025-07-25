from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

app = Flask(__name__)

@app.route("/get-price", methods=["POST"])
def get_price():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL lipsă"}), 400

    # Configurare Chrome headless pentru Render
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/google-chrome-stable"
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1920x1080")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        # Așteaptă ca prețul să apară
        price_element = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "td.MuiTableCell-alignRight > span"))
        )

        price_text = price_element.text.strip()

        driver.quit()
        return jsonify({
            "pret": price_text,
            "sursa": url
        })

    except TimeoutException:
        # Afișează primele 1000 caractere din HTML pentru depanare
        debug_html = driver.page_source[:1000]
        driver.quit()
        return jsonify({
            "error": "Timeout - Prețul nu a fost găsit",
            "html_sample": debug_html
        }), 500

    except Exception as err:
        try:
            debug_html = driver.page_source[:1000]
        except:
            debug_html = "Nu s-a putut extrage HTML-ul"

        driver.quit()
        return jsonify({
            "error": "Prețul nu a putut fi extras",
            "details": str(err),
            "html_sample": debug_html
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
