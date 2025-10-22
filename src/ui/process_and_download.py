import streamlit as st
import pandas as pd
from data_processing import process_data, process_clustering


def render_results_summary():
    if st.session_state.get("df_display") is not None:
        if (
            st.session_state["warning_patients"] is not None
            and st.session_state["warning_patients"]
        ):
            st.warning(
                f"Samples for patients {st.session_state["warning_patients"]} have less than {st.session_state["param_k"]} samples. This can distort their score. "
            )
        params_used_column, overall_evaluation_column = st.columns([1, 1])
        with params_used_column:
            st.subheader("Used Parameters")
            st.json(st.session_state["params"])
        with overall_evaluation_column:
            if st.session_state.get("metrics") is not None:
                st.subheader("📈 Evaluation Metrics (over all samples)")
                st.table(
                    pd.DataFrame.from_dict(
                        st.session_state["metrics"], orient="index", columns=["Value"]
                    ).style.format({"Value": "{:.2f}"})
                )

        st.subheader("📋 Results Scoring")
        patient_status_summary = (
            st.session_state["df_display"]
            .groupby("Patient ID")["Sample Status"]
            .apply(lambda statuses: " ".join(statuses))
            .reset_index(name="Samples Status Summary")
        )
        patient_summary = patient_status_summary
        st.dataframe(patient_summary)

        st.dataframe(st.session_state["df_display"])

        download_df = st.session_state["df_display"].copy()
        download_df = download_df.drop(columns=["Patient Status", "Sample Status"])
        csv = download_df.to_csv(index=False)
        st.download_button(
            label="Download table as CSV",
            data=csv,
            file_name=f"results.csv",
            mime="text/csv",
        )
    else:
        st.info("No data processed yet. Please upload and/ or configure your data.")


def run_processing_button(parameters):
    if (
        st.session_state["df"] is not None
        and st.session_state["df_protein_ranking"] is not None
    ):
        if st.button("Run Processing"):
            df_display, metrics, warning_patients, used_params, error = process_data(
                st.session_state["df"],
                st.session_state["df_protein_ranking"],
                parameters,
            )
            if error:
                st.error(error)
            else:
                st.session_state["df_display"] = df_display
                st.session_state["metrics"] = metrics
                st.session_state["params"] = used_params
                st.session_state["refresh_data"] = False
                st.session_state["warning_patients"] = warning_patients
                st.success("Processing complete!")
    else:
        st.info(
            "⬆️ Please upload your protein data frame to enable parameter selection and processing."
        )


def run_clustering_button(parameters):
    """
    Button to trigger clustering computation. Stores everything in st.session_state.
    """
    if (
        st.session_state.get("df") is not None
        and st.session_state.get("df_protein_ranking") is not None
        and st.session_state.get("result_distances") is not None
    ):
        if st.button("Run Clustering"):
            result = st.session_state["result_distances"]
            df = st.session_state["df"]
            method = parameters["param_method"]
            n_neighbors = parameters["param_n_cluster_neighbours"]
            max_cluster_size = parameters["param_max_cluster_size"]

            process_clustering(
                result=result,
                df=df,
                method=method,
                n_neighbors=n_neighbors,
                max_cluster_size=max_cluster_size,
            )
    else:
        st.info("⬆️ Please upload your data and run processing before clustering.")


def render_clustering_results():
    if (
        "clustering_result" in st.session_state
        and st.session_state.get("clustering_result") is not None
    ):
        cached = st.session_state["clustering_result"]
        method = st.session_state["last_params"]["method"]

        # --- Figure ---
        st.subheader(f"Clustering Result ({method})")
        st.image(cached["fig_bytes"])
        st.download_button(
            label="Download Clustering as PNG",
            data=cached["fig_bytes"],
            file_name=f"{method}_clustering.png",
            mime="image/png",
        )

        # --- Transitive results ---
        if cached["transitive_results"]:
            st.subheader("Transitive Results")
            df_results = pd.DataFrame(
                list(cached["transitive_results"].items()), columns=["Metric", "Value"]
            )
            st.table(df_results)

        # --- Cluster assignment ---
        if cached["cluster_assignment"]:
            st.subheader("Cluster Assignment Preview")
            df_clusters = pd.DataFrame(
                list(cached["cluster_assignment"].items()),
                columns=["Sample", "Cluster"],
            )
            st.dataframe(df_clusters.head(20))

            # CSV download
            csv_buf = df_clusters.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Cluster Assignment as CSV",
                data=csv_buf,
                file_name=f"{method}_cluster_assignment.csv",
                mime="text/csv",
            )
        if cached["uncertain_nodes"]:
            st.subheader("Uncertain Samples Preview")
            df_uncertain_nodes = pd.DataFrame(
                list(cached["uncertain_nodes"]),
                columns=["Sample"],
            )
            st.dataframe(df_uncertain_nodes.head(20))

            # CSV download
            csv_buf = df_uncertain_nodes.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Uncertain Samples as CSV",
                data=csv_buf,
                file_name=f"{method}_uncertain_nodes.csv",
                mime="text/csv",
            )
        if cached["error_candidates"]:
            st.subheader("Error Candidates Preview")
            df_error_candidates = pd.DataFrame(
                list(cached["error_candidates"]),
                columns=["Sample"],
            )
            st.dataframe(df_error_candidates.head(20))

            # CSV download
            csv_buf = df_error_candidates.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Error Candidates as CSV",
                data=csv_buf,
                file_name=f"{method}_error_candidates.csv",
                mime="text/csv",
            )

    else:
        st.info("No clustering results yet. Click 'Run Clustering' to compute.")
