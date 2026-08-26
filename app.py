import streamlit as st
import pandas as pd
from collections import defaultdict
from datetime import datetime

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

st.subheader("📸 رفع شبكة التقييم")
uploaded_file = st.file_uploader("اختر صورة الشبكة", type=["jpg", "png", "jpeg"])

st.markdown("---")
st.subheader("✏️ أو أدخل البيانات يدوياً")

names = st.text_area("أسماء التلاميذ (كل اسم في سطر)")
grades_m1 = st.text_area("تقديرات المعيار 1 (كل تقدير في سطر)")
grades_m2 = st.text_area("تقديرات المعيار 2 (كل تقدير في سطر)")
grades_m3 = st.text_area("تقديرات المعيار 3 (كل تقدير في سطر)")
grades_m4 = st.text_area("تقديرات المعيار 4 (كل تقدير في سطر)")

if st.button("🚀 تحليل البيانات وإنشاء التقرير", type="primary"):
    st.success("✅ جاري تحليل البيانات... (سيتم إضافة المنطق الكامل قريباً)")
    st.info("📌 هذا الإصدار التجريبي يعرض الواجهة فقط. سيتم إضافة منطق التحليل في التحديث القادم.")
