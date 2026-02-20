import streamlit as st
import requests
from datetime import datetime, timedelta
import re
import urllib.parse

# ==========================================
# 1. إعدادات الهوية والتصميم (Dark UI Pro)
# ==========================================
st.set_page_config(page_title="AMIN STREAM V1000", layout="wide", page_icon="⚡")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; }
    .stApp { background-color: #050505; color: #ffffff; }
    
    /* تصميم كارت المسلسل الاحترافي */
    .movie-card {
        background: #111111;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 25px;
        border: 1px solid #1f1f1f;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        border-right: 4px solid #00ff88; /* خط النيون الجانبي */
    }
    
    .movie-title { color: #00ff88; font-size: 26px; font-weight: 700; margin-bottom: 5px; }
    .movie-date { color: #666666; font-size: 13px; margin-bottom: 15px; }
    
    /* تحسين الأزرار */
    .stButton>button {
        background-color: #00ff88 !important;
        color: #000000 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
    }
    
    /* تعديل الهيدر */
    h1 { color: #ffffff; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. الدوال البرمجية (Logic)
# ==========================================

def clean_name(text):
    """تنظيف العنوان من الكلمات المزعجة ليكون احترافياً"""
    unwanted = ['Arabseed', 'عرب سيد', 'مشاهدة', 'تحميل', 'حلقة', 'كاملة', 'H d', '720p', '1080p', 'WEB-DL', '2026']
    for word in unwanted:
        text = re.sub(word, '', text, flags=re.IGNORECASE)
    return text.strip()

def get_metadata(identifier):
    """سحب الفيديو والبوستر من الأرشيف"""
    try:
        r = requests.get(f"https://archive.org/metadata/{identifier}", timeout=5).json()
        server, dir_path = r.get('server'), r.get('dir')
        files = r.get('files', [])
        
        video, poster = None, "https://via.placeholder.com/300x450/111/00ff88?text=NO+POSTER"
        
        for f in files:
            name = f['name']
            if not video and name.lower().endswith(('.mp4', '.mkv')):
                video = f"https://{server}{dir_path}/{name}"
            if name.lower().endswith(('.jpg', '.png', '.jpeg')):
                poster = f"https://{server}{dir_path}/{name}"
        return video, poster
    except: return None, None

def generate_qr(link):
    """توليد كود البث للشاشة"""
    return f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={urllib.parse.quote(link)}"

# ==========================================
# 3. الهيكل الرئيسي (Main Layout)
# ==========================================

st.markdown("<h1 style='text-align: center;'>⚡ AMIN STREAM TITAN</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>نظام البث السينمائي لرمضان 2026</p>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h2 style='color: #00ff88;'>🔍 الرادار</h2>", unsafe_allow_html=True)
    query = st.text_input("اسم المسلسل", placeholder="اكتب هنا...")
    search_btn = st.button("🚀 إطلاق البحث")
    st.divider()
    st.markdown("### 📱 البث الذكي")
    st.caption("استخدم الـ QR Code لإرسال الفيديو لشاشة التلفزيون فوراً.")

if search_btn:
    with st.spinner('📡 جاري مسح السيرفرات...'):
        q = f'title:("{query if query else "2026"}") AND mediatype:(video)'
        params = {'q': q, 'fl[]': ['identifier', 'title', 'addeddate'], 'sort[]': 'addeddate desc', 'rows': '15', 'output': 'json'}
        
        try:
            results = requests.get("https://archive.org/advancedsearch.php", params=params).json().get('response', {}).get('docs', [])
            
            if not results:
                st.error("❌ لم يتم العثور على محتوى بهذا الاسم.")
            else:
                for item in results:
                    video_url, poster_url = get_metadata(item['identifier'])
                    
                    if video_url:
                        # عرض المحتوى بنظام الكروت
                        with st.container():
                            col_img, col_txt = st.columns([1, 3])
                            
                            with col_img:
                                st.image(poster_url, use_column_width=True)
                            
                            with col_txt:
                                clean_t = clean_name(item['title'])
                                st.markdown(f"""
                                    <div class="movie-card">
                                        <div class="movie-title">🎬 {clean_t}</div>
                                        <div class="movie-date">تاريخ الرفع: {item.get('addeddate', '')[:10]}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                st.video(video_url)
                                
                                # أدوات التحكم والبث
                                with st.expander("🔗 خيارات البث والتحميل"):
                                    c1, c2 = st.columns(2)
                                    with c1:
                                        st.markdown("**📺 بث للشاشة (QR)**")
                                        st.image(generate_qr(video_url), width=120)
                                    with c2:
                                        st.markdown("**📥 الحفظ والمشاركة**")
                                        st.link_button("تحميل الملف المباشر", video_url)
                                        wa_url = f"https://wa.me/?text={urllib.parse.quote('شاهد ' + clean_t + ': ' + video_url)}"
                                        st.link_button("إرسال عبر WhatsApp", wa_url)
                            st.divider()
        except:
            st.error("⚠️ فشل الاتصال بالسيرفر، جرب مرة أخرى.")
