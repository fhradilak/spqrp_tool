import streamlit as st
from utils import reset_outputs, reset_clustering_outputs


def parameters_interface():
    if (
        st.session_state["df"] is not None
        and st.session_state["df_protein_ranking"] is not None
    ):
        st.subheader(
            " Step 3: Distance and Threshold Calculation: Set Parameters & Run"
        )
        left_col, spacer, right_col = st.columns([1, 0.1, 1])

        with spacer:
            st.markdown(
                """
                <style>
                .vertical-line {
                    border-left: 1px solid lightgray;
                    height: 400px; 
                    margin: auto;
                }
                </style>
                <div class="vertical-line"></div>
                """,
                unsafe_allow_html=True,
            )
        with right_col:
            st.markdown("###### Parameters for Score Calculation")

            if "param_evaluation_method" not in st.session_state:
                st.session_state["param_evaluation_method"] = "Threshold"
            param_evaluation_method = st.selectbox(
                "param_evaluation_method: Result Scoring Method",
                ["Nearest Neighbour", "Threshold"],
                key="param_evaluation_method",
                on_change=reset_outputs,
            )

            param_k = None
            if param_evaluation_method == "Nearest Neighbour":
                if "param_k" not in st.session_state:
                    st.session_state["param_k"] = 1
                param_k = st.number_input(
                    "param_k: k nearest neighbours to use in the scoring.",
                    min_value=1,
                    max_value=int(st.session_state["number_display_neighbours"]),
                    step=1,
                    key="param_k",
                    on_change=reset_outputs,
                )

            st.divider()
            number_display_neighbours = None
            if "number_display_neighbours" not in st.session_state:
                st.session_state["number_display_neighbours"] = min(
                    10, st.session_state["df"]["Sample_ID"].nunique() - 1
                )
            number_display_neighbours = st.number_input(
                "Number of nearest neighbours to retrieve and show in the table.",
                min_value=1,
                max_value=st.session_state["df"]["Sample_ID"].nunique() - 1,
                value=min(10, st.session_state["df"]["Sample_ID"].nunique() - 1),
                step=1,
                key="number_display_neighbours",
                on_change=reset_outputs,
            )

        with left_col:
            df_ranking = st.session_state.get("df_protein_ranking")

            if df_ranking is not None and len(df_ranking) > 0:
                default_value = min(20, len(df_ranking))
            else:
                # fallback if not available
                default_value = 1
            st.markdown("###### Parameters for the Distance Calculation")
            if "param_n" not in st.session_state:
                st.session_state["param_n"] = default_value

            param_n = st.number_input(
                "n :number of top n proteins from the ranking used for the distance calculation.",
                min_value=1,
                max_value=len(st.session_state["df_protein_ranking"]),
                value=default_value,
                step=1,
                key="param_n",
                on_change=reset_outputs,
            )

            if "param_metric" not in st.session_state:
                st.session_state["param_metric"] = "correlation"
            param_metric = st.selectbox(
                "metric: Metric for distance calculation.",
                ["correlation", "fractional", "euclidean"],
                index=["correlation", "fractional", "euclidean"].index(
                    st.session_state["param_metric"]
                ),
                key="param_metric",
                on_change=reset_outputs,
            )

            if "param_mode" not in st.session_state:
                st.session_state["param_mode"] = "optimize parameters"
            param_mode = st.selectbox(
                "Mode for calculation: A optimizing for given n, B return result for given parameters",
                ["optimize parameters", "use parameters"],
                index=["optimize parameters", "use parameters"].index(
                    st.session_state["param_mode"]
                ),
                key="param_mode",
                on_change=reset_outputs,
            )

            param_fractional_p = None
            if (
                st.session_state["param_metric"] == "fractional"
                and param_mode != "optimize parameters"
            ):
                if "param_fractional_p" not in st.session_state:
                    st.session_state["param_fractional_p"] = 0.01

                param_fractional_p = st.number_input(
                    "fractional_p: fractional value for fractional distance metric.",
                    min_value=0.01,
                    max_value=1.0,
                    step=0.01,
                    key="param_fractional_p",
                    on_change=reset_outputs,
                )
            else:
                st.session_state["param_fractional_p"] = 0.01

            param_percentile = None
            if param_mode == "use parameters":
                if "param_percentile" not in st.session_state:
                    st.session_state["param_percentile"] = 0.5

                param_percentile = st.number_input(
                    "percentile: Threshold as percentile for the distance distribution. Sample pairs distance below this threshold classified as belonging to the same patient else as not belonging.",
                    min_value=0.0,
                    max_value=100.0,
                    step=0.1,
                    key="param_percentile",
                    on_change=reset_outputs,
                )

            param_optimization_metric = "F1"
            if param_mode == "optimize parameters":
                if "param_optimization_metric" not in st.session_state:
                    st.session_state["param_optimization_metric"] = "F1"
                param_optimization_metric = st.selectbox(
                    "Metric for Distance calculation",
                    ["F1", "fp+fn", "fp", "fn", "precision", "sensitivity"],
                    index=["F1", "fp+fn", "fp", "fn", "precision", "sensitivity"].index(
                        st.session_state["param_optimization_metric"]
                    ),
                    key="param_optimization_metric",
                    on_change=reset_outputs,
                )
            else:
                st.session_state["param_optimization_metric"] = "F1"

        parameters = {
            "param_evaluation_method": param_evaluation_method,
            "param_k": param_k,
            "param_n": param_n,
            "param_metric": param_metric,
            "param_fractional_p": param_fractional_p,
            "param_mode": param_mode,
            "param_optimization_metric": param_optimization_metric,
            "param_percentile": param_percentile,
            "number_display_neighbours": number_display_neighbours,
        }
        return parameters
    return None


def clustering_interface():
    if st.session_state["result_distances"] is not None:
        st.subheader(" Step 4: Clustering: Set Parameters & Run")
        st.markdown("Clustering based on the distances calculated in Step 3")

        st.markdown("###### Parameters for Clustering Calculation")

        if "param_n_cluster_neighbours" not in st.session_state:
            st.session_state["param_n_cluster_neighbours"] = 1
        param_n_cluster_neighbours = st.number_input(
            "param_n_cluster_neighbours: k nearest neighbours to use in the clustering.",
            min_value=1,
            max_value=st.session_state["df"]["Sample_ID"].nunique() - 1,
            step=1,
            key="param_n_cluster_neighbours",
            on_change=reset_clustering_outputs,
        )

        if "param_max_cluster_size" not in st.session_state:
            st.session_state["param_max_cluster_size"] = 1
        param_max_cluster_size = st.number_input(
            "param_max_cluster_size: k nearest neighbours to use in the clustering.",
            min_value=1,
            max_value=int(st.session_state["df"]["Sample_ID"].nunique() - 1),
            step=1,
            key="param_max_cluster_size",
            on_change=reset_clustering_outputs,
        )

        if "param_method" not in st.session_state:
            st.session_state["param_method"] = "UMAP"
        param_method = st.selectbox(
            "Method for representing the clustering :",
            ["UMAP", "PCA", "MDS"],
            index=["UMAP", "PCA", "MDS"].index(st.session_state["param_method"]),
            key="param_method",
            on_change=reset_clustering_outputs,
        )

        parameters = {
            "param_n_cluster_neighbours": param_n_cluster_neighbours,
            "param_max_cluster_size": param_max_cluster_size,
            "param_method": param_method,
        }
        return parameters
    return None
