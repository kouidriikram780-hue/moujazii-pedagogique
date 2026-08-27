import streamlit as st
import pandas as pd
from collections import defaultdict
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import re
import os
import numpy as np

# ============================================
# إعداد مسار Tesseract
# ============================================
if os.name == 'nt':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
else:
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# ============================================
# دالة معالجة الصورة قبل OCR
# ============================================
def preprocess_image(img):
    """تحسين جودة الصورة قبل استخراج النصوص"""
    # تحويل إلى أبيض وأسود
    img = img.convert('L')
    # تحسين التباين
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    # زيادة الحدة
    img = img.filter(ImageFilter.SHARPEN)
    return img

# ============================================
# دالة استخراج البيانات من النص
# ============================================
def extract_data_from_text(text):
    """استخراج الأسماء والتقديرات من النص المستخرج"""
    lines = text.strip().split('\n')
    data = []
    for line in lines:
        # البحث عن اسم + 4 تقديرات (أ، ب، ج، د)
        match = re.search(r'([\u0600-\u06FF\s]{2,})\s+([\u0600-\u06FF])\s+([\u0600-\u06FF])\s+([\u0600-\u06FF])\s+([\u0600-\u06FF])', line)
        if match:
            name = match.group(1).strip()
            m1 = match.group(2)
            m2 = match.group(3)
            m3 = match.group(4)
            m4 = match.group(5)
            data.append([name, m1, m2, m3, m4])
    return data

# ============================================
# واجهة Streamlit
# ============================================
st.set_page_config(page_title="المجزئ البيداغوجي", page_icon="📚", layout="centered")

st.title("📚 المجزئ البيداغوجي الذكي")
st.markdown("### للطور المتوسط - التعلم بالأقران")

# كود التفعيل
st.sidebar.header("🔑 تفعيل المنتج")
code = st.sidebar.text_input("أدخل كود التفعيل", type="password")
VALID_CODES = ["MOYEN2025", "MED2026", "TEACHERDZ"]

if code not in VALID_CODES:
    st.sidebar.warning("⚠️ كود غير صحيح")
    st.stop()
else:
    st.sidebar.success("✅ تم التفعيل")

# اختيار المادة والمستوى
col1, col2 = st.columns(2)
with col1:
    niveau = st.selectbox("📌 المستوى", ["1 متوسط", "2 متوسط", "3 متوسط", "4 متوسط"])
with col2:
    matiere = st.selectbox("📖 المادة", ["رياضيات", "علوم", "لغة عربية", "لغة فرنسية", "إنجليزية", "تاريخ"])

st.divider()

# ============================================
# رفع الصورة (الميزة الأساسية)
# ============================================
st.subheader("📸 رفع شبكة التقييم")
uploaded_file = st.file_uploader("اختر صورة الشبكة", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    try:
        # فتح الصورة
        img = Image.open(uploaded_file)
        st.image(img, caption="الصورة الأصلية", use_container_width=True)
        
        # معالجة الصورة
        processed_img = preprocess_image(img)
        st.image(processed_img, caption="الصورة بعد المعالجة (للقراءة)", use_container_width=True)
        
        if st.button("🔍 استخراج البيانات"):
            with st.spinner("جاري تحليل الصورة..."):
                try:
                    # استخراج النص بعد المعالجة
                    text = pytesseract.image_to_string(processed_img, lang='ara')
                    
                    if text.strip():
                        st.success("✅ تم استخراج النص!")
                        with st.expander("📝 عرض النص المستخرج"):
                            st.text(text)
                        
                        # استخراج البيانات من النص
                        data = extract_data_from_text(text)
                        
                        if data:
                            df = pd.DataFrame(data, columns=['الاسم', 'م1', 'م2', 'م3', 'م4'])
                            st.dataframe(df, use_container_width=True)
                            st.info("📌 تم استخراج البيانات. اضغط على 'تحليل البيانات' أدناه.")
                            # حفظ البيانات في session_state
                            st.session_state['df_image'] = df
                        else:
                            st.warning("⚠️ لم يتم العثور على بيانات. تأكد من وضوح الصورة.")
                    else:
                        st.error("❌ لم يتم استخراج أي نص. حاول تصوير الشبكة بوضوح.")
                        
                except Exception as e:
                    st.error(f"❌ خطأ: {e}")
    except Exception as e:
        st.error(f"❌ خطأ في فتح الصورة: {e}")

st.markdown("---")

# ============================================
# دوال التحليل (نفسها)
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
# زر التحليل
# ============================================
if st.button("🚀 تحليل البيانات وإنشاء التقرير", type="primary"):
    # محاولة استخدام البيانات من الصورة
    if 'df_image' in st.session_state and not st.session_state['df_image'].empty:
        df_analysis = st.session_state['df_image'].copy()
    else:
        st.error("❌ الرجاء رفع صورة واستخراج البيانات أولاً.")
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
    st.success(f"✅ تم تحليل {len(df_analysis)} تلميذاً")
    
    st.subheader("📈 إحصائيات الأفواج")
    col1, col2, col3 = st.columns(3)
    counts = df_analysis['الفوج'].value_counts()
    with col1:
        st.metric("🆘 الإنقاذ", counts.get("فوج إنقاذ عاجل (د)", 0))
    with col2:
        st.metric("📚 الدعم", counts.get("فوج دعم مكثف (ج)", 0))
    with col3:
        st.metric("🌟 التعزيز", counts.get("مرشد (أ/ب)", 0))
    
    with st.expander("📊 عرض جدول التلاميذ"):
        st.dataframe(df_analysis, use_container_width=True)
    
    st.subheader("📋 التقرير")
    template = memo_templates.get(matiere, memo_templates['رياضيات'])
    
    st.markdown(f"**المادة:** {matiere}  |  **المستوى:** {niveau}  |  **عدد التلاميذ:** {len(df_analysis)}")
    if not mentors.empty:
        st.info(f"👨‍🏫 المرشدون: {', '.join(mentors['الاسم'].tolist())}")
    
    for i, (difficulty, students) in enumerate(groups.items(), 1):
        with st.expander(f"🔹 المجموعة {i} - الصعوبة: {difficulty}"):
            st.write(f"**التلاميذ:** {', '.join(students)}")
            st.write(f"**عددهم:** {len(students)}")
            st.write(f"**🛠️ الاستراتيجية:** {template['strategies']}")
            st.write(f"**📝 الأنشطة:** {template['activities']}")
    
    csv = df_analysis.to_csv(index=False)
    st.download_button("📥 تحميل التقرير", csv, f"تقرير_{matiere}.csv", "text/csv")
