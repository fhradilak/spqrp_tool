import streamlit as st
from ui.upload import upload_and_preview_data
from ui.parameters import parameters_interface, clustering_interface
from ui.process_and_download import (
    render_results_summary,
    run_processing_button,
    run_clustering_button,
    render_clustering_results,
)
from utils import initialize_session_state


def main():
    initialize_session_state()
    st.title("SPQRP - Protein Sample Analysis")

    upload_and_preview_data()
    parameters = parameters_interface()
    run_processing_button(parameters)
    render_results_summary()

    parameters_clustering = clustering_interface()
    run_clustering_button(parameters_clustering)
    render_clustering_results()


if __name__ == "__main__":
    main()
