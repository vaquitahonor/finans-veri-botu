import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def calistir(ticker):
    # --- AYARLAR ---
    current_folder = os.path.dirname(os.path.abspath(__file__))
    folder_name = f"{ticker.upper()} Earnings Calls"
    save_dir = os.path.join(current_folder, folder_name)
    
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    print(f"\n🚀 [ADIM 1/2] Veri çekme başlatılıyor: {ticker.upper()}")
    
    # --- CHROME AYARLARI (SUNUCU İÇİN KRİTİK) ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ekransız mod (Görünmez tarayıcı)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Sunucuda SSL hatası almamak için
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Driver başlatma hatası: {e}")
        return

    try:
        base_url = "https://earningscall.biz"
        url = f"{base_url}/e/nasdaq/s/{ticker.lower()}"
        
        try:
            driver.get(url)
            time.sleep(2)
        except:
            driver.get(url)

        if "404" in driver.title or "Not Found" in driver.page_source:
            url = f"{base_url}/e/nyse/s/{ticker.lower()}"
            driver.get(url)
            time.sleep(2)

        links = []
        try:
            elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/y/') and contains(@href, '/q/')]")
            for elem in elements:
                href = elem.get_attribute('href')
                if href and href not in links:
                    links.append(href)
        except:
            pass

        print(f"✅ {len(links)} adet rapor bulundu. İndiriliyor...")

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
                
                if os.path.exists(file_path):
                    continue

                driver.get(link)
                # Sayfanın yüklenmesi için bekle
                time.sleep(1)
                page_text = driver.find_element(By.TAG_NAME, "body").text
                
                if len(page_text) < 1000 or "scheduled to happen" in page_text.lower():
                    continue
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"URL: {link}\nDATE: {time.strftime('%Y-%m-%d')}\n{'-'*50}\n\n{page_text}")
                
                print(f"  💾 İndirildi: {filename}")
                time.sleep(0.5)

            except:
                continue

    except Exception as e:
        print(f"Hata: {e}")
    finally:
        driver.quit()
        print("✅ Veri çekme tamamlandı.\n")