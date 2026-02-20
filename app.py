import streamlit as st
import requests
from datetime import datetime, timedelta
import re
import urllib.parse

# ==========================================
# 1. إعدادات الهوية والتصميم (UI/UX)
# ==========================================
st.set_page_config(page_title="Amin Stream V900 - TITAN", layout="wide", page_icon="🎬")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; }
    .stApp { background-color: #0b0e14; }
    
    /* تصميم كارت المسلسل */
    .movie-card {
        background: linear-gradient(145deg, #161b22, #0d1117);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 25px;
        border: 1px solid #30363d;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        transition: 0.3s;
    }
    .movie-card:hover { border-color: #238636; transform: translateY(-5px); }
    
    .movie-title { color: #2ea043; font-size: 24px; font-weight: bold; margin-bottom: 10px; }
    .movie-date { color: #8b949e; font-size: 14px; }
    .badge { background-color: #238636; color: white; padding: 2px 10px; border-radius: 10px; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. الدوال الذكية (Logic)
# ==========================================

def clean_name(text):
    """تنظيف اسم المسلسل من الكلمات المزعجة"""
    unwanted = ['Arabseed', 'عرب سيد', 'مشاهدة', 'تحميل', 'حلقة', 'كاملة', 'H d', '720p', '1080p', 'WEB-DL']
    for word in unwanted:
        text = re.sub(word, '', text, flags=re.IGNORECASE)
    return text.strip()

def get_metadata(identifier):
    """جلب تفاصيل الملف (فيديو + بوستر)"""
    try:
        r = requests.get(f"https://archive.org/metadata/{identifier}").json()
        server = r.get('server')
        dir_path = r.get('dir')
        files = r.get('files', [])
        
        video = None
        poster = "https://via.placeholder.com/300x450/161b22/2ea043?text=RAMADAN+2026"
        
        for f in files:
            name = f['name']
            if not video and name.lower().endswith(('.mp4', '.mkv')):
                video = f"https://{server}{dir_path}/{name}"
            if name.lower().endswith(('.jpg', '.png', '.jpeg')):
                poster = f"https://{server}{dir_path}/{name}"
                
        return video, poster
    except:
        return None, None

def generate_qr(link):
    """توليد رابط QR Code للبث على الشاشة"""
    encoded_link = urllib.parse.quote(link)
    return f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={encoded_link}"

# ==========================================
# 3. واجهة المستخدم الرئيسية
# ==========================================

st.title("🎬 AMIN STREAM | TITAN V900")
st.markdown("<p style='color: #8b949e;'>رادار مسلسلات رمضان 2026 - نظام البث الذكي</p>", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3163/3163478.png", width=100)
    st.header("🔍 ابحث عن مسلسلك")
    query = st.text_input("اسم المسلسل", placeholder="مثال: المداح، عرس الجن...")
    search_btn = st.button("🚀 اضرب نار (بحث)")
    st.divider()
    st.info("نصيحة: استخدم متصفح الشاشة لمسح الـ QR والتشغيل فوراً.")

if search_btn:
    with st.spinner('📡 جاري سحب الترددات وفحص الروابط...'):
        # استعلام الأرشيف
        today = datetime.now().strftime('%Y-%m-%d')
        q = f'title:("{query if query else "2026"}") AND mediatype:(video)'
        params = {'q': q, 'fl[]': ['identifier', 'title', 'addeddate'], 'sort[]': 'addeddate desc', 'rows': '20', 'output': 'json'}
        
        try:
            results = requests.get("https://archive.org/advancedsearch.php", params=params).json().get('response', {}).get('docs', [])
            
            if not results:
                st.error("⚠️ مفيش نتائج بالاسم ده لـ 2026 حالياً.")
            else:
                for item in results:
                    video_url, poster_url = get_metadata(item['identifier'])
                    
                    if video_url:
                        # إنشاء الكارت
                        with st.container():
                            col_img, col_txt = st.columns([1, 3])
                            
                            with col_img:
                                st.image(poster_url, use_column_width=True)
                            
                            with col_txt:
                                clean_t = clean_name(item['title'])
                                st.markdown(f"""
                                    <div class="movie-card">
                                        <div class="movie-title">{clean_t} <span class="badge">LIVE 2026</span></div>
                                        <div class="movie-date">تاريخ الرفع: {item.get('addeddate', '')[:10]}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                # مشغل الفيديو
                                st.video(video_url)
                                
                                # أدوات المشاركة والبث
                                exp = st.expander("🛠️ خيارات البث والمشاركة")
                                with exp:
                                    c1, c2, c3 = st.columns(3)
                                    with c1:
                                        st.markdown(f"**📺 بث للشاشة (DLNA)**")
                                        st.image(generate_qr(video_url), caption="امسح الكود بالشاشة")
                                    with c2:
                                        st.markdown("**🔗 روابط سريعة**")
                                        st.link_button("📥 تحميل مباشر", video_url)
                                        # مشاركة واتساب
                                        wa_link = f"https://wa.me/?text={urllib.parse.quote('اتفرج معايا على ' + clean_t + ' هنا: ' + video_url)}"
                                        st.link_button("🟢 واتساب", wa_link)
                                    with c3:
                                        st.markdown("**📡 برامج خارجية**")
                                        st.code(video_url, language="text")
                                        st.caption("انسخ الرابط لـ VLC")
                                
                            st.divider()
        except Exception as e:
            st.error(f"حدث خطأ في الاتصال: {e}")

else:
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <img src="https://cdn-icons-png.flaticon.com/512/2585/2585090.png" width="150" style="opacity: 0.5;">
        <h3 style="color: #30363d;">في انتظار أوامرك يا محمد.. ابحث عن أي مسلسل</h3>
    </div>
    """, unsafe_allow_html=True)
