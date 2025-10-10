# DPS-Tool

[![DOI](https://zenodo.org/badge/1015940112.svg)](https://doi.org/10.5281/zenodo.16781971)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## An online service platform for disease perturbation scoring
DPS-Tool is a bioinformatics tool designed to quantify the **disease perturbation level** of samples by analyzing gene expression patterns between positive and negative samples, while providing intuitive visualizations to help researchers understand the perturbation patterns under disease conditions.

### Key Features

- **Multi-scenario assessment**  
  Evaluate perturbation levels across different stages, subtypes, or data sources of the same disease, and compare perturbations among distinct diseases.

- **Outlier detection**  
  Automatically flags outlier samples, reducing noise and boosting downstream-analysis reliability.

- **Key gene-pair signatures**  
  Identifies robust gene-pair features that effectively discriminate positive from negative samples, facilitating diagnosis and classification studies.

- **Gene-set & clinical integration**  
  Supports perturbation analysis of disease-related gene sets and correlates perturbation scores with clinical metadata.

- **Cross-platform robustness**  
  Designed to be resilient to batch effects, enabling seamless integration of data from heterogeneous platforms and sources.

![Figure](./images/Figure.png)

### Input Files

**1. Expression Matrix File**
- The gene expression matrix must have "Symbol" as the first column for Gene symbols, followed by columns representing expression levels for each sample (with sample names as column headers).
- There should be between 2 and 10 sample categories, with at least 10 negative and 10 positive samples. The matrix must contain more than 100 genes.
- Expression values can be normalized or unnormalized (e.g., Count, TPM, FPKM), and each gene should have a non-zero expression in at least 80% of the samples.
- The file must be in 'CSV' format.

**2. Sample Information Matrix File**
- The first column should be the sample name (with the column name "Sample"), the second column should be the sample category label (with the column name "Class"), and the third column should represent the rank corresponding to the sample category label, with negative to positive samples labeled as integers starting from 0 (column name: "Rank").
- The "Sample" column in the sample info matrix must match the expression matrix sample names exactly.
- Additional columns like gender and age can be added.
- Column names can only consist of letters, numbers, and underscores.
- Ensure no NA values in the matrix.
- The file must be in 'CSV' format.

### Parameters

**1. Negative Sample Class**  
Specify the category of negative samples used for analysis (the leftmost category).

**2. Positive Sample Class**  
Specify the category of positive samples used for analysis (the rightmost category).

**3. Reversal Ratio Threshold**  
The threshold used to extract reversal gene pairs. The value must be between 0.3 and 1, with a default of 0.5. A higher threshold results in fewer gene pairs.

**4. Deduplicate Gene Pairs**  
Some gene pairs satisfying the threshold may contain the same gene. If you choose to deduplicate, only the gene pair with the highest reversal ratio will be retained. The default is not to deduplicate.

**5. Gene Set File**  
Present in a single column, with the column name being the gene set name. The Gene symbol in this column must exist in the "Symbol" column of the expression matrix. The file must be in 'CSV' format.

**6. Sample Information Category**  
Specify the sample information to be used in the analysis. It must be assigned along with Sample Category and Data Type.

**7. Sample Category**  
Specify the sample category to be used in the analysis. It must be assigned along with Sample Information Category and Data Type.

**8. Data Type**  
Specify the data type of the sample information. It must be assigned along with Sample Information Category and Sample Category.

### Output

**1. Gene Pairs Table**
- **Gene1:** The first gene in a gene pair, which is expressed lower than the second gene in negative samples and higher in positive samples.
- **Gene2:** The first gene in a gene pair, which is expressed higher than the second gene in negative samples and lower in positive samples.
- **ReversalRatio:** The reversal ratio of a gene pair between negative and positive samples, defined as the absolute difference in the proportion of Gene1 < Gene2 between the two sample types.
- **ImportanceScore:** Gene pair importance score, where higher scores indicate a greater difference in the scores of the gene pair between the two sample groups. The maximum value is 1.  

The table is sorted in descending order based on the 'ImportanceScore' column.

**2. DP_Score Table**  
Add two new columns to the sample information matrix:  
- **DP_Score:** The disease perturbation score for the corresponding sample, ranging from 0 to 1.
- **Outlier:** "Yes" indicates an outlier sample.

**3. TOP10 Gene Pairs Bar Chart**  
The Y-axis represents gene pairs, and the X-axis represents their importance scores. Only the Top 10 gene pairs are displayed; if there are fewer than 10, only the available gene pairs will be shown.

**4. DP_Score Bar Chart**  
The Y-axis represents the disease perturbation score, and the X-axis represents samples. Different colors are used to distinguish the sample categories, showcasing the score differences among them.

**5. DP_Score Boxplot**  
The Y-axis represents the disease perturbation score, and the X-axis represents different sample categories, showcasing the differences in scores among them.

**6. DP_Score With Sample Information Plot**  
- When the sample information is 'Discrete', the relationship between the sample information and the disease perturbation score is displayed using box plots.
- When the sample information is 'Continuous', the correlation between the sample information and the disease perturbation score is shown using a scatter plot.

### 📁 Project Structure

| **Path** | **Description** |
|----------|------------------|
| `css/` | Global stylesheets for the entire site. |
| `dps_tool/` | Contains only `DPS-Tool.py`, the core Python script for the DPS-Tool. |
| `example/` | Sample input files together with their expected output. |
| `images/` | Static assets such as logos, screenshots, and example figures. |
| `js/` | Front-end JavaScript files for interactive functionality. |
| `README.md` | Project overview (this document). |
| `check_status.php` | Lightweight polling endpoint that returns real-time job progress. |
| `error.html` | Unified error page with common troubleshooting tips. |
| `example.html` | Quick demo page showing sample output. |
| `help.html` | Comprehensive help page explaining input formats and result interpretation. |
| `index.html` | Landing page featuring an interactive run portal and concise project overview. |
| `result.php` | Result-display API; returns interactive plots and download links for a given job ID. |
| `run.html` | Task-submission interface for uploading new datasets. |
| `upload.php` | Upload handler that performs file validation, renaming, and so on. |
| `waiting.php` | Waiting page; auto-redirects to results once ready. |

---
Paper describing this work has been received in *Frontiers of Computer Science* (FCS) special column “Code & Data”.  

**Cited as:** Changchun WU, Xueqin XIE, Ziru HUANG, Hao LIN, Jian HUANG. DPS-Tool: An online service platform for disease perturbation scoring. *Front. Comput. Sci.*, 2025, DOI: [10.1007/s11704-025-50841-y](https://doi.org/10.1007/s11704-025-50841-y)
