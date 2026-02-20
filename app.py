import streamlit as st
import requests
from datetime import datetime, timedelta
import re

# إعدادات الصفحة
st.set_page_config(page_title="Amin Stream - Ramadan 2026", layout="wide")

# تصميم واجهة المستخدم (CSS)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #1b5e20; color: white; }
    .video-card { border: 1px solid #333; padding: 15px; border-radius: 10px; margin-bottom: 10px; background-color: #161b22; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 MOHAMMED AMIN | Master Stream V800")
st.subheader("رادار مسلسلات رمضان 2026 - مشاهدة مباشرة")

# الجانب الأيسر (Sidebar) للمدخلات
with st.sidebar:
    st.header("🔍 محرك البحث")
    query = st.text_input("اسم المسلسل (مثلاً: وحوش، المداح)", placeholder="اتركه فارغاً لجلب كل الجديد...")
    
    col1, col2 = st.columns(2)
    with col1:
        search_btn = st.button("🚀 بحث")
    with col2:
        stop_btn = st.button("🛑 إيقاف")

    st.info("النسخة تعمل بنظام المشاهدة المباشرة دون مغادرة الموقع.")

# وظيفة البحث
def fetch_data(search_query):
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # بناء الاستعلام لضمان 2026 فقط
    if search_query:
        q = f'title:("{search_query}") AND addeddate:[2026-01-01 TO {today}]'
    else:
        q = f'title:("2026") AND addeddate:[{yesterday} TO {today}]'
    
    params = {
        'q': q,
        'fl[]': ['identifier', 'title', 'addeddate'],
        'sort[]': 'addeddate desc',
        'rows': '40',
        'output': 'json'
    }
    
    try:
        r = requests.get("https://archive.org/advancedsearch.php", params=params, timeout=10)
        return r.json().get('response', {}).get('docs', [])
    except:
        return []

# وظيفة استخراج الرابط المباشر
def get_direct_link(identifier):
    try:
        meta = requests.get(f"https://archive.org/metadata/{identifier}").json()
        server = meta.get('server')
        dir_path = meta.get('dir')
        for f in meta.get('files', []):
            if f['name'].lower().endswith(('.mp4', '.mkv')):
                return f"https://{server}{dir_path}/{f['name']}"
    except:
        return None

# تنفيذ البحث والعرض
if search_btn:
    if stop_btn:
        st.warning("تم إيقاف العملية.")
    else:
        with st.spinner('جاري فحص سيرفرات الأرشيف وجلب الروابط الحية...'):
            results = fetch_data(query)
            
            if not results:
                st.error("لم يتم العثور على نتائج جديدة لعام 2026 بهذا الاسم.")
            else:
                for item in results:
                    title = item['title']
                    # تنظيف العنوان
                    clean_title = re.sub(r'Arabseed|عرب سيد|مشاهدة|تحميل', '', title, flags=re.IGNORECASE).strip()
                    
                    video_url = get_direct_link(item['identifier'])
                    
                    if video_url:
                        with st.container():
                            st.markdown(f"""<div class="video-card">
                                <h4>📺 {clean_title}</h4>
                                <p style='color: gray;'>تاريخ الرفع: {item.get('addeddate', '')[:10]}</p>
                            </div>""", unsafe_allow_html=True)
                            
                            # مشغل الفيديو المباشر
                            st.video(video_url)
                            
                            # روابط إضافية
                            c1, c2 = st.columns([1, 5])
                            with c1:
                                st.download_button("📥 تحميل", data="", file_name=f"{clean_title}.mp4", help="اضغط يمين وحفظ باسم على رابط الفيديو")
                            st.divider()

# تعليمات التشغيل لـ Streamlit
if not search_btn:
    st.info("قم بكتابة اسم المسلسل في القائمة الجانبية واضغط 'بحث' للبدء.")
