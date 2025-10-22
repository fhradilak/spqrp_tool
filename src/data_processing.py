import streamlit as st
from io import BytesIO
import matplotlib.pyplot as plt
from utils import (
    get_missing_columns,
    calculate_f1_based_on_cutoff,
    calculate_f1_based_on_nn_neighbour,
)
from utils import format_neighbors_with_distances, f1_color
import sys
import pandas as pd

sys.path.append("../")
from spqrp.core import (
    perform_distance_evaluation_on_ranked_proteins,
    optimize_parameters,
    cluster_samples_iteratively,
    plot_distances_neighbours_with_coloring_hue,
)


def process_clustering(result, df, method, n_neighbors, max_cluster_size):
    # Track current parameters
    current_params = {
        "method": method,
        "n_neighbors": n_neighbors,
        "max_cluster_size": max_cluster_size,
    }

    # Only recompute if clustering_result is missing or params changed
    if (
        "clustering_result" not in st.session_state
        or st.session_state.get("last_params") != current_params
    ):
        with st.status(
            "🔍 Clustering...",
            expanded=True,
        ) as status:
            g, coords_2d = cluster_samples_iteratively(
                result,
                df,
                method,
                n_neighbors=n_neighbors,
                max_component_size=max_cluster_size,
            )

            res = (
                plot_distances_neighbours_with_coloring_hue(
                    df=df,
                    G=g,
                    coords_2d=coords_2d,
                    method=method,
                    return_clusters=True,
                )
            )
            
            cluster_assignment = res["cluster_assignments"] 
            transitive_results = res["transitive_results"]

            fig = plt.gcf()
            buf = BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)
            fig_bytes = buf.getvalue()

            # Save everything into session_state
            st.session_state["clustering_result"] = {
                "fig_bytes": fig_bytes,
                "cluster_assignment": cluster_assignment,
                "transitive_results": transitive_results,
            }
            st.session_state["last_params"] = current_params
            status.update(label="✅ Clustering complete!", state="complete")


def process_data(df, prot_ranking, parameters):
    try:
        required_columns_df = ["Sample_ID", "Patient_ID", "Protein", "Intensity"]
        missing_columns_df = get_missing_columns(required_columns_df, df)

        required_columns_ranking = ["Protein", "Importance"]
        missing_columns_ranking = get_missing_columns(
            required_columns_ranking, prot_ranking
        )

        if missing_columns_df or missing_columns_ranking:
            delimiter = ", "
            missing_columns_text_df = delimiter.join(missing_columns_df)
            missing_columns_text_ranking = delimiter.join(missing_columns_ranking)
            return (
                None,
                None,
                None,
                None,
                (
                    f"{len(missing_columns_df)} missing required columns for the dataframe: {missing_columns_text_df}\n \n"
                    f"{len(missing_columns_ranking)} missing required columns for the protein_ranking: {missing_columns_text_ranking}"
                ),
            )
        n = parameters["param_n"]
        metric = parameters["param_metric"]
        percentile = parameters["param_percentile"]
        fractional_p = parameters["param_fractional_p"]
        param_evaluation_method = parameters["param_evaluation_method"]
        param_k = parameters["param_k"]
        mode = parameters["param_mode"]
        optimization_metric = parameters["param_optimization_metric"]
        number_neighbours_table = parameters["number_display_neighbours"]

        result = []
        if mode == "optimize parameters":
            with st.status(
                "🔍 Optimizing parameters... this may take a moment especially for fractional metric",
                expanded=True,
            ) as status:
                optimized_params = optimize_parameters(
                    df=df,
                    metric=metric,
                    range=range(n, n + 1, 1),
                    optimization_strategy=optimization_metric,
                    top_importance_df=prot_ranking,
                    quiet=True,
                )

                fractional_p = optimized_params["fractional_p"][0]
                percentile = optimized_params["percentile"][0]
                status.update(label="✅ Optimization complete!", state="complete")
        used_params = {
            "n": n,
            "metric": metric,
            "percentile": percentile,
            "fractional_p": fractional_p,
            "param_evaluation_method": param_evaluation_method,
            "param_k": param_k,
        }
        result = perform_distance_evaluation_on_ranked_proteins(
            df=df,
            top_importance_df=prot_ranking,
            n=n,
            p=percentile,
            metric=metric,
            fractional_p=fractional_p,
            number_display_neighbours=number_neighbours_table,
        )
        st.session_state["result_distances"] = result

        eval_metric = result.get("eval_metrics", {})
        metrics_order = [
            ("TP", "True Positives"),
            ("FP", "False Positives"),
            ("FN", "False Negatives"),
            ("TN", "True Negatives"),
            ("Accuracy", "Accuracy"),
            ("Precision", "Precision"),
            ("Sensitivity", "Sensitivity"),
            ("F1", "F1 Score"),
        ]

        raw_metrics = {
            display_name: eval_metric.get(key, 0) for key, display_name in metrics_order
        }

        nearest_neighbours = result["nearest_neighbours"]
        sample_patient_mapping = dict(zip(df["Sample_ID"], df["Patient_ID"]))
        warning_patients = None
        if param_evaluation_method == "Threshold":
            tp = result["eval_metrics"]["True_Positive_Pairs"]
            fp = result["eval_metrics"]["False_Positive_Pairs"]
            tn = result["eval_metrics"]["True_Negative_Pairs"]
            fn = result["eval_metrics"]["False_Negative_Pairs"]
            F1_per_sample, F1_per_patient = calculate_f1_based_on_cutoff(
                df=df,
                tp=tp,
                fp=fp,
                tn=tn,
                fn=fn,
                sample_patient_mapping=sample_patient_mapping,
            )
        elif param_evaluation_method == "Nearest Neighbour":
            F1_per_sample, F1_per_patient, warning_patients = (
                calculate_f1_based_on_nn_neighbour(
                    df=df,
                    neighbors_df=nearest_neighbours,
                    sample_patient_mapping=sample_patient_mapping,
                    n=param_k,
                )
            )

        rows = []
        for patient, f1_p in F1_per_patient.items():
            samples = [s for s, p in sample_patient_mapping.items() if p == patient]
            for sample in samples:
                f1_s = F1_per_sample[sample]

                neighbors = format_neighbors_with_distances(
                    nearest_neighbours.loc[sample]
                )
                rows.append(
                    {
                        "Patient ID": patient,
                        "Patient F1": f1_p,
                        "Patient Status": f1_color(f1_p),
                        "Sample ID": sample,
                        "Sample F1": f1_s,
                        "Sample Status": f1_color(f1_s),
                        "Nearest Neighbors": neighbors,
                    }
                )
        df_display = pd.DataFrame(rows)
        st.session_state["df_display"] = df_display
        return df_display, raw_metrics, warning_patients, used_params, None
    except Exception as e:
        return (
            None,
            None,
            None,
            None,
            f"❌ An unexpected error occurred during processing:\n{str(e)}",
        )
