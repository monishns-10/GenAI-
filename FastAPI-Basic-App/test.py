import streamlit as st

st.title("My First Streamlit App")
st.write("Hello, World! Streamlit is working perfectly.")

name = st.text_input("Enter your name:")
st.write("Hello, ", name)

age = st.number_input("Enter your age:", min_value=0, max_value=120)
st.write("Your age is: ", age)


if st.button("Click me"):
   st.write("You clicked the button!")

