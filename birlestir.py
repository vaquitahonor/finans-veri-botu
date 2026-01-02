import os

def calistir(ticker, yil_sayisi="4"):
    ticker = ticker.upper()
    print(f"🧩 [ADIM 2/2] Dosyalar birleştiriliyor: {ticker}")

    current_folder = os.path.dirname(os.path.abspath(__file__))
    hedef_klasor = os.path.join(current_folder, f"{ticker} Earnings Calls")
    cikis_dosyasi = os.path.join(current_folder, f"{ticker}_FULL_RAPOR.txt")

    if not os.path.exists(hedef_klasor):
        print("❌ Klasör bulunamadı! Önce veri çekilmeli.")
        return

    dosyalar = [f for f in os.listdir(hedef_klasor) if f.endswith('.txt')]
    dosyalar.sort(reverse=True)

    if not dosyalar:
        print("⚠️ Klasör boş.")
        return

    with open(cikis_dosyasi, "w", encoding="utf-8") as ana_dosya:
        sayac = 0
        for dosya_adi in dosyalar:
            path = os.path.join(hedef_klasor, dosya_adi)
            with open(path, "r", encoding="utf-8") as kaynak:
                ana_dosya.write(f"\n{'='*40}\nRAPOR: {dosya_adi}\n{'='*40}\n")
                ana_dosya.write(kaynak.read())
                ana_dosya.write(f"\n\n{'-'*20} SONRAKİ {'-'*20}\n\n")
            sayac += 1
            print(f"  + Eklendi: {dosya_adi}")

    print(f"🎉 BİTTİ! Toplam {sayac} rapor birleştirildi.")
    print(f"📄 Dosyan burada: {cikis_dosyasi}")