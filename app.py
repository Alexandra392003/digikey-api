from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

@app.route('/get-price', methods=['GET'])
def get_price():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(5)

    try:
        price_element = driver.find_element(By.CSS_SELECTOR, 'td.MuiTableCell-root span')
        price = price_element.text
    except Exception as e:
        price = "Eroare la extragere: " + str(e)

    driver.quit()
    return jsonify({"price": price})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
