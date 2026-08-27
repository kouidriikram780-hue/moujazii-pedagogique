import streamlit as st
import pandas as pd
from collections import defaultdict
from PIL import Image
import pytesseract
import re
import os

# ============================================
# إعداد مسار Tesseract (مهم جداً للنشر)
# ============================================
if os.name == 'nt':  # نظام Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
else:  # نظام Linux (Streamlit Cloud)
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# ============================================
# إعدادات الصفحة
# ============================================
st.set_page_config(
    page_title="المجزئ البيداغوجي",
    page_icon="📚",
    layout="centered"
)

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
# اختيار المادة والمستوى
# ============================================
col1, col2 = st.columns(2)
with col1:
    niveau = st.selectbox("📌 المستوى", ["1 متوسط", "2 متوسط", "3 متوسط", "4 متوسط"])
with col2:
    matiere = st.selectbox("📖 المادة", ["رياضيات", "علوم", "لغة عربية", "لغة فرنسية", "إنجليزية", "تاريخ وجغرافيا"])

st.divider()

# ============================================
# رفع الصورة (الميزة الأساسية)
# ============================================
st.subheader("📸 رفع شبكة التقييم")
st.caption("صوّر الشبكة الورقية وارفعها")

uploaded_file = st.file_uploader("اختر صورة الشبكة", type=["jpg", "png", "jpeg"])

# متغير لتخزين البيانات المستخرجة من الصورة
df_image_data = None

if uploaded_file is not None:
    try:
        img = Image.open(uploaded_file)
        # ✅ تم التعديل هنا: use_column_width -> use_container_width
        st.image(img, caption="الصورة المرفوعة", use_container_width=True)
        
        if st.button("🔍 استخراج البيانات من الصورة"):
            with st.spinner("جاري تحليل الصورة واستخراج البيانات..."):
                try:
                    # استخراج النص من الصورة
                    text = pytesseract.image_to_string(img, lang='ara')
                    
                    if text.strip():
                        st.success("✅ تم استخراج النص بنجاح!")
                        with st.expander("📝 عرض النص المستخرج"):
                            st.text(text)
                        
                        # محاولة استخراج الأسماء والتقديرات
                        lines = text.strip().split('\n')
                        data = []
                        for line in lines:
                            # البحث عن اسم + تقديرات (م، أ، ج، د)
                            match = re.search(r'([\u0600-\u06FF\s]{2,})\s+([\u0600-\u06FF])\s+([\u0600-\u06FF])\s+([\u0600-\u06FF])\s+([\u0600-\u06FF])', line)
                            if match:
                                name = match.group(1).strip()
                                m1 = match.group(2)
                                m2 = match.group(3)
                                m3 = match.group(4)
                                m4 = match.group(5)
                                data.append([name, m1, m2, m3, m4])
                        
                        if data:
                            df_image_data = pd.DataFrame(data, columns=['الاسم', 'م1', 'م2', 'م3', 'م4'])
                            # ✅ تم التعديل هنا أيضاً use_container_width
                            st.dataframe(df_image_data, use_container_width=True)
                            st.info("📌 تم استخراج البيانات. يمكنك الآن الضغط على 'تحليل البيانات' أدناه.")
                        else:
                            st.warning("⚠️ لم يتم العثور على بيانات منظمة. حاول تحسين جودة الصورة.")
                    else:
                        st.error("❌ لم يتم استخراج أي نص. تأكد من وضوح الصورة.")
                        
                except Exception as e:
                    st.error(f"❌ حدث خطأ أثناء معالجة الصورة: {e}")
    except Exception as e:
        st.error(f"❌ خطأ في فتح الصورة: {e}")

st.markdown("---")

# ============================================
# الإدخال اليدوي (كخيار بديل)
# ============================================
st.subheader("✏️ أو أدخل البيانات يدوياً")
st.caption("إذا لم تعمل ميزة الصورة، يمكنك الإدخال يدوياً")

names = st.text_area("👨‍🎓 أسماء التلاميذ (كل اسم في سطر)")
grades_m1 = st.text_area("📊 تقديرات المعيار 1 (كل تقدير في سطر)")
grades_m2 = st.text_area("📊 تقديرات المعيار 2 (كل تقدير في سطر)")
grades_m3 = st.text_area("📊 تقديرات المعيار 3 (كل تقدير في سطر)")
grades_m4 = st.text_area("📊 تقديرات المعيار 4 (كل تقدير في سطر)")

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
# زر التحليل النهائي
# ============================================
if st.button("🚀 تحليل البيانات وإنشاء التقرير", type="primary"):
    # محاولة استخدام البيانات من الصورة أولاً
    if 'df_image_data' in locals() and df_image_data is not None and not df_image_data.empty:
        df_analysis = df_image_data.copy()
    elif names and grades_m1:
        name_list = names.strip().split('\n')
        m1_list = grades_m1.strip().split('\n') if grades_m1 else []
        m2_list = grades_m2.strip().split('\n') if grades_m2 else []
        m3_list = grades_m3.strip().split('\n') if grades_m3 else []
        m4_list = grades_m4.strip().split('\n') if grades_m4 else []
        
        max_len = len(name_list)
        m1_list = m1_list + [''] * (max_len - len(m1_list))
        m2_list = m2_list + [''] * (max_len - len(m2_list))
        m3_list = m3_list + [''] * (max_len - len(m3_list))
        m4_list = m4_list + [''] * (max_len - len(m4_list))
        
        data = []
        for i in range(max_len):
            data.append([name_list[i], m1_list[i], m2_list[i], m3_list[i], m4_list[i]])
        df_analysis = pd.DataFrame(data, columns=['الاسم', 'م1', 'م2', 'م3', 'م4'])
    else:
        st.error("❌ الرجاء إدخال البيانات أو رفع صورة واستخراج البيانات منها.")
        st.stop()
    
    # تطبيق التحليل
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
    st.success(f"✅ تم تحليل {len(df_analysis)} تلميذاً بنجاح")
    
    # إحصائيات
    st.subheader("📈 إحصائيات الأفواج")
    col1, col2, col3 = st.columns(3)
    counts = df_analysis['الفوج'].value_counts()
    with col1:
        st.metric("🆘 الإنقاذ", counts.get("فوج إنقاذ عاجل (د)", 0))
    with col2:
        st.metric("📚 الدعم", counts.get("فوج دعم مكثف (ج)", 0))
    with col3:
        st.metric("🌟 التعزيز", counts.get("مرشد (أ/ب)", 0))
    
    # عرض الجدول
    with st.expander("📊 عرض جدول التلاميذ"):
        st.dataframe(df_analysis, use_container_width=True)
    
    # التقرير
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
    
    # تحميل التقرير
    csv = df_analysis.to_csv(index=False)
    st.download_button(
        label="📥 تحميل التقرير (Excel)",
        data=csv,
        file_name=f"تقرير_{matiere}_{niveau}.csv",
        mime="text/csv"
    )
