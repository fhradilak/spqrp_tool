import streamlit as st
from collections import defaultdict


def initialize_session_state():
    default_state = {
        "df": None,
        "df_protein_ranking": None,
        "df_display": None,
        "metrics": None,
        "params": {},
        "refresh_data": False,
        "warning_patients": [],
        "param_k": 1,
        "param_n": 20,
        "number_display_neighbours": 4,
        "result_distances": None,
    }

    for key, default_value in default_state.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def reset_outputs():
    st.session_state["df_display"] = None
    st.session_state["formatted_metrics"] = None


def reset_clustering_outputs():
    st.session_state["clustering_result"] = None


def get_missing_columns(required_columns, df):
    missing_columns = []
    for column in required_columns:
        if column not in df.columns:
            missing_columns.append(column)
    return missing_columns


def sum_up_per_sample(pairs, d):
    for pair in pairs:
        p1, p2 = pair
        d[p1] = d.get(p1, 0) + 1
        d[p2] = d.get(p2, 0) + 1
    return d


def f1_color(f1):
    if f1 >= 0.8:
        return "🟢"
    elif f1 >= 0.5:
        return "🟡"
    else:
        return "🔴"


def format_neighbors_with_distances(row):
    neighbors = []
    # Assuming neighbors are in even columns (0,2,4...) and distances in odd columns (1,3,5...)
    for i in range(0, len(row), 2):
        neighbor = row[i]
        distance = row[i + 1]
        neighbors.append(f"{neighbor} ({distance})")
    return ", ".join(neighbors)


def calculate_f1_based_on_nn_neighbour(df, neighbors_df, sample_patient_mapping, n):

    tp_per_sample = dict()
    fp_per_sample = defaultdict(int)
    fn_per_sample = dict()

    # subset of dataframe with only nearest neighbors and not distances
    neighbor_cols = [col for col in neighbors_df.columns if col.startswith("Neighbor")]
    neighbors_df = neighbors_df[neighbor_cols]
    max_n = len(neighbors_df.columns)
    if n > max_n:
        st.warning(
            f"k (number nearest neighbours for scoring):{n} larger then number of retrieved nearest neighbors. Using the maximal number of neighbors available: {len(neighbors_df.columns)}."
        )
        n = len(neighbors_df.columns)
    neighbors = neighbors_df.iloc[:, :n]

    patient_to_samples = defaultdict(list)
    warning_patients = []

    for sample, patient in sample_patient_mapping.items():
        patient_to_samples[patient].append(sample)
    for patient, samples in patient_to_samples.items():
        if len(samples) <= n:
            warning_patients.append(patient)

    for sample in neighbors.index:
        # get nearest neighbors
        nn = neighbors.loc[sample]
        patient = sample_patient_mapping[sample]

        for n in nn:
            n_patient = sample_patient_mapping[n]
            if n_patient != patient:
                fp_per_sample[sample] = fp_per_sample.get(sample, 0) + 1
            elif n_patient == patient:
                tp_per_sample[sample] = tp_per_sample.get(sample, 0) + 1

        samples_per_patient = patient_to_samples[patient]

        fn_per_sample[sample] = (
            len(samples_per_patient) - 1 - tp_per_sample.get(sample, 0)
        )
    F1_per_sample, F1_per_patient = calculate_f1_scores(
        df, tp_per_sample, fp_per_sample, fn_per_sample, sample_patient_mapping
    )

    return F1_per_sample, F1_per_patient, warning_patients


def calculate_f1_scores(
    df, tp_per_sample, fp_per_sample, fn_per_sample, sample_patient_mapping
):
    tp_per_patient = defaultdict(int)
    fp_per_patient = defaultdict(int)
    fn_per_patient = defaultdict(int)
    F1_per_sample = dict()
    F1_per_patient = dict()
    for sample in df["Sample_ID"].unique():
        current_tp = tp_per_sample[sample] if sample in tp_per_sample else 0
        current_fp = fp_per_sample[sample] if sample in fp_per_sample else 0
        current_fn = fn_per_sample[sample] if sample in fn_per_sample else 0
        precision = (
            current_tp / (current_tp + current_fp)
            if (current_tp + current_fp) > 0
            else 0
        )
        sensitivity = (
            current_tp / (current_tp + current_fn)
            if (current_tp + current_fn) > 0
            else 0
        )
        F1 = (
            2 * ((precision * sensitivity) / (precision + sensitivity))
            if (precision + sensitivity) > 0
            else 0
        )

        patient = sample_patient_mapping[sample]
        tp_per_patient[patient] = tp_per_patient.get(patient, 0) + current_tp
        fp_per_patient[patient] = fp_per_patient.get(patient, 0) + current_fp
        fn_per_patient[patient] = fn_per_patient.get(patient, 0) + current_fn

        F1_per_sample[sample] = F1

    for patient in df["Patient_ID"].unique():
        current_tp = tp_per_patient[patient]
        current_fp = fp_per_patient[patient]
        current_fn = fn_per_patient[patient]
        precision = (
            current_tp / (current_tp + current_fp)
            if (current_tp + current_fp) > 0
            else 0
        )
        sensitivity = (
            current_tp / (current_tp + current_fn)
            if (current_tp + current_fn) > 0
            else 0
        )
        F1 = (
            2 * ((precision * sensitivity) / (precision + sensitivity))
            if (precision + sensitivity) > 0
            else 0
        )
        F1_per_patient[patient] = F1

    return F1_per_sample, F1_per_patient


def calculate_f1_based_on_cutoff(df, tp, fp, tn, fn, sample_patient_mapping):
    tp_per_sample = dict()
    fp_per_sample = dict()
    tn_per_sample = dict()
    fn_per_sample = dict()

    tp_per_sample = sum_up_per_sample(tp, tp_per_sample)
    fp_per_sample = sum_up_per_sample(fp, fp_per_sample)
    tn_per_sample = sum_up_per_sample(tn, tn_per_sample)
    fn_per_sample = sum_up_per_sample(fn, fn_per_sample)

    F1_per_sample, F1_per_patient = calculate_f1_scores(
        df, tp_per_sample, fp_per_sample, fn_per_sample, sample_patient_mapping
    )
    return F1_per_sample, F1_per_patient
