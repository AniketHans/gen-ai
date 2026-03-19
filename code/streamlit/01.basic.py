import streamlit as st

st.title("Hello Duniya")
st.subheader("Kya haal hain?")
st.text("Sab theek hai ji")
st.write("Kya piyoge?")
drink = st.selectbox("Pick a drink", ["Diet coke", "Coke Zero"," Thandai", "Daaru"], index=None)
if drink != None:
    st.write(f"User has chosen {drink}")
    st.success("Drink ready!!")