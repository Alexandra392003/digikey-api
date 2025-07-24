from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

app = Flask(__name__)

def get_price_from_digikey(url):
    options = Options()
    options.add_argument("--headless")  # browser fără fereastră
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(url)
    time.sleep(5)  # așteaptă să se încarce pagina

    try:
        price_element = driver.find_element(By.CSS_SELECTOR, 'td.MuiTableCell-root.MuiTableCell-body.MuiTableCell-alignRight.MuiTableCell-sizeMedium.tss-css-fz7dy5-tableCell.mui-css-115xzy4 span')
        price = price_element.text
    except Exception as e:
        price = "Nu am găsit prețul: " + str(e)

    driver.quit()
    return price

@app.route("/")
def home():
    return "API DigiKey este activ! Folosește ruta /digikey?url=URL_PRODUS"

@app.route("/digikey")
def digikey():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Parametrul 'url' este obligatoriu"}), 400

    pret = get_price_from_digikey(url)
    return jsonify({"price": pret})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
