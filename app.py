import streamlit as st
import pandas as pd
from collections import defaultdict

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
# اختيار المادة والمستوى
# ============================================
col1, col2 = st.columns(2)
with col1:
    niveau = st.selectbox("📌 المستوى", ["1 متوسط", "2 متوسط", "3 متوسط", "4 متوسط"])
with col2:
    matiere = st.selectbox("📖 المادة", ["رياضيات", "علوم", "لغة عربية", "لغة فرنسية", "إنجليزية", "تاريخ وجغرافيا"])

st.divider()

# ============================================
# الجدول التفاعلي للإدخال
# ============================================
st.subheader("✏️ أدخل بيانات التلاميذ في الجدول")
st.caption("املأ الأسماء واختر التقديرات (م، أ، ج، د) من القائمة المنسدلة")

# إعداد بيانات افتراضية (5 صفوف فارغة كنموذج)
default_data = {
    "الاسم": ["", "", "", "", ""],
    "المعيار 1": ["", "", "", "", ""],
    "المعيار 2": ["", "", "", "", ""],
    "المعيار 3": ["", "", "", "", ""],
    "المعيار 4": ["", "", "", "", ""],
}
df_default = pd.DataFrame(default_data)

# عرض المحرر مع خيارات منسدلة للتقديرات
edited_df = st.data_editor(
    df_default,
    column_config={
        "الاسم": st.column_config.TextColumn("👨‍🎓 الاسم", required=True),
        "المعيار 1": st.column_config.SelectboxColumn(
            "📊 المعيار 1",
            options=["", "م", "أ", "ج", "د"],
            required=False,
        ),
        "المعيار 2": st.column_config.SelectboxColumn(
            "📊 المعيار 2",
            options=["", "م", "أ", "ج", "د"],
            required=False,
        ),
        "المعيار 3": st.column_config.SelectboxColumn(
            "📊 المعيار 3",
            options=["", "م", "أ", "ج", "د"],
            required=False,
        ),
        "المعيار 4": st.column_config.SelectboxColumn(
            "📊 المعيار 4",
            options=["", "م", "أ", "ج", "د"],
            required=False,
        ),
    },
    num_rows="dynamic",  # يسمح بإضافة أو حذف صفوف
    use_container_width=True,
)

st.caption("💡 يمكنك إضافة صفوف جديدة بالضغط على '+' في أسفل الجدول.")

st.divider()

# ============================================
# دوال التحليل
# ============================================
def get_difficulties(row):
    difficulties = []
    if row['المعيار 1'] == 'ج':
        difficulties.append('المعيار 1')
    if row['المعيار 2'] == 'ج':
        difficulties.append('المعيار 2')
    if row['المعيار 3'] == 'ج':
        difficulties.append('المعيار 3')
    if row['المعيار 4'] == 'ج':
        difficulties.append('المعيار 4')
    return difficulties

def classify_student(row):
    grades = [row['المعيار 1'], row['المعيار 2'], row['المعيار 3'], row['المعيار 4']]
    # تجاهل التلاميذ الذين لم يتم إدخال بياناتهم
    if not any(grades) or not row['الاسم']:
        return 'غير مكتمل'
    
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

# قوالب المذكرات حسب المواد
memo_templates = {
    'رياضيات': {'strategies': 'حل المشكلات + التعلم التعاوني', 'activities': 'تمارين تطبيقية، مسائل حياتية'},
    'علوم': {'strategies': 'التجريب + الاستقصاء العلمي', 'activities': 'تجارب عملية، مشاريع بحثية'},
    'لغة عربية': {'strategies': 'التعلم باللعب + القراءة الموجهة', 'activities': 'قراءة نصوص، كتابة إبداعية'},
    'لغة فرنسية': {'strategies': 'التعلم بالمشاريع + المحاكاة', 'activities': 'حوارات، أغاني'},
    'إنجليزية': {'strategies': 'Total Physical Response + Storytelling', 'activities': 'قصص مصورة، أغاني'},
    'تاريخ': {'strategies': 'التعلم بالخرائط + السرد القصصي', 'activities': 'خرائط ذهنية، خطوط زمنية'}
}

# ============================================
# زر التحليل والتقسيم
# ============================================
if st.button("🚀 تقسيم التلاميذ إلى أفواج وإنشاء التقرير", type="primary"):
    # تصفية الصفوف الفارغة (التي ليس فيها اسم)
    df_filtered = edited_df[edited_df['الاسم'].str.strip() != ""].copy()
    
    if df_filtered.empty:
        st.error("❌ الرجاء إدخال أسماء التلاميذ في الجدول.")
        st.stop()
    
    # تطبيق التحليل
    df_filtered['الصعوبات'] = df_filtered.apply(get_difficulties, axis=1)
    df_filtered['الفوج'] = df_filtered.apply(classify_student, axis=1)
    
    # فصل المرشدين عن التلاميذ المحتاجين
    mentors = df_filtered[df_filtered['الفوج'] == 'مرشد (أ/ب)']
    students_need_support = df_filtered[df_filtered['الفوج'].isin(['فوج إنقاذ عاجل (د)', 'فوج دعم مكثف (ج)'])]
    
    # تجميع حسب الصعوبات
    groups = defaultdict(list)
    for _, student in students_need_support.iterrows():
        if student['الصعوبات']:
            key = ', '.join(student['الصعوبات'])
        else:
            key = 'صعوبة غير محددة'
        groups[key].append(student['الاسم'])
    
    st.balloons()
    st.success(f"✅ تم تقسيم {len(df_filtered)} تلميذاً إلى أفواج!")
    
    # إحصائيات الأفواج
    st.subheader("📈 إحصائيات الأفواج")
    col1, col2, col3 = st.columns(3)
    counts = df_filtered['الفوج'].value_counts()
    with col1:
        st.metric("🆘 فوج الإنقاذ", counts.get("فوج إنقاذ عاجل (د)", 0))
    with col2:
        st.metric("📚 فوج الدعم", counts.get("فوج دعم مكثف (ج)", 0))
    with col3:
        st.metric("🌟 المرشدون", counts.get("مرشد (أ/ب)", 0))
    
    # عرض الجدول مع التصنيف
    with st.expander("📊 عرض جدول التلاميذ المصنفين", expanded=True):
        st.dataframe(df_filtered, use_container_width=True)
    
    # التقرير النهائي
    st.subheader("📋 تقرير المعالجة البيداغوجية")
    template = memo_templates.get(matiere, memo_templates['رياضيات'])
    
    st.markdown(f"""
    <div style="background-color: #f0f4ff; padding: 15px; border-radius: 15px;">
        <b>المادة:</b> {matiere}<br>
        <b>المستوى:</b> {niveau}<br>
        <b>عدد التلاميذ:</b> {len(df_filtered)}<br>
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
        st.info("🎉 جميع التلاميذ في مستوى جيد (مرشدون)، لا توجد مجموعات معالجة مطلوبة.")
    
    # زر تحميل التقرير
    csv = df_filtered.to_csv(index=False)
    st.download_button(
        label="📥 تحميل التقرير (Excel)",
        data=csv,
        file_name=f"تقرير_{matiere}_{niveau}.csv",
        mime="text/csv"
)
