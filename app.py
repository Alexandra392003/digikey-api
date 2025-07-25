from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

app = Flask(__name__)

def get_price_from_digikey(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.binary_location = "/usr/bin/google-chrome-stable"  # IMPORTANT pe Render

    driver = webdriver.Chrome(
        ChromeDriverManager().install(),
        options=options
    )

    try:
        driver.get(url)

        # DEBUG: loghează codul HTML primit
        print("=== HTML PRIMIT ===")
        print(driver.page_source[:3000])  # log scurt

        # Așteaptă apariția prețului în pagină
        wait = WebDriverWait(driver, 10)
        price_element = wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            'td.MuiTableCell-root.MuiTableCell-body.MuiTableCell-alignRight.MuiTableCell-sizeMedium.tss-css-fz7dy5-tableCell.mui-css-115xzy4 span'
        )))
        price = price_element.text.strip()
        print("Preț extras:", price)

    except Exception as e:
        print("Eroare la extragere preț:", e)
        price = None
    finally:
        driver.quit()

    return price


@app.route('/get-price', methods=['GET'])
def get_price():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Lipsește parametrul 'url'"}), 400

    price = get_price_from_digikey(url)
    if price:
        return jsonify({"pret": price})
    else:
        return jsonify({"error": "500 - Pretul nu a putut fi extras"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
