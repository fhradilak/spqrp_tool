import streamlit as st
import os
import pandas as pd

from constants import DEFAULT_RANKING_FILE


def upload_and_preview_data():
    # --- Protein Data Frame Upload Section ---
    st.subheader("Step 1: Upload Your Protein Data Frame")
    if "df" not in st.session_state:
        st.session_state["df"] = None

    uploaded_file = st.file_uploader(
        "Upload data frame CSV File (required)",
        type=["csv"],
        key="protein_df_uploader",
        help="You must upload your main protein data frame here.",
    )

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.session_state["df"] = df
        st.session_state["uploaded_file_name"] = uploaded_file.name
        st.success(f"Protein data frame uploaded: `{uploaded_file.name}`")
        st.session_state["formatted_metrics"] = None
    elif st.session_state["df"] is not None:
        st.info(
            f"Using previously uploaded data frame: `{st.session_state.get('uploaded_file_name', 'Unnamed file')}`"
        )
    else:
        st.warning("⚠️ Please upload your protein data frame CSV file to proceed.")

    if st.session_state["df"] is not None:
        st.write("Preview of uploaded protein intensity data:")
        st.dataframe(st.session_state["df"].head())

    # --- Protein Ranking Upload Section ---
    st.subheader("Step 2: Upload or Use Default Protein Ranking")
    current_dir = os.path.dirname(__file__)
    default_file_path = os.path.join(
        current_dir, "..", "..", "data", "ranked_classification_importance_cohort_a.csv"
    )
    uploaded_protein_ranking = st.file_uploader(
        "Upload protein ranking CSV File (optional)",
        type=["csv"],
        key="protein_ranking_uploader",
        help="Upload your protein ranking CSV file or use the default provided.",
        accept_multiple_files=False,
        disabled=False,
        label_visibility="visible",
    )

    if uploaded_protein_ranking is not None:
        df_protein_ranking = pd.read_csv(uploaded_protein_ranking)
        st.session_state["df_protein_ranking"] = df_protein_ranking
        st.session_state["ranking_file_name"] = uploaded_protein_ranking.name
        st.success(f"Protein ranking file uploaded: `{uploaded_protein_ranking.name}`")
    elif (
        "df_protein_ranking" in st.session_state
        and st.session_state["df_protein_ranking"] is not None
        and st.session_state["ranking_file_name"] != DEFAULT_RANKING_FILE
    ):
        name = st.session_state.get("ranking_file_name", "Default ranking file")
        st.info(f"Using previously loaded ranking file: `{name}`")
    elif os.path.exists(default_file_path):
        df_protein_ranking = pd.read_csv(default_file_path)
        st.session_state["ranking_file_name"] = DEFAULT_RANKING_FILE
        st.session_state["df_protein_ranking"] = df_protein_ranking
        st.info(
            f"Using default protein ranking file from data folder {DEFAULT_RANKING_FILE}."
        )
    else:
        df_protein_ranking = None
        st.warning("No protein ranking file found. Please upload one.")

    # --- Protein Ranking Preview ---
    if (
        "df_protein_ranking" in st.session_state
        and st.session_state["df_protein_ranking"] is not None
    ):
        st.caption("Preview of protein ranking (first 3 rows):")
        st.dataframe(
            st.session_state["df_protein_ranking"].head(3),
            height=100,
            use_container_width=True,
        )
    st.divider()
