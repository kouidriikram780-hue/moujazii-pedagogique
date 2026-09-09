import streamlit as st

st.set_page_config(page_title="اختبار", layout="centered")

st.title("✅ التطبيق يعمل!")
st.write("إذا رأيت هذه الرسالة، فالنشر ناجح.")

name = st.text_input("أدخل اسمك")
if name:
    st.success(f"مرحباً {name}!")
