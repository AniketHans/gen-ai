import streamlit as st

st.title("Subway Maker")

if "started" not in st.session_state:
    st.session_state.started = False

if st.button("Start"):
    st.session_state.started = True
    
if st.session_state.started:
    st.success("Make better choice for best subway")
    bun = st.radio("Pick your bun type", ["Maida", "Aata", "Sooji"], index=None)
    st.write(f"Bun choice: {bun}")
    
    st.write("Add Ons:")
    add_extras1 = st.checkbox("Single cheeze slice")
    add_extras2 = st.checkbox( "Double cheese slice")
    add_extras3 = st.checkbox("tomato")
    add_extras4 = st.checkbox("cucumber")
    
    combo = st.selectbox("Select the combos", ["Coke + fries", "Fries + Ice tea"], index=None)
    if combo:
        st.write(f"combo choice: {combo}")
    
    spicy = st.slider("Choose spicyness:", 1, 5, 3)
    st.write(f"Spicyness level: {spicy}")
    
    numberOfCombos = st.number_input("How many burgers:", min_value=1, max_value=20, step=1)    
    st.write(f"Number of burgers: {numberOfCombos}")
    
    name = st.text_input("Enter your name:")
    if name:
        st.write(f"Preparing order for {name}!!")
    dob = st.date_input("Select DOB for offers:")
    st.write(f"Your dob is {dob}")
    
