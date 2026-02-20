import streamlit as st
import requests
from datetime import datetime, timedelta
import re
import urllib.parse

# ==========================================
# 1. إعدادات الواجهة (The Titan Theme)
# ==========================================
st.set_page_config(page_title="AMIN STREAM V1100", layout="wide", page_icon="⚡")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; }
    .stApp { background-color: #050505; color: #e0e0e0; }
    
    /* تصميم الكارت الاحترافي */
    .movie-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 30px;
        border: 1px solid #1f1f1f;
        border-right: 5px solid #00ff88; /* خط نيون جانبي */
        transition: 0.3s;
    }
    .movie-card:hover { border-color: #00ff88; box-shadow: 0 0 20px rgba(0,255,136,0.2); }
    
    .movie-title { color: #00ff88; font-size: 28px; font-weight: bold; margin-bottom: 10px; }
    .movie-info { color: #888; font-size: 14px; margin-bottom: 20px; }
    
    /* تحسين الأزرار */
    .stButton>button {
        background: linear-gradient(90deg, #00ff88, #00bd6e) !important;
        color: black !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. محركات البحث والجلب (The Engine)
# ==========================================

def get_content_data(identifier):
    """جلب الفيديو والبوستر من سيرفر الأرشيف"""
    try:
        r = requests.get(f"https://archive.org/metadata/{identifier}", timeout=5).json()
        server = r.get('server')
        dir_path = r.get('dir')
        files = r.get('files', [])
        
        video, poster = None, "https://via.placeholder.com/300x450/111/00ff88?text=NO+POSTER"
        
        for f in files:
            name = f['name']
            if not video and name.lower().endswith(('.mp4', '.mkv')):
                video = f"https://{server}{dir_path}/{name}"
            if name.lower().endswith(('.jpg', '.png', '.jpeg')) and 'thumb' not in name:
                poster = f"https://{server}{dir_path}/{name}"
        return video, poster
    except: return None, None

def generate_qr(link):
    """توليد كود QR للبث المباشر (DLNA)"""
    return f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={urllib.parse.quote(link)}"

# ==========================================
# 3. بناء الصفحة (Main Scene)
# ==========================================

st.markdown("<h1 style='text-align: center; color: #00ff88;'>⚡ AMIN STREAM TITAN V1100</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h2 style='color: #00ff88;'>🔍 الرادار</h2>", unsafe_allow_html=True)
    query = st.text_input("اسم المسلسل أو المحتوى", placeholder="مثلاً: المداح، عرس الجن...")
    search_btn = st.button("🚀 اضرب نار (بحث)")
    st.divider()
    st.markdown("### 📱 خاصية DLNA")
    st.info("اضغط على زر 'بث للشاشة' داخل أي مسلسل لمسح الكود وتشغيله على التلفزيون.")

if search_btn:
    with st.spinner('📡 جاري سحب البيانات من السيرفرات...'):
        # البحث في أرشيف
        q = f'title:("{query if query else "2026"}") AND mediatype:(video)'
        params = {'q': q, 'fl[]': ['identifier', 'title', 'addeddate'], 'sort[]': 'addeddate desc', 'rows': '15', 'output': 'json'}
        
        try:
            results = requests.get("https://archive.org/advancedsearch.php", params=params).json().get('response', {}).get('docs', [])
            
            if not results:
                st.error("❌ ملقيناش حاجة بالاسم ده حالياً.. جرب كلمة تانية.")
            else:
                for item in results:
                    video_url, poster_url = get_content_data(item['identifier'])
                    
                    if video_url:
                        with st.container():
                            # تنظيم المحتوى (بوستر على اليمين وكلام على اليسار)
                            col_img, col_txt = st.columns([1, 3])
                            
                            with col_img:
                                st.image(poster_url, use_column_width=True)
                            
                            with col_txt:
                                # تنظيف العنوان
                                clean_t = re.sub(r'Arabseed|عرب سيد|مشاهدة|تحميل|2026', '', item['title'], flags=re.IGNORECASE).strip()
                                
                                st.markdown(f"""
                                    <div class="movie-card">
                                        <div class="movie-title">🎬 {clean_t}</div>
                                        <div class="movie-info">📅 تاريخ الإضافة: {item.get('addeddate', '')[:10]} | ⚡ جودة عالية</div>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                # مشغل الفيديو
                                st.video(video_url)
                                
                                # أدوات المشاركة والبث
                                with st.expander("🔗 خيارات البث الذكي والمشاركة"):
                                    c1, c2, c3 = st.columns(3)
                                    with c1:
                                        st.markdown("**📺 بث للشاشة (QR)**")
                                        st.image(generate_qr(video_url), width=120)
                                    with c2:
                                        st.markdown("**📤 مشاركة فورية**")
                                        wa_url = f"https://wa.me/?text={urllib.parse.quote('اتفرج معايا على ' + clean_t + ': ' + video_url)}"
                                        st.link_button("🟢 WhatsApp", wa_url)
                                        tg_url = f"https://t.me/share/url?url={video_url}&text={clean_t}"
                                        st.link_button("🔵 Telegram", tg_url)
                                    with c3:
                                        st.markdown("**📥 تحميل**")
                                        st.link_button("تحميل مباشر", video_url)
                                        st.code(video_url, language="text")
                            st.divider()
        except:
            st.error("⚠️ السيرفر مضغوط.. حاول كمان ثواني.")

# حالة الصفحة عند البداية
else:
    st.markdown("<br><br><p style='text-align: center; color: #444; font-size: 20px;'>في انتظار أوامرك يا محمد.. ابدأ البحث الآن</p>", unsafe_allow_html=True)
