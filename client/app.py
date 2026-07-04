"""
Course Store — Streamlit client (UI only for now).

Not connected to the FastAPI server yet.

From project root: activate venv, then:
  cd client
  streamlit run app.py
"""

import streamlit as st

st.set_page_config(page_title="Course Store", page_icon="📚", layout="wide")

st.title("Course Store")
st.caption("Frontend placeholder — API connection coming next.")

st.info("This app does not talk to the backend yet. Start with `server/main.py` for the API.")

tab_users, tab_courses = st.tabs(["Users", "Courses"])

with tab_users:
    st.subheader("Users")
    st.write("List, create, update, and delete users will go here.")
    st.text_input("Name", disabled=True, placeholder="Coming soon")
    st.text_input("Email", disabled=True, placeholder="Coming soon")
    st.selectbox("Role", ["student", "instructor"], disabled=True)
    st.button("Save user", disabled=True)

with tab_courses:
    st.subheader("Courses")
    st.write("Browse and manage courses will go here.")
    st.text_input("Title", disabled=True, placeholder="Coming soon")
    st.text_area("Description", disabled=True, placeholder="Coming soon")
    st.number_input("Price", min_value=0.0, disabled=True)
    st.text_input("Instructor", disabled=True, placeholder="Coming soon")
    st.checkbox("Published", disabled=True)
    st.button("Save course", disabled=True)
