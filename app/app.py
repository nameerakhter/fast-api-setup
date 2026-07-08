# =============================================================================
# STREAMLIT UI (the "frontend")
# =============================================================================
#
# This is the user-facing app. It does NOT touch MongoDB.
# Every action calls app/api.py, which sends HTTP to FastAPI (server.py).
#
# Design choices (same as the React refresher App.jsx):
#   - Load courses  → GET only, manual button (not on page load)
#   - Add course    → POST only, does NOT auto-refetch the list
#   - Delete        → DELETE only, removes row from local state (no GET refetch)
#
# Run with: streamlit run app/app.py
# Open: http://localhost:8501
#
# You need BOTH terminals running:
#   1. uvicorn server:app --reload   (API on :8000)
#   2. streamlit run app/app.py      (UI on :8501)
# =============================================================================

import streamlit as st

from app import api

st.set_page_config(page_title="Course Store", page_icon="📚", layout="wide")

# Light-mode styling (also see .streamlit/config.toml)
st.markdown(
    """
    <style>
        .stApp { background-color: #f8fafc; color: #0f172a; }
        .block-container { padding-top: 2rem; max-width: 960px; }
        div[data-testid="stMetricValue"] { color: #0f172a; }
        .status-box {
            background: #e2e8f0;
            border-left: 4px solid #2563eb;
            padding: 0.75rem 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# session_state = data that survives when Streamlit re-runs the script on each click
# (similar to useState in React)
if "courses" not in st.session_state:
    st.session_state.courses = []
if "status" not in st.session_state:
    st.session_state.status = "Ready — no requests yet."

st.title("Course Store")
st.caption("Streamlit UI → HTTP → FastAPI → PyMongo → MongoDB")

st.markdown(f'<div class="status-box"><strong>Status:</strong> {st.session_state.status}</div>', unsafe_allow_html=True)

# --- load courses (GET, manual) ---
col_load, col_count = st.columns([1, 3])
with col_load:
    if st.button("Load courses", type="primary"):
        try:
            st.session_state.courses = api.get_courses()
            st.session_state.status = f"GET /courses — loaded {len(st.session_state.courses)} course(s)."
        except Exception as exc:
            st.session_state.status = f"GET /courses failed: {exc}"

with col_count:
    st.metric("Courses in view", len(st.session_state.courses))

st.divider()
st.subheader("Add course")

# --- add course (POST, no auto-refetch) ---
with st.form("add_course_form", clear_on_submit=True):
    title = st.text_input("Title", placeholder="Intro to Python")
    description = st.text_area("Description", placeholder="A beginner-friendly course.")
    instructor_email = st.text_input("Instructor email", placeholder="instructor@example.com")
    price = st.number_input("Price", min_value=0.0, step=1.0, value=0.0)
    submitted = st.form_submit_button("Add course")

    if submitted:
        if not title.strip():
            st.session_state.status = "POST /courses skipped — title is required."
        else:
            try:
                created = api.create_course(
                    title=title.strip(),
                    description=description.strip(),
                    instructor_email=instructor_email.strip(),
                    price=price,
                )
                st.session_state.status = (
                    f"POST /courses — created \"{created['title']}\" (id: {created['id']}). "
                    "List not refetched."
                )
            except Exception as exc:
                st.session_state.status = f"POST /courses failed: {exc}"

st.divider()
st.subheader("Courses")

# --- course list + delete (DELETE, update local state only) ---
if not st.session_state.courses:
    st.info("No courses loaded. Click **Load courses** to fetch from the API.")
else:
    for course in st.session_state.courses:
        with st.container(border=True):
            left, right = st.columns([4, 1])
            with left:
                st.markdown(f"**{course['title']}**")
                if course.get("description"):
                    st.write(course["description"])
                st.caption(
                    f"Instructor: {course.get('instructor_email') or '—'} · "
                    f"Price: ${course.get('price', 0):.2f}"
                )
                st.caption(f"ID: `{course['id']}`")
            with right:
                if st.button("Delete", key=f"delete-{course['id']}"):
                    try:
                        api.delete_course(course["id"])
                        # Remove from local list — we do NOT call get_courses() again
                        st.session_state.courses = [
                            item for item in st.session_state.courses if item["id"] != course["id"]
                        ]
                        st.session_state.status = (
                            f"DELETE /courses/{course['id']} — removed locally (no GET refetch)."
                        )
                    except Exception as exc:
                        st.session_state.status = f"DELETE /courses/{course['id']} failed: {exc}"
