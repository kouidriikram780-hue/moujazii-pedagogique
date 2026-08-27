import streamlit as st
import pandas as pd
from collections import defaultdict
from PIL import Image
import google.generativeai as genai
import json
import re

# ============================================
# إعداد Gemini API
# ============================================
# ضع مفتاح API الخاص بك هنا (أو استخدم st.secrets للنشر)
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# ============================================
# دالة تحليل الصورة باستخدام Gemini
# ============================================
def analyze_image_with_gemini(image):
    """إرسال الصورة إلى Gemini واستخراج البيانات"""
    prompt = """
    أنت مساعد ذكي متخصص في تحليل شبكات تقييم التلاميذ في الطور المتوسط.
    
    المطلوب:
    1. اقرأ الصورة التي تحتوي على شبكة تقييم.
    2. استخرج أسماء التلاميذ وتقديراتهم (م، أ، ج، د) من الشبكة.
    3. أعد البيانات على شكل JSON بهذا التنسيق:
    [
        {"name": "اسم التلميذ", "m1": "تقدير المعيار1", "m2": "تقدير المعيار2", "m3": "تقدير المعيار3", "m4": "تقدير المعيار4"},
        ...
    ]
    
    ملاحظات:
    - التقديرات هي: م (مكتسب)، أ (متحكم)، ج (مقترح الاكتساب)، د (غير مكتسب).
    - إذا كان هناك 4 معايير فقط، استخدمها. إذا كان هناك أكثر، اختر أول 4.
    - تأكد من صحة الأسماء والتقديرات.
    
    أعد JSON فقط، بدون أي نص إضافي.
    """
    
    response = model.generate_content([prompt, image])
    return response.text

# ============================================
# واجهة Streamlit
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
# رفع الصورة (الميزة الأساسية)
# ============================================
st.subheader("📸 رفع شبكة التقييم")
st.caption("صوّر الشبكة الورقية وارفعها")

uploaded_file = st.file_uploader("اختر صورة الشبكة", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    try:
        img = Image.open(uploaded_file)
        st.image(img, caption="الصورة المرفوعة", use_container_width=True)
        
        if st.button("🔍 تحليل الصورة وتقسيم التلاميذ", type="primary"):
            with st.spinner("جاري تحليل الصورة باستخدام الذكاء الاصطناعي..."):
                try:
                    # إرسال الصورة إلى Gemini
                    response_text = analyze_image_with_gemini(img)
                    
                    # استخراج JSON من الرد
                    json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        data = json.loads(json_str)
                    else:
                        # محاولة قراءة النص مباشرة
                        data = json.loads(response_text)
                    
                    if data:
                        # تحويل إلى DataFrame
                        df = pd.DataFrame(data)
                        
                        # التأكد من الأعمدة المطلوبة
                        required_cols = ['name', 'm1', 'm2', 'm3', 'm4']
                        if all(col in df.columns for col in required_cols):
                            df.columns = ['الاسم', 'م1', 'م2', 'م3', 'م4']
                            st.success(f"✅ تم استخراج بيانات {len(df)} تلميذاً بنجاح!")
                            st.dataframe(df, use_container_width=True)
                            
                            # حفظ في session_state
                            st.session_state['df_image'] = df
                        else:
                            st.error("❌ البيانات المستخرجة غير مكتملة. تأكد من وضوح الصورة.")
                    else:
                        st.error("❌ لم يتم العثور على بيانات. حاول تصوير الشبكة بوضوح.")
                        
                except Exception as e:
                    st.error(f"❌ حدث خطأ: {e}")
                    st.info("💡 تأكد من أن الصورة واضحة وأن الشبكة تحتوي على أسماء وتقديرات.")
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
# زر التحليل النهائي
# ============================================
if st.button("🚀 تقسيم التلاميذ إلى أفواج وإنشاء التقرير", type="secondary"):
    if 'df_image' in st.session_state and not st.session_state['df_image'].empty:
        df_analysis = st.session_state['df_image'].copy()
    else:
        st.error("❌ الرجاء رفع صورة وتحليلها أولاً.")
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
