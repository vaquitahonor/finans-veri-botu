import streamlit as st
import os
import time
import sys

# Diğer dosyaları içeri alıyoruz (Aynı klasörde olmaları şart)
try:
    import data_cekme
    import birlestir
except ImportError:
    st.error("HATA: 'data_cekme.py' ve 'birlestir.py' dosyaları bu dosya ile aynı klasörde olmalı!")
    st.stop()

# --- SAYFA YAPISI VE STİL ---
st.set_page_config(page_title="Finansal Veri Merkezi", layout="centered")

# CSS: Butonları güzelleştirme
st.markdown("""
<style>
    div.stButton > button {
        width: 100%;
        height: 80px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 10px;
        border: 2px solid #f0f0f0;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        border-color: #ff4b4b;
        color: #ff4b4b;
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# --- SAYFA YÖNETİMİ ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

def git_home(): st.session_state.page = 'home'
def git_earnings(): st.session_state.page = 'earnings'

# --- 1. SAYFA: ANA MENÜ ---
if st.session_state.page == 'home':
    st.title("Ana Kontrol Paneli")
    st.write("İşlem yapmak istediğiniz modülü seçin:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📞 Earnings Call\n(Transkript)", key="btn1"):
            git_earnings()
            st.rerun()
        st.button("📊 Bilanço\n(Yakında)", key="btn3")
        st.button("🐦 Twitter\n(Yakında)", key="btn5")
        
    with col2:
        st.button("📰 Haberler\n(Yakında)", key="btn2")
        st.button("📈 Teknik Analiz\n(Yakında)", key="btn4")
        st.button("⚙️ Ayarlar\n(Yakında)", key="btn6")

# --- 2. SAYFA: EARNINGS CALL (İŞLEM EKRANI) ---
elif st.session_state.page == 'earnings':
    # Üst bar
    col_back, col_title = st.columns([1, 4])
    with col_back:
        if st.button("⬅ Geri"):
            git_home()
            st.rerun()
    with col_title:
        st.subheader("Earnings Call İndirici")

    st.divider()

    # Ticker Girişi
    ticker = st.text_input("Hisse Kodu (Ticker)", placeholder="Örn: NVDA, THYAO").upper()
    
    if st.button("Verileri Getir ve Birleştir 🚀", type="primary"):
        if not ticker:
            st.warning("Lütfen bir hisse kodu yazın.")
        else:
            # --- İŞLEM BAŞLIYOR ---
            status = st.status("İşlemler yapılıyor...", expanded=True)
            
            try:
                # 1. ADIM: VERİ ÇEKME
                status.write(f"📥 {ticker} verileri indiriliyor (Chrome açılacak)...")
                # data_cekme.py içindeki fonksiyonu çağırıyoruz
                data_cekme.calistir(ticker)
                status.write("✅ İndirme tamamlandı.")
                
                # 2. ADIM: BİRLEŞTİRME
                status.write("🔄 Dosyalar birleştiriliyor...")
                # birlestir.py içindeki fonksiyonu çağırıyoruz
                birlestir.calistir(ticker)
                
                # Dosya adını oluştur (birlestir.py bu ismi veriyor)
                hedef_dosya_adi = f"{ticker}_FULL_RAPOR.txt"
                current_folder = os.path.dirname(os.path.abspath(__file__))
                dosya_yolu = os.path.join(current_folder, hedef_dosya_adi)

                if os.path.exists(dosya_yolu):
                    status.write("✅ Birleştirme tamamlandı!")
                    status.update(label="İşlem Başarıyla Bitti", state="complete", expanded=False)
                    
                    # 3. ADIM: İNDİRME BUTONU
                    with open(dosya_yolu, "r", encoding="utf-8") as f:
                        dosya_icerigi = f.read()

                    st.success(f"🎉 {ticker} raporu hazır!")
                    st.download_button(
                        label=f"📄 {hedef_dosya_adi} İNDİR",
                        data=dosya_icerigi,
                        file_name=hedef_dosya_adi,
                        mime="text/plain",
                        use_container_width=True
                    )
                else:
                    status.update(label="Hata", state="error")
                    st.error("Dosya oluşturulamadı. Lütfen hisse kodunu kontrol edin.")

            except Exception as e:
                status.update(label="Hata", state="error")
                st.error(f"Bir hata oluştu: {str(e)}")