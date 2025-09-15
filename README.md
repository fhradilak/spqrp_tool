[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Local SPQRP TOOL
Sample Provenance Quality Resolver in Proteomics is a tool that provides quality assessment for plasma-MS-proteome studies. Recent advancements in MS technology and lab methods opened the door for large-scale proteomics and raised a growing concern regarding sample mix-ups. This tool creates a visual interface to help scientists evaluate whether their sample data is safe for further analysis. It uses functions from the python package (also usable in R) for [spqrp](https://github.com/fhradilak/spqrp/).
### Functionality
1. Upload plasma-MS-proteome dataset (& protein ranking)
2. Set parameters for distance calculations and threshold-based approach.
3. View visual quality assessment of the threshold-based approach.
4. Set parameters for clustering-based approach.
5. View clustering and performance assessment.
6. Download results.

- tested for Chrome on Windows

## First steps
### Running SPQRP Locally
1. Download/ clone the repository
2. Open a terminal where the repository is saved on your computer and [create a new environment from requirements.txt](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).
   - (Windows: create a new environemnt: ```py -m venv .venv```, activate it ```.venv\Scripts\activate```, install requirements: ```py -m pip install -r requirements.txt```)
4. To start ther app run
```{console}
streamlit run src/main.py
```
4. This opens up a Browser where you can interact with the app
  - alternatively use the URL from the terminal output
    <img src="https://github.com/user-attachments/assets/0159f11c-2c07-41d2-afe5-5104d88391f9" width="300"/>

### Using SPQRP
1. Protein DF: Upload your protein intensity dataframe with the [right format](#data_format)!
2. Protein Ranking: Default: use the provided protein ranking or Custom: upload your own ranking with the [right format](#data_format)!
3. Set Parameters
    - Parameters for the Distance Calculation
    - (Parameters for Threshold and Score Calculation)
    - (Number nearest neighbours)
5. Run
6. Results & Donwload as csv file
7. Set Paramters for Clustering
   - Parameters for the expected overall sample number per person
8. Run
9. Results & Donwload as csv file

<a id="data_format"></a>

## Parameters
1. ### Parameters for the Distance Calculation
   - **`n`**
      Number of top n proteins from the ranking used for the distance calculation.
   - **`metric`** Metric used for the distance calculation. (correlation, euclidean, fractional)
   - **`percentile`** Threshold as percentile for the distance distribution. Sample pairs with a distance below this threshold are classified as belonging else not belonging.
   - **`fractional`** (for `fractional`): fractional value for fractional distance metric.
   - **`mode for calculation`**
     - `optimize parameters`: optimize `percentile` (& `fractional`)
     - `use parameters`: use user input for `percentile` (& `fractional`)
    
2. ### Parameters for Score Calculation
   - **`param_evaluation_method`**: Result scoring Method for the F1 score and visual evaluation (🟢,🟡,🔴)
       - `Threshold`: Based on the percentile Threshold and the sample pairs classified as belonging or not belonging. Compare those to the label identity and calculate the F1 score for each sample based on per sample sensitivity and precision. Also calculate the patient level F1 score.
       - `Nearest Neighbour`: Classify per sample the **k** nearest neighbours as belonging and the others as not belonging. Compare those to the label identity and calculate the F1 score for each sample based on per sample sensitivity and precision. Also calculate the patient level F1 score.
   - **`param_k`**(for Nearest Neighbour): **k** nearest neighbours used for the scoring method.
3. ### Parameter for the number of nearest neighbours
   - Number of nearest neighbours to retrieve and show in the table. **`param_k`** can max. be as big as this value. If it is greater it will be reset to the max value.
4. ### Parameters for the Clustering
   - **`param_n_cluster_neighbours`**: The k nearest neighbours to use for the clustering. Normally = expected number of samples per patient for the cohort - 1 aka. param_max_cluster_size - 1. Therefore, for e.g. a cohort with 4 samples per person the default setting should be have param_n_cluster_neighbours = 3 and param_max_cluster_size = 4.
   - **`param_max_cluster_size`**: The maximum size a cluster should have and therefore normally = expected number of samples per patient for the cohort.
   - **`Method for representing the clustering`**: UMAP, PCA or MDS dimensionality reduction method to display the clustering in 2D.

## Results

1. Used Parameters
   - especially interesting when optimizing with `optimize parameters`
  
2. Evaluation Metrics
  Based on the Percentile and sample pairings classified as belonging or not metrics are calculated in comparison to the original patient IDs.
    - True Postive: Patient ID is the same & distance in belonging
    - False Positive: Patient ID not the same & distance in belonging
    - False Negatives: Patient ID is the same & distance in not belonging
    - True Negatives: Patient ID not the same & distance in not belonging
    - Accuracy
    - balanced Accuracy
    - Precision
    - Sensitivity
    - **`F1 Score`**: The harmonic mean of precision and sensitivity. It's calculated as: ```F1 = 2 * (precision * sensitivity) / (precision + sensitivity)```
  Example:
  <img src="https://github.com/user-attachments/assets/0b30f630-4dab-43a8-9c63-7df835ee408a" width="300"/>

3. Results Scoring
    - a. per Patient Summary
    - b. Results for all samples
   
   The result scoring color (🟢,🟡,🔴) is based on the F1 score.
   - f1 >= 0.8:'🟢'
   - f1 >= 0.5:'🟡'
   - f1 <0.5: '🔴'

4. Clustering Graph
  - The Graph from the SPQRP clustering-approach.
  - > "Clustering visualization with green nodes and connections denoting clusterings in accordance with the patient IDs, error candidates connected with samples with different patient IDs are shown in magenta with dashed lines. A Sample that is the only member of its cluster, even though the dataset contains at least one other sample with a matching patient ID, is marked as an uncertain sample with a pink circle. Singular samples that are the unique representative for their patient ID in the data and correctly have no connections in the plot are flagged with a blue square."
6. Clustering Performance Metrics
 Based on the CLustering and sample pairings classified as belonging or not metrics are calculated in comparison to the original patient IDs.
    - True Postive: Patient ID is the same & 2 samples in the same cluster
    - False Positive: Patient ID not the same & 2 samples in the same cluster
    - False Negatives: Patient ID is the same & 2 samples not in the same cluster
    - True Negatives: Patient ID not the same & 2 samples not in the same cluster
    - Accuracy
    - balanced Accuracy
    - Precision
    - Sensitivity
    - **`F1 Score`**: The harmonic mean of precision and sensitivity. It's calculated as: ```F1 = 2 * (precision * sensitivity) / (precision + sensitivity)```
   - precision, sensitivity, f1 score, and accuracy calculated based on the pairwise clustering relationship and the labeled Patient IDs.
   - ari and nmi calculated for the overall clustering.
7. Clustering Assignment
   - List of Samples with their corresponding Cluster ID. If Sample1 and Sample2 are assigned to the same cluster their Cluster ID will be equal.
## 🗃️ Input Data Format
1. **Cohort data**: protein intensities per sample
2. Protein importance ranking list (optional - can use default list)

#### Naming of the Proteins:
```UniProt Entry-Id + "_"+ Gene Name```
**Example: P08519_LPA**
  - <img src="https://github.com/user-attachments/assets/25de5a83-7e05-4379-9087-5656965cc3e4" width="300"/>

#### Cohort data
The following columns have to be present in the input df.

| Column Name | Description                        |
|-------------|------------------------------------|
| `Sample_ID` | Unique identifier for the sample   |
| `Patient_ID`| Identifier for the patient         |
| `Protein`   | Name or identifier of the protein  |
| `Intensity` | Measured intensity (numeric value) |
#### Protein ranking
| Column Name | Description                        |
|-------------|------------------------------------|
| `Protein`   | Name or identifier of the protein  |
| `Importance`| Importance/ Ranking of the protein |
