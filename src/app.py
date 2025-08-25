import streamlit as st
import os
import base64
from pathlib import Path
from matcher import match_cvs

# --- Set up CV storage folder ---
CV_FOLDER = Path.cwd() / "docs"
CV_FOLDER.mkdir(parents=True, exist_ok=True)

# --- Page title and styling ---
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
        }
    </style>
    <h1 style='text-align: center;'>CVision</h1>
    """,
    unsafe_allow_html=True
)

# --- Short description below the title ---
st.markdown(
    """
    <p style="color: gray; font-size: 16px; line-height: 1.5;">
    Upload your CVs and provide a job description, and CVision will analyze the CVs and return the most relevant ones for the given job, helping you quickly identify suitable candidates.
    </p>
    """,
    unsafe_allow_html=True
)

# --- Helper function to display PDF in Streamlit ---
def show_pdf(container, file_path, height=270, zoom=25):
    with open(file_path, "rb") as f:
        pdf_bytes = f.read()
    b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{b64_pdf}#zoom={zoom}" width="100%" height="{height}"></iframe>'
    container.markdown(pdf_display, unsafe_allow_html=True)

# --- Helper function to truncate long text ---
def truncate_text(text, max_chars=20):
    return text if len(text) <= max_chars else text[:max_chars-3] + "..."

# --- Initialize session state variables ---
if "matching" not in st.session_state:
    st.session_state.matching = False

if "cv_display_count" not in st.session_state:
    st.session_state.cv_display_count = 3

if "existing_cvs" not in st.session_state:
    st.session_state.existing_cvs = [f for f in os.listdir(CV_FOLDER) if f.endswith(".pdf")]

# --- File uploader for CVs ---
uploaded_files = st.file_uploader(
    "Choose one or more CV PDFs",
    type=["pdf"],
    accept_multiple_files=True,
    disabled=st.session_state.matching
)

# --- Save uploaded CVs to local folder ---
if uploaded_files:
    if "existing_cvs" not in st.session_state:
        st.session_state.existing_cvs = []
    for uploaded_file in uploaded_files:
        file_path = CV_FOLDER / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        if uploaded_file.name not in st.session_state.existing_cvs:
            st.session_state.existing_cvs.append(uploaded_file.name)

# --- Display already uploaded CVs with delete functionality ---
if st.session_state.existing_cvs:
    st.subheader("Uploaded CVs")
    cols_per_row = 3
    files_to_remove = []

    display_cvs = st.session_state.existing_cvs[:st.session_state.cv_display_count]

    for i in range(0, len(display_cvs), cols_per_row):
        row_items = display_cvs[i:i + cols_per_row]
        row_cols = st.columns(cols_per_row)
        for j, col in enumerate(row_cols):
            if j < len(row_items):
                cv_file = row_items[j]
                cv_path = CV_FOLDER / cv_file
                truncated_name = truncate_text(cv_file, max_chars=20)
                col.markdown(f"**{truncated_name}**", unsafe_allow_html=True)
                show_pdf(col, cv_path)

                with col:
                    button_cols = st.columns([1.5, 1, 1.5])
                    with button_cols[1]:
                        disabled = st.session_state.matching
                        if st.button("❌", key=f"del_{cv_file}", disabled=disabled):
                            os.remove(cv_path)
                            files_to_remove.append(cv_file)
            else:
                col.write("")

    # --- Remove deleted CVs from session state ---
    for f in files_to_remove:
        st.session_state.existing_cvs.remove(f)
        if "sorted_results" in st.session_state:
            st.session_state.sorted_results = [
                r for r in st.session_state.sorted_results if r.get("file") != f
            ]
            if st.session_state.cv_index >= len(st.session_state.sorted_results):
                st.session_state.cv_index = max(0, len(st.session_state.sorted_results) - 1)

    if files_to_remove:
        st.rerun()

    # --- Show more CVs button ---
    if st.session_state.cv_display_count < len(st.session_state.existing_cvs):
        col1, col2, col3 = st.columns([6, 2.3, 6])
        with col2:
            if st.button("Show more", disabled=st.session_state.matching):
                st.session_state.cv_display_count += 3
                st.rerun()

# --- Input for job description ---
job_role = st.text_area("Paste job description or role here:", height=300, disabled=st.session_state.matching)

# --- Match CVs button ---
cols = st.columns([6, 2.1, 6])
with cols[1]:
    run_clicked = st.button("Match CVs", key="run_rec", disabled=st.session_state.matching)

# --- Start matching process ---
if run_clicked:
    if not job_role:
        st.error("Please enter a job role.")
    elif not st.session_state.existing_cvs:
        st.error("No CVs uploaded yet.")
    else:
        st.session_state.matching = True
        st.session_state.sorted_results = []
        st.session_state.cv_index = 0
        st.rerun()

# --- Perform CV matching if matching is active ---
if st.session_state.matching:
    log_container = st.empty()
    results = []

    for msg in match_cvs(job_role):
        if isinstance(msg, dict) and "results" in msg:
            results = msg["results"]
        else:
            log_container.info(msg)

    st.session_state.sorted_results = results
    st.session_state.cv_index = 0
    st.session_state.matching = False
    st.rerun()

# --- Display recommended CVs ---
if st.session_state.get("sorted_results") and not st.session_state.matching:
    sorted_results = st.session_state.sorted_results
    cv_index = st.session_state.cv_index
    total_cvs = len(sorted_results)
    current_item = sorted_results[cv_index]
    cv_name = current_item.get("file", "Unknown")
    score = current_item.get("score", None)
    explanation = current_item.get("explanation", "")

    cv_path = CV_FOLDER / cv_name
    st.subheader("Recommended CVs")

    # --- Prepare PDF bytes for download link ---
    with open(cv_path, "rb") as f:
        pdf_bytes = f.read()
    b64_pdf = base64.b64encode(pdf_bytes).decode()

    # --- Display rank with clickable download link ---
    subheader_html = f"""
    <h5>
    <a href="data:application/pdf;base64,{b64_pdf}" download="{cv_name}" style="text-decoration: none; color: inherit;">
        Rank #{cv_index + 1} - {truncate_text(cv_name, max_chars=30)}
    </a>
    </h5>
    """
    st.markdown(subheader_html, unsafe_allow_html=True)

    # --- Display PDF content ---
    if cv_path.exists():
        show_pdf(st, cv_path, height=1000, zoom=85)
        st.markdown(f"<h5 style='color: inherit;'>Score : {score}</h5>", unsafe_allow_html=True)
        st.write(f"**Explanation :** {explanation}")

    # --- Navigation functions for CVs ---
    def next_cv():
        if st.session_state.cv_index < len(st.session_state.sorted_results) - 1:
            st.session_state.cv_index += 1

    def prev_cv():
        if st.session_state.cv_index > 0:
            st.session_state.cv_index -= 1

    # --- Navigation buttons for next/previous CV ---
    nav_col1, nav_col2, nav_col3 = st.columns([1, 6, 1])
    with nav_col1:
        st.button("⬅", on_click=prev_cv, disabled=cv_index == 0 or st.session_state.matching)
    with nav_col3:
        st.button("➡", on_click=next_cv, disabled=cv_index == len(st.session_state.sorted_results) - 1 or st.session_state.matching)
