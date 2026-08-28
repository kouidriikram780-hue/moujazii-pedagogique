import streamlit as st
import pandas as pd
from collections import defaultdict
from PIL import Image
import requests
import json
import re
import io

# ============================================
# إعدادات الصفحة
# ============================================
st.set_page_config(page_title="المجزئ البيداغوجي", page_icon="📚", layout="centered")

st.title("📚 المجزئ البيداغوجي الذكي")
st.markdown("### للطور المتوسط - التعلم بالأقران")

# كود التفعيل (للبيع)
st.sidebar.header("🔑 تفعيل المنتج")
code = st.sidebar.text_input("أدخل كود التفعيل", type="password")
VALID_CODES = ["MOYEN2025", "MED2026", "TEACHERDZ"]

if code not in VALID_CODES:
    st.sidebar.warning("⚠️ كود غير صحيح. اشترِ المنتج للوصول")
    st.stop()
else:
    st.sidebar.success("✅ تم التفعيل بنجاح")

# اختيار المادة والمستوى
col1, col2 = st.columns(2)
with col1:
    niveau = st.selectbox("📌 المستوى", ["1 متوسط", "2 متوسط", "3 متوسط", "4 متوسط"])
with col2:
    matiere = st.selectbox("📖 المادة", ["رياضيات", "علوم", "لغة عربية", "لغة فرنسية", "إنجليزية", "تاريخ وجغرافيا"])

st.divider()

# ============================================
# OCR.space API - استخراج النص من الصورة
# ============================================
st.subheader("📸 رفع شبكة التقييم")
st.caption("صوّر الشبكة الورقية بوضوح وارفعها")

# ضع مفتاح API الخاص بك هنا
OCR_API_KEY = st.secrets.get("OCR_API_KEY", "helloworld")  # استخدم st.secrets أو ضع المفتاح مباشرة

uploaded_file = st.file_uploader("اختر صورة الشبكة", type=["jpg", "png", "jpeg"])

def ocr_space_file(file_bytes, api_key=OCR_API_KEY, language='ara'):
    """إرسال الصورة إلى OCR.space واسترجاع النص"""
    payload = {
        'isOverlayRequired': False,
        'apikey': api_key,
        'language': language,
        'isTable': True,
        'detectOrientation': True,
        'scale': True,
    }
    
    files = {'file': ('image.jpg', file_bytes, 'image/jpeg')}
    
    try:
        response = requests.post('https://api.ocr.space/parse/image', files=files, data=payload)
        result = response.json()
        
        if result.get('IsErroredOnProcessing'):
            error_msg = result.get('ErrorMessage', ['خطأ غير معروف'])[0]
            return None, f"❌ خطأ في OCR: {error_msg}"
        
        if result.get('ParsedResults'):
            parsed_text = result['ParsedResults'][0]['ParsedText']
            return parsed_text, None
        else:
            return None, "❌ لم يتم العثور على نص في الصورة."
            
    except Exception as e:
        return None, f"❌ خطأ في الاتصال: {e}"

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
        
        # البحث عن التقديرات (م، أ، ج، د) في السطر
        grades = re.findall(r'[مأجد]', line)
        
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
    
    # إذا لم نجد نتائج، نحاول نمطاً آخر
    if not students:
        for line in lines:
            line = line.strip()
            match = re.search(r'([\u0600-\u06FF\s]{4,})\s+([\u0600-\u06FF])\s+([\u0600-\u06FF])\s+([\u0600-\u06FF])\s+([\u0600-\u06FF])', line)
            if match:
                name = match.group(1).strip()
                m1, m2, m3, m4 = match.group(2), match.group(3), match.group(4), match.group(5)
                if all(g in ['م', 'أ', 'ج', 'د'] for g in [m1, m2, m3, m4]):
                    students.append([name, m1, m2, m3, m4])
    
    return students

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
# رفع الصورة ومعالجتها
# ============================================
if uploaded_file is not None:
    try:
        # عرض الصورة
        img = Image.open(uploaded_file)
        st.image(img, caption="الصورة المرفوعة", use_container_width=True)
        
        if st.button("🔍 استخراج البيانات من الصورة", type="primary"):
            with st.spinner("جاري إرسال الصورة إلى OCR.space..."):
                # قراءة بيانات الصورة
                file_bytes = uploaded_file.getvalue()
                
                # إرسال إلى OCR.space
                parsed_text, error = ocr_space_file(file_bytes)
                
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
                        st.warning("⚠️ لم يتم العثور على بيانات. حاول تحسين جودة الصورة أو استخدام شبكة أوضح.")
                else:
                    st.error("❌ لم يتم استخراج أي نص. تأكد من وضوح الصورة.")
                    
    except Exception as e:
        st.error(f"❌ خطأ: {e}")

st.markdown("---")

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
