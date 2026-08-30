import streamlit as st
import pandas as pd
from collections import defaultdict
from PIL import Image
import requests
import re
import io
import time
import base64

# ============================================
# إعدادات الصفحة
# ============================================
st.set_page_config(page_title="المجزئ البيداغوجي", page_icon="📚", layout="centered")

st.title("📚 المجزئ البيداغوجي الذكي")
st.markdown("### للطور المتوسط - التعلم بالأقران")

# ============================================
# كود التفعيل (للبيع)
# ============================================
st.sidebar.header("🔑 تفعيل المنتج")
code = st.sidebar.text_input("أدخل كود التفعيل", type="password")
VALID_CODES = ["MOYEN2025", "MED2026", "TEACHERDZ"]

if code not in VALID_CODES:
    st.sidebar.warning("⚠️ كود غير صحيح. اشترِ المنتج للوصول")
    st.stop()
else:
    st.sidebar.success("✅ تم التفعيل بنجاح")

# ============================================
# مفتاح DeepRead API (من st.secrets)
# ============================================
DEEPREAD_API_KEY = st.secrets.get("DEEPREAD_API_KEY", "YOUR_API_KEY_HERE")

# ============================================
# دالة استخراج النص باستخدام DeepRead API
# ============================================
def extract_text_with_deepread(image_bytes):
    """إرسال الصورة إلى DeepRead API واسترجاع النص"""
    url = "https://api.deepread.tech/v1/process"
    headers = {"X-API-Key": DEEPREAD_API_KEY}
    files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
    data = {'pipeline': 'fast'}
    
    try:
        response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            # محاولة استخراج النص من الرد
            if 'text' in result:
                return result['text'], None
            elif 'result' in result and 'text' in result['result']:
                return result['result']['text'], None
            else:
                return None, "❌ لم يتم العثور على نص في الرد."
        else:
            return None, f"❌ خطأ في الاتصال: {response.status_code} - {response.text}"
    except requests.exceptions.Timeout:
        return None, "❌ انتهى الوقت المحدد للاتصال بالخادم."
    except Exception as e:
        return None, f"❌ خطأ: {e}"

# ============================================
# دالة استخراج البيانات الذكية من النص
# ============================================
def extract_students_smart(text):
    """استخراج الأسماء والتقديرات من النص"""
    lines = text.strip().split('\n')
    students = []
    
    for line in lines:
        line = line.strip()
        if len(line) < 3:
            continue
        
        # البحث عن التقديرات (م، أ، ج، د، ح، غ) في السطر
        grades = re.findall(r'[مأجدحغ]', line)
        
        if len(grades) >= 4:
            grades = grades[:4]
            
            # إزالة التقديرات من النص للحصول على الاسم
            name_text = line
            for g in grades:
                name_text = name_text.replace(g, '', 1)
            
            # تنظيف النص (إزالة الأرقام والرموز)
            name_text = re.sub(r'[0-9\|\-\(\)\.\,\s]+', ' ', name_text)
            name_text = re.sub(r'\s+', ' ', name_text).strip()
            
            if len(name_text) > 2 and re.search(r'[\u0600-\u06FF]', name_text):
                students.append([name_text] + grades)
    
    # إذا لم نجد نتائج، نحاول نمطاً آخر (البحث عن أسماء متبوعة بأرقام)
    if not students:
        for line in lines:
            line = line.strip()
            # البحث عن اسم عربي + 4 أرقام أو تقديرات
            match = re.search(r'([\u0600-\u06FF\s]{2,})\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', line)
            if match:
                name = match.group(1).strip()
                # تحويل الأرقام إلى تقديرات تقريبية
                m1 = 'ج' if int(match.group(2)) < 50 else 'أ'
                m2 = 'ج' if int(match.group(3)) < 50 else 'أ'
                m3 = 'ج' if int(match.group(4)) < 50 else 'أ'
                m4 = 'ج' if int(match.group(5)) < 50 else 'أ'
                students.append([name, m1, m2, m3, m4])
    
    return students

# ============================================
# اختيار المادة والمستوى
# ============================================
col1, col2 = st.columns(2)
with col1:
    niveau = st.selectbox("📌 المستوى", ["1 متوسط", "2 متوسط", "3 متوسط", "4 متوسط"])
with col2:
    matiere = st.selectbox("📖 المادة", ["رياضيات", "علوم", "لغة عربية", "لغة فرنسية", "إنجليزية", "تاريخ وجغرافيا"])

st.divider()

# ============================================
# رفع الصورة
# ============================================
st.subheader("📸 رفع شبكة التقييم")
st.caption("صوّر الشبكة الورقية بوضوح وارفعها")

uploaded_file = st.file_uploader("اختر صورة الشبكة", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    try:
        img = Image.open(uploaded_file)
        st.image(img, caption="الصورة المرفوعة", use_container_width=True)
        
        if st.button("🔍 استخراج البيانات من الصورة", type="primary"):
            with st.spinner("جاري إرسال الصورة إلى خادم DeepRead..."):
                # قراءة بيانات الصورة
                file_bytes = uploaded_file.getvalue()
                
                # إرسال إلى DeepRead
                parsed_text, error = extract_text_with_deepread(file_bytes)
                
                if error:
                    st.error(error)
                elif parsed_text:
                    st.success("✅ تم استخراج النص بنجاح!")
                    with st.expander("📝 عرض النص المستخرج"):
                        st.text(parsed_text)
                    
                    # استخراج البيانات من النص
                    data = extract_students_smart(parsed_text)
                    
                    if data:
                        df = pd.DataFrame(data, columns=['الاسم', 'م1', 'م2', 'م3', 'م4'])
                        st.success(f"✅ تم استخراج بيانات {len(df)} تلميذاً بنجاح!")
                        st.dataframe(df, use_container_width=True)
                        st.session_state['df_image'] = df
                    else:
                        st.warning("⚠️ لم يتم العثور على بيانات. حاول تحسين جودة الصورة.")
                else:
                    st.error("❌ لم يتم استخراج أي نص. تأكد من وضوح الصورة.")
                    
    except Exception as e:
        st.error(f"❌ خطأ في فتح الصورة: {e}")

st.markdown("---")

# ============================================
# دوال التحليل
# ============================================
def get_difficulties(row):
    difficulties = []
    if row['م1'] == 'ج':
        difficulties.append('المعيار 1')
    if row['م2'] == 'ج':
        difficulties.append('المعيار 2')
    if row['م3'] == 'ج':
        difficulties.append('المعيار 3')
    if row['م4'] == 'ج':
        difficulties.append('المعيار 4')
    return difficulties

def classify_student(row):
    grades = [row['م1'], row['م2'], row['م3'], row['م4']]
    if all(g in ['م', 'أ'] for g in grades):
        return 'مرشد (أ/ب)'
    elif 'ج' in grades:
        count_j = grades.count('ج')
        if count_j >= 3:
            return 'فوج إنقاذ عاجل (د)'
        else:
            return 'فوج دعم مكثف (ج)'
    else:
        return 'غير مصنف'

memo_templates = {
    'رياضيات': {'strategies': 'حل المشكلات + التعلم التعاوني', 'activities': 'تمارين تطبيقية، مسائل حياتية'},
    'علوم': {'strategies': 'التجريب + الاستقصاء العلمي', 'activities': 'تجارب عملية، مشاريع بحثية'},
    'لغة عربية': {'strategies': 'التعلم باللعب + القراءة الموجهة', 'activities': 'قراءة نصوص، كتابة إبداعية'},
    'لغة فرنسية': {'strategies': 'التعلم بالمشاريع + المحاكاة', 'activities': 'حوارات، أغاني'},
    'إنجليزية': {'strategies': 'Total Physical Response + Storytelling', 'activities': 'قصص مصورة، أغاني'},
    'تاريخ': {'strategies': 'التعلم بالخرائط + السرد القصصي', 'activities': 'خرائط ذهنية، خطوط زمنية'}
}

# ============================================
# زر التقسيم النهائي
# ============================================
if st.button("🚀 تقسيم التلاميذ إلى أفواج وإنشاء التقرير", type="secondary"):
    if 'df_image' in st.session_state and not st.session_state['df_image'].empty:
        df_analysis = st.session_state['df_image'].copy()
    else:
        st.error("❌ الرجاء استخراج البيانات من الصورة أولاً.")
        st.stop()
    
    df_analysis['الصعوبات'] = df_analysis.apply(get_difficulties, axis=1)
    df_analysis['الفوج'] = df_analysis.apply(classify_student, axis=1)
    
    mentors = df_analysis[df_analysis['الفوج'] == 'مرشد (أ/ب)']
    students_need_support = df_analysis[df_analysis['الفوج'] != 'مرشد (أ/ب)']
    
    groups = defaultdict(list)
    for _, student in students_need_support.iterrows():
        if student['الصعوبات']:
            key = ', '.join(student['الصعوبات'])
        else:
            key = 'صعوبة غير محددة'
        groups[key].append(student['الاسم'])
    
    st.balloons()
    st.success(f"✅ تم تقسيم {len(df_analysis)} تلميذاً إلى أفواج!")
    
    # إحصائيات
    st.subheader("📈 إحصائيات الأفواج")
    col1, col2, col3 = st.columns(3)
    counts = df_analysis['الفوج'].value_counts()
    with col1:
        st.metric("🆘 فوج الإنقاذ", counts.get("فوج إنقاذ عاجل (د)", 0))
    with col2:
        st.metric("📚 فوج الدعم", counts.get("فوج دعم مكثف (ج)", 0))
    with col3:
        st.metric("🌟 المرشدون", counts.get("مرشد (أ/ب)", 0))
    
    with st.expander("📊 عرض جدول التلاميذ"):
        st.dataframe(df_analysis, use_container_width=True)
    
    st.subheader("📋 تقرير المعالجة البيداغوجية")
    template = memo_templates.get(matiere, memo_templates['رياضيات'])
    
    st.markdown(f"""
    <div style="background-color: #f0f4ff; padding: 15px; border-radius: 15px;">
        <b>المادة:</b> {matiere}<br>
        <b>المستوى:</b> {niveau}<br>
        <b>عدد التلاميذ:</b> {len(df_analysis)}<br>
        <b>عدد المرشدين:</b> {len(mentors)}
    </div>
    """, unsafe_allow_html=True)
    
    if not mentors.empty:
        st.info(f"👨‍🏫 المرشدون: {', '.join(mentors['الاسم'].tolist())}")
    
    st.divider()
    
    for i, (difficulty, students) in enumerate(groups.items(), 1):
        with st.expander(f"🔹 المجموعة {i} - الصعوبة: {difficulty}"):
            st.write(f"**التلاميذ:** {', '.join(students)}")
            st.write(f"**عددهم:** {len(students)}")
            st.write(f"**🛠️ الاستراتيجية:** {template['strategies']}")
            st.write(f"**📝 الأنشطة:** {template['activities']}")
    
    csv = df_analysis.to_csv(index=False)
    st.download_button(
        label="📥 تحميل التقرير (Excel)",
        data=csv,
        file_name=f"تقرير_{matiere}_{niveau}.csv",
        mime="text/csv"
                )
