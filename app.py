import streamlit as st
import pandas as pd
from collections import defaultdict

# ============================================
# إعدادات الصفحة
# ============================================
st.set_page_config(page_title="المجزئ البيداغوجي", page_icon="📚", layout="centered")

st.title("📚 المجزئ البيداغوجي الذكي")
st.markdown("### للطور المتوسط - التعلم بالأقران")

# كود التفعيل
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
# الإدخال عبر مربعات نصية
# ============================================
st.subheader("✏️ أدخل بيانات التلاميذ")
st.caption("اكتب كل اسم في سطر، وكل تقدير في سطر مقابل")

names = st.text_area("👨‍🎓 أسماء التلاميذ (كل اسم في سطر)", height=150)
m1 = st.text_area("📊 تقديرات المعيار 1 (م، أ، ج، د)", height=150)
m2 = st.text_area("📊 تقديرات المعيار 2 (م، أ، ج، د)", height=150)
m3 = st.text_area("📊 تقديرات المعيار 3 (م، أ، ج، د)", height=150)
m4 = st.text_area("📊 تقديرات المعيار 4 (م، أ، ج، د)", height=150)

# ============================================
# دوال التحليل
# ============================================
def classify_student(grades):
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

def get_difficulties(grades):
    difficulties = []
    if grades[0] == 'ج':
        difficulties.append('المعيار 1')
    if grades[1] == 'ج':
        difficulties.append('المعيار 2')
    if grades[2] == 'ج':
        difficulties.append('المعيار 3')
    if grades[3] == 'ج':
        difficulties.append('المعيار 4')
    return difficulties

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
if st.button("🚀 تقسيم التلاميذ إلى أفواج وإنشاء التقرير", type="primary"):
    name_list = [n.strip() for n in names.strip().split('\n') if n.strip()]
    m1_list = [g.strip() for g in m1.strip().split('\n') if g.strip()]
    m2_list = [g.strip() for g in m2.strip().split('\n') if g.strip()]
    m3_list = [g.strip() for g in m3.strip().split('\n') if g.strip()]
    m4_list = [g.strip() for g in m4.strip().split('\n') if g.strip()]
    
    if not name_list:
        st.error("❌ الرجاء إدخال أسماء التلاميذ.")
        st.stop()
    
    if len(m1_list) != len(name_list) or len(m2_list) != len(name_list) or len(m3_list) != len(name_list) or len(m4_list) != len(name_list):
        st.error(f"❌ عدد التقديرات لا يتطابق مع عدد الأسماء ({len(name_list)}).")
        st.stop()
    
    data = []
    for i in range(len(name_list)):
        grades = [m1_list[i], m2_list[i], m3_list[i], m4_list[i]]
        if not all(g in ['م', 'أ', 'ج', 'د'] for g in grades):
            st.error(f"❌ تقديرات غير صالحة للتلميذ '{name_list[i]}'. استخدم فقط: م، أ، ج، د")
            st.stop()
        data.append({
            'الاسم': name_list[i],
            'المعيار 1': m1_list[i],
            'المعيار 2': m2_list[i],
            'المعيار 3': m3_list[i],
            'المعيار 4': m4_list[i],
        })
    
    df = pd.DataFrame(data)
    df['الصعوبات'] = df.apply(lambda row: get_difficulties([row['المعيار 1'], row['المعيار 2'], row['المعيار 3'], row['المعيار 4']]), axis=1)
    df['الفوج'] = df.apply(lambda row: classify_student([row['المعيار 1'], row['المعيار 2'], row['المعيار 3'], row['المعيار 4']]), axis=1)
    
    mentors = df[df['الفوج'] == 'مرشد (أ/ب)']
    students_need_support = df[df['الفوج'].isin(['فوج إنقاذ عاجل (د)', 'فوج دعم مكثف (ج)'])]
    
    groups = defaultdict(list)
    for _, student in students_need_support.iterrows():
        if student['الصعوبات']:
            key = ', '.join(student['الصعوبات'])
        else:
            key = 'صعوبة غير محددة'
        groups[key].append(student['الاسم'])
    
    st.balloons()
    st.success(f"✅ تم تقسيم {len(df)} تلميذاً إلى أفواج!")
    
    st.subheader("📈 إحصائيات الأفواج")
    col1, col2, col3 = st.columns(3)
    counts = df['الفوج'].value_counts()
    with col1:
        st.metric("🆘 فوج الإنقاذ", counts.get("فوج إنقاذ عاجل (د)", 0))
    with col2:
        st.metric("📚 فوج الدعم", counts.get("فوج دعم مكثف (ج)", 0))
    with col3:
        st.metric("🌟 المرشدون", counts.get("مرشد (أ/ب)", 0))
    
    with st.expander("📊 عرض جدول التلاميذ المصنفين", expanded=True):
        st.dataframe(df, use_container_width=True)
    
    st.subheader("📋 تقرير المعالجة البيداغوجية")
    template = memo_templates.get(matiere, memo_templates['رياضيات'])
    
    st.markdown(f"""
    <div style="background-color: #f0f4ff; padding: 15px; border-radius: 15px;">
        <b>المادة:</b> {matiere}<br>
        <b>المستوى:</b> {niveau}<br>
        <b>عدد التلاميذ:</b> {len(df)}<br>
        <b>عدد المرشدين:</b> {len(mentors)}
    </div>
    """, unsafe_allow_html=True)
    
    if not mentors.empty:
        st.info(f"👨‍🏫 المرشدون: {', '.join(mentors['الاسم'].tolist())}")
    
    st.divider()
    
    if groups:
        for i, (difficulty, students) in enumerate(groups.items(), 1):
            with st.expander(f"🔹 المجموعة {i} - الصعوبة: {difficulty}"):
                st.write(f"**التلاميذ:** {', '.join(students)}")
                st.write(f"**عددهم:** {len(students)}")
                st.write(f"**🛠️ الاستراتيجية:** {template['strategies']}")
                st.write(f"**📝 الأنشطة:** {template['activities']}")
    else:
        st.info("🎉 جميع التلاميذ مرشدون، لا توجد مجموعات معالجة.")
    
    csv = df.to_csv(index=False)
    st.download_button("📥 تحميل التقرير (Excel)", csv, f"تقرير_{matiere}_{niveau}.csv", "text/csv")
