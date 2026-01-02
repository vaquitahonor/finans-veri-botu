import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.common.by import By

def calistir(ticker):
    # --- AYARLAR ---
    current_folder = os.path.dirname(os.path.abspath(__file__))
    folder_name = f"{ticker.upper()} Earnings Calls"
    save_dir = os.path.join(current_folder, folder_name)
    
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    print(f"\n🚀 [ADIM 1/2] Veri çekme başlatılıyor: {ticker.upper()}")
    
    # --- CHROME AYARLARI (GÜÇLENDİRİLMİŞ) ---
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--ignore-certificate-errors')
    
    # Sunucuda (Linux) Chromium yolunu bulmaya çalış
    # Streamlit Cloud genelde bu yola kurar
    if os.path.exists("/usr/bin/chromium"):
        chrome_options.binary_location = "/usr/bin/chromium"
    elif os.path.exists("/usr/bin/chromium-browser"):
         chrome_options.binary_location = "/usr/bin/chromium-browser"

    driver = None
    try:
        # Chrome Driver'ı otomatik kur ve başlat
        service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"KRİTİK HATA: Driver başlatılamadı! Sebebi: {e}")
        # İkinci deneme: Standart Chrome ile
        try:
            print("Standart Chrome deneniyor...")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e2:
             print(f"İkinci deneme de başarısız: {e2}")
             return

    if not driver:
        return

    try:
        base_url = "https://earningscall.biz"
        url = f"{base_url}/e/nasdaq/s/{ticker.lower()}"
        
        print(f"Siteye gidiliyor: {url}")
        driver.get(url)
        time.sleep(3) # Sayfanın yüklenmesi için biraz daha bekle

        # 404 Kontrolü
        if "404" in driver.title or "Not Found" in driver.page_source:
            url = f"{base_url}/e/nyse/s/{ticker.lower()}"
            driver.get(url)
            time.sleep(3)

        links = []
        try:
            elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/y/') and contains(@href, '/q/')]")
            for elem in elements:
                href = elem.get_attribute('href')
                if href and href not in links:
                    links.append(href)
        except:
            pass

        print(f"✅ {len(links)} adet rapor bulundu.")

        if len(links) == 0:
            print("HATA: Hiç link bulunamadı! Site engellemiş veya sayfa boş olabilir.")
        
        for link in links:
            try:
                if not link.startswith("http"): link = base_url + link
                
                parts = link.strip('/').split('/')
                try:
                    year = parts[parts.index('y') + 1]
                    quarter = parts[-1]
                    filename = f"{year}_{quarter}.txt"
                except:
                    filename = f"report_{int(time.time())}.txt"

                file_path = os.path.join(save_dir, filename)
                
                driver.get(link)
                time.sleep(1)
                page_text = driver.find_element(By.TAG_NAME, "body").text
                
                if len(page_text) < 1000:
                    continue
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"URL: {link}\nDATE: {time.strftime('%Y-%m-%d')}\n{'-'*50}\n\n{page_text}")
                
            except:
                continue

    except Exception as e:
        print(f"İşlem Hatası: {e}")
    finally:
        if driver:
            driver.quit()
        print("✅ Veri çekme işlemi sonlandı.\n")
