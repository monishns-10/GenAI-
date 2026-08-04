import streamlit as st

# Give the app a title so it looks finished
st.title("Student Grade Calculator")

# Provide an input widget for the mark (handling the empty edge case by defaulting to None)
mark_input = st.number_input("Enter your mark (0-100):", min_value=None, max_value=None, value=None, step=1)

# Handle edge cases: empty field, out of bounds
if mark_input is None:
    st.info("Please enter a mark in the box above to see the matching grade.")
elif mark_input < 0 or mark_input > 100:
    st.error("Oops! Invalid input. Please enter a valid number between 0 and 100.")
else:
    # Determine the grade using the exact scale with inclusive boundaries
    if 90 <= mark_input <= 100:
        grade = "A"
    elif 80 <= mark_input <= 89:
        grade = "B"
    elif 70 <= mark_input <= 79:
        grade = "C"
    elif 60 <= mark_input <= 69:
        grade = "D"
    else:
        # Covers everything below 60
        grade = "E"
        
    # Display the entered mark and the resulting grade clearly on the page
    st.success(f"Mark: {mark_input} -> Grade: {grade}")
