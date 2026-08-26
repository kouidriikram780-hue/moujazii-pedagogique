import streamlit as st
import pandas as pd
from collections import defaultdict
from datetime import datetime
import re

# إعداد الصفحة
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

# إدخال البيانات
st.subheader("✏️ أدخل بيانات التلاميذ")

names = st.text_area("👨‍🎓 أسماء التلاميذ (كل اسم في سطر)")
grades_m1 = st.text_area("📊 تقديرات المعيار 1 (كل تقدير في سطر)")
grades_m2 = st.text_area("📊 تقديرات المعيار 2 (كل تقدير في سطر)")
grades_m3 = st.text_area("📊 تقديرات المعيار 3 (كل تقدير في سطر)")
grades_m4 = st.text_area("📊 تقديرات المعيار 4 (كل تقدير في سطر)")

# دوال التحليل
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

# قوالب المذكرات حسب المواد
memo_templates = {
    'رياضيات': {'title': 'مذكرة معالجة في الرياضيات', 'strategies': 'استراتيجية حل المشكلات + التعلم التعاوني', 'activities': 'تمارين تطبيقية، مسائل حياتية', 'tools': 'السبورة، الكراسات', 'evaluation': 'اختبار قصير'},
    'علوم': {'title': 'مذكرة معالجة في العلوم', 'strategies': 'التجريب + الاستقصاء العلمي', 'activities': 'تجارب عملية، مشاريع بحثية', 'tools': 'المختبر، المجهر', 'evaluation': 'تقرير تجربة'},
    'لغة عربية': {'title': 'مذكرة معالجة في اللغة العربية', 'strategies': 'التعلم باللعب + القراءة الموجهة', 'activities': 'قراءة نصوص، كتابة إبداعية', 'tools': 'الكتب، البطاقات', 'evaluation': 'إملاء، تعبير كتابي'},
    'لغة فرنسية': {'title': 'مذكرة معالجة في اللغة الفرنسية', 'strategies': 'التعلم بالمشاريع + المحاكاة', 'activities': 'حوارات، أغاني', 'tools': 'الصور، الفيديو', 'evaluation': 'اختبار شفوي'},
    'إنجليزية': {'title': 'مذكرة معالجة في اللغة الإنجليزية', 'strategies': 'Total Physical Response + Storytelling', 'activities': 'قصص مصورة، أغاني', 'tools': 'الفيديو، الصور', 'evaluation': 'محادثة قصيرة'},
    'تاريخ': {'title': 'مذكرة معالجة في التاريخ', 'strategies': 'التعلم بالخرائط + السرد القصصي', 'activities': 'خرائط ذهنية، خطوط زمنية', 'tools': 'الخرائط، الصور', 'evaluation': 'خرائط، اختبار مقالي'}
}

if st.button("🚀 تحليل البيانات وإنشاء التقرير", type="primary"):
    if not names or not grades_m1:
        st.error("❌ الرجاء إدخال أسماء التلاميذ وتقديرات المعيار 1 على الأقل.")
    else:
        # معالجة البيانات
        name_list = names.strip().split('\n')
        m1_list = grades_m1.strip().split('\n') if grades_m1 else []
        m2_list = grades_m2.strip().split('\n') if grades_m2 else []
        m3_list = grades_m3.strip().split('\n') if grades_m3 else []
        m4_list = grades_m4.strip().split('\n') if grades_m4 else []
        
        # التأكد من تطابق الأطوال
        max_len = len(name_list)
        m1_list = m1_list + [''] * (max_len - len(m1_list))
        m2_list = m2_list + [''] * (max_len - len(m2_list))
        m3_list = m3_list + [''] * (max_len - len(m3_list))
        m4_list = m4_list + [''] * (max_len - len(m4_list))
        
        # إنشاء DataFrame
        data = []
        for i in range(max_len):
            data.append([str(i+1).zfill(2), name_list[i], m1_list[i] if i < len(m1_list) else '', 
                         m2_list[i] if i < len(m2_list) else '', 
                         m3_list[i] if i < len(m3_list) else '', 
                         m4_list[i] if i < len(m4_list) else ''])
        
        df = pd.DataFrame(data, columns=['الرقم', 'الاسم', 'م1', 'م2', 'م3', 'م4'])
        
        # تطبيق دوال التحليل
        df['الصعوبات'] = df.apply(get_difficulties, axis=1)
        df['الفوج'] = df.apply(classify_student, axis=1)
        
        # فصل المرشدين عن التلاميذ المحتاجين
        mentors = df[df['الفوج'] == 'مرشد (أ/ب)']
        students_need_support = df[df['الفوج'] != 'مرشد (أ/ب)']
        
        # تجميع حسب الصعوبات
        groups = defaultdict(list)
        for _, student in students_need_support.iterrows():
            if student['الصعوبات']:
                key = ', '.join(student['الصعوبات'])
            else:
                key = 'صعوبة غير محددة'
            groups[key].append(student['الاسم'])
        
        # عرض النتائج
        st.success(f"✅ تم تحليل {len(df)} تلميذاً بنجاح")
        
        # عرض الجدول
        st.subheader("📊 جدول التلاميذ المصنفين")
        st.dataframe(df, use_container_width=True)
        
        # إحصائيات
        st.subheader("📈 إحصائيات الأفواج")
        col1, col2, col3, col4 = st.columns(4)
        counts = df['الفوج'].value_counts()
        with col1:
            st.metric("🆘 الإنقاذ", counts.get("فوج إنقاذ عاجل (د)", 0))
        with col2:
            st.metric("📚 الدعم", counts.get("فوج دعم مكثف (ج)", 0))
        with col3:
            st.metric("🌟 التعزيز", counts.get("مرشد (أ/ب)", 0))
        with col4:
            st.metric("📖 الأخرى", counts.get("غير مصنف", 0))
        
        # التقرير المفصل
        st.subheader("📋 تقرير المعالجة البيداغوجية")
        
        template = memo_templates.get(matiere, memo_templates['رياضيات'])
        
        st.markdown(f"**المادة:** {matiere}")
        st.markdown(f"**المستوى:** {niveau}")
        st.markdown(f"**عدد التلاميذ:** {len(df)}")
        st.markdown(f"**عدد المرشدين (أ/ب):** {len(mentors)}")
        if not mentors.empty:
            st.markdown(f"**المرشدون:** {', '.join(mentors['الاسم'].tolist())}")
        
        st.divider()
        
        # عرض المجموعات
        for i, (difficulty, students) in enumerate(groups.items(), 1):
            with st.expander(f"🔹 المجموعة {i} - الصعوبة: {difficulty}"):
                st.write(f"**التلاميذ:** {', '.join(students)}")
                st.write(f"**عددهم:** {len(students)}")
                
                # اقتراح علاج
                st.write(f"**🛠️ الاستراتيجية:** {template['strategies']}")
                st.write(f"**📝 الأنشطة:** {template['activities']}")
                st.write(f"**🧰 الوسائل:** {template['tools']}")
                st.write(f"**📊 التقييم:** {template['evaluation']}")
                
                if len(students) <= 5:
                    st.info("💡 مجموعة صغيرة → دعم فردي مكثف")
                else:
                    st.info("💡 مجموعة متوسطة → مجموعات فرعية داخل المجموعة")
        
        # رابط التحميل
        csv = df.to_csv(index=False)
        st.download_button("📥 تحميل التقرير (CSV)", csv, f"تقرير_{matiere}_{niveau}.csv", "text/csv")
