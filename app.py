from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os

app = Flask(__name__)

def create_driver():
    """Creează un driver Chrome optimizat pentru Render"""
    chrome_options = Options()
    
    # Configurații pentru Render/Docker
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    return webdriver.Chrome(options=chrome_options)

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint - ACESTA REZOLVĂ EROAREA 404"""
    return jsonify({"status": "API is running", "service": "digikey-scraper"})

@app.route("/digikey", methods=["GET"])
def get_digikey_price():
    """Endpoint pentru n8n workflow - folosește query parameter"""
    url = request.args.get('url')
    
    if not url:
        return jsonify({"error": "URL parameter lipsă"}), 400
    
    return scrape_price(url)

@app.route("/get-price", methods=["POST"])
def get_price():
    """Endpoint original POST"""
    data = request.get_json()
    url = data.get("url")
    
    if not url:
        return jsonify({"error": "URL lipsă"}), 400
    
    return scrape_price(url)

def scrape_price(url):
    """Funcția principală de extragere preț"""
    driver = None
    
    try:
        driver = create_driver()
        
        # Setează timeout-uri mai scurte
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        # Accesează pagina
        driver.get(url)
        
        # Așteaptă ca pagina să se încarce
        time.sleep(5)
        
        # Încearcă mai mulți selectori posibili pentru preț
        price_selectors = [
            "td.MuiTableCell-alignRight > span",
            "td.MuiTableCell-alignRight span",
            "[data-testid='price-break-price']",
            ".price-break-price",
            ".currency-price",
            ".price",
            "span[class*='price']",
            "td[class*='price'] span"
        ]
        
        price_text = None
        
        for selector in price_selectors:
            try:
                price_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                price_text = price_element.text.strip()
                if price_text and price_text != "":
                    break
            except TimeoutException:
                continue
        
        if not price_text:
            # Dacă nu găsește prețul, încearcă să găsească orice text care arată ca un preț
            all_text = driver.find_elements(By.XPATH, "//*[contains(text(), '€') or contains(text(), '$') or contains(text(), '£')]")
            for element in all_text:
                text = element.text.strip()
                if any(char.isdigit() for char in text):
                    price_text = text
                    break
        
        driver.quit()
        
        if price_text:
            return jsonify({
                "pret": price_text,
                "sursa": url,
                "status": "success"
            })
        else:
            return jsonify({
                "error": "Prețul nu a fost găsit pe pagină",
                "sursa": url,
                "status": "not_found"
            }), 404
            
    except TimeoutException:
        if driver:
            debug_html = driver.page_source[:1000] if driver.page_source else "HTML indisponibil"
            driver.quit()
        return jsonify({
            "error": "Timeout - Pagina nu s-a încărcat la timp",
            "html_sample": debug_html,
            "status": "timeout"
        }), 408
        
    except Exception as err:
        if driver:
            try:
                debug_html = driver.page_source[:1000]
            except:
                debug_html = "Nu s-a putut extrage HTML-ul"
            driver.quit()
            
        return jsonify({
            "error": "Eroare în procesarea cererii",
            "details": str(err),
            "html_sample": debug_html,
            "status": "error"
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
