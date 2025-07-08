import argparse
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.stats import spearmanr

mpl.rcParams['pdf.fonttype'] = 42 
plt.rcParams['font.family'] = 'Arial' 
plt.rcParams['font.size'] = 12
plt.rcParams['text.color'] = 'black'

# ==============================
#       Reverse_gene_pairs
# ==============================
def Reverse_gene_pairs(expr_df, negative_samples_num, positive_samples_num, reversal_ratio_threshold, remove_duplicate_gene_pairs, gene_set_input):
    """
    Reverse_gene_pairs: Function to extract reversed gene pairs
    
    Input Parameters:
    expr_df: An expression matrix sorted by Symbol, negative samples, and positive samples
    negative_samples_num: Number of negative samples
    positive_samples_num: Number of positive samples
    reversal_ratio_threshold: Reversal proportion threshold
    remove_duplicate_gene_pairs: Remove duplicates or not
    gene_set_input: Path to gene set data
    
    Output:
    reverse_gene_pairs_reslut: Includes the columns: 'Gene1', 'Gene2', and 'ReversalRatio' (reversal ratio)
    """
    expr_df = expr_df.set_index(expr_df.columns[0])  # Set the first column as the index
    
    def get_reverse_gene_pairs(row):
        # Get the index of the current row
        current_index = row.name
    
        # Get all rows below the current row
        below_matrix = expr_df.loc[current_index:].iloc[1:]
    
        # Calculate the difference between the current row and all rows in below_matrix
        diff = row - below_matrix

        # Compute the proportion difference
        neg_columns = diff.iloc[:, :negative_samples_num]
        pos_columns = diff.iloc[:, negative_samples_num:]
        neg_value = neg_columns < 0  
        pos_value = pos_columns < 0 
        neg_counts = neg_value.sum(axis=1) 
        pos_counts = pos_value.sum(axis=1) 
        neg_ratios = neg_counts / negative_samples_num
        pos_ratios = pos_counts / positive_samples_num
        diff_ratios = neg_ratios - pos_ratios

        # Generate the gene pair dataframe
        diff_ratios_df = pd.DataFrame({
            'Gene1': row.name,              
            'Gene2': diff.index.values     
        })
        diff_ratios = diff_ratios.reset_index(drop=True)
        diff_ratios_df['ReversalRatio'] = diff_ratios

        # Swap genes in rows with negative values to ensure the smaller gene is listed first
        neg_rows = diff_ratios_df['ReversalRatio'] < 0
        diff_ratios_df.loc[neg_rows, ['Gene1', 'Gene2']] = diff_ratios_df.loc[neg_rows, ['Gene2', 'Gene1']].values
        diff_ratios_df['ReversalRatio'] = diff_ratios_df['ReversalRatio'].abs()

        # Filter by threshold
        diff_ratios_df = diff_ratios_df[diff_ratios_df['ReversalRatio'] > reversal_ratio_threshold]
        
        return diff_ratios_df

    result_list = expr_df.apply(get_reverse_gene_pairs, axis=1)
    
    # Merge the list into the final result dataframe
    reverse_gene_pairs_reslut = pd.concat(result_list.tolist(), ignore_index=True)
    reverse_gene_pairs_reslut = reverse_gene_pairs_reslut.sort_values(by='ReversalRatio', ascending=False)

    # Check the number of gene pairs
    if reverse_gene_pairs_reslut.shape[0] < 100:
        raise ValueError("The reversal ratio threshold is too high or there is no difference between the two sample groups. Please adjust the threshold accordingly!")

    # Gene set processing
    if gene_set_input is not None:
        gene_set_df = pd.read_csv(gene_set_input, sep=',')
        
        # Check whether the gene set contains only one column
        if gene_set_df.shape[1] != 1:
            raise ValueError("Incorrect gene set data format!")
        
        # Check whether all gene symbols are present in the 'Symbol' column of the expression dataframe
        gene_list = gene_set_df.iloc[:, 0].dropna().astype(str).tolist()
        missing_genes = [g for g in gene_list if g not in expr_df.index.tolist()]
        if missing_genes:
            raise ValueError("Some genes in the gene set do not exist in the expression dataframe!")
        
        # Select reversed gene pairs where at least one gene is present in the provided gene set
        reverse_gene_pairs_reslut = reverse_gene_pairs_reslut[
            reverse_gene_pairs_reslut['Gene1'].isin(gene_list) | reverse_gene_pairs_reslut['Gene2'].isin(gene_list)
        ]

        # Check if there are any gene pairs after filtering
        if reverse_gene_pairs_reslut.shape[0] < 1:
            raise ValueError("No reversed gene pairs were obtained, indicating that this gene set shows no difference between the two sample groups!")
       
    # Define function for removing duplicate gene pairs
    def duplicate_removal(matrix):
        seen_genes = set()
        result_matrix = []
    
        for idx, row in matrix.iterrows():
            gene1, gene2 = row.iloc[:2]
    
            if gene1 not in seen_genes and gene2 not in seen_genes:
                result_matrix.append(row)
                seen_genes.update([gene1, gene2])
    
        return pd.DataFrame(result_matrix, columns=matrix.columns)

    # Remove duplicate gene pairs
    if remove_duplicate_gene_pairs:
        reverse_gene_pairs_reslut = duplicate_removal(reverse_gene_pairs_reslut)
        
    # Return the result
    return reverse_gene_pairs_reslut

# ==============================
#            DP_Score
# ==============================
def DP_Score(reversal_gene_pairs, expression_matrix, sample_info_matrix):
    """
    DP_Score: Function to calculate disease perturbation score
    
    Input Parameters:
    reversal_gene_pairs: Data of reversed gene pairs
    expression_matrix: Gene expression matrix (including the first column as symbol, others as sample expression levels)
    sample_info_matrix: Sample information matrix
    
    Output: 
    Disease_perturbation_scoring: A data frame that adds two columns [DP_Score, Outlier] based on the sample information matrix
    diff_matrix: Used for calculating the importance of gene pairs
    """
    
    # 1. Extract corresponding data from the expression matrix based on Gene1 and Gene2
    # Gene1 is usually lowly expressed in negative samples, Gene2 is usually highly expressed in negative samples
    small_gene_matrix = expression_matrix.loc[reversal_gene_pairs['Gene1']].reset_index(drop=True)
    big_gene_matrix = expression_matrix.loc[reversal_gene_pairs['Gene2']].reset_index(drop=True)

    # 2. Calculate the difference matrix
    diff_matrix = small_gene_matrix - big_gene_matrix
 
    # 3. For each column (sample), count how many values are greater than or equal to 0, then divide by the logarithm of the number of gene pairs as the score for each sample
    scores = (diff_matrix >= 0).sum(axis=0)
    gene_pairs_num = reversal_gene_pairs.shape[0]
    normalized_scores = scores / gene_pairs_num
    
    # 4. Create the result data frame
    scores_result = pd.DataFrame({
        'Sample': normalized_scores.index,
        'DP_Score': normalized_scores.values
    })
    result_matrix = pd.merge(sample_info_matrix, scores_result, on='Sample', how='inner')

    # 5. Retrieve the 'Outlier' column
    def mark_outliers(sample_info_matrix):
        # Get the unique values of the 'Rank' column and their corresponding counts
        rank_counts = sample_info_matrix['Rank'].value_counts().sort_index()
    
        # Initialize the 'Outlier' column with the default value 'No'
        sample_info_matrix['Outlier'] = 'No'
     
        # Iterate over the ranks in order
        start_idx = 0
        for rank_value, count in rank_counts.items():
            # Get the index range for the current rank segment
            end_idx = start_idx + count
            subset = sample_info_matrix.iloc[start_idx:end_idx]
    
            # Find rows where the Rank value is not equal to the current rank_value and mark them as "Yes"
            sample_info_matrix.loc[subset.index[subset['Rank'] != rank_value], 'Outlier'] = 'Yes'
            
            # Update the starting index
            start_idx = end_idx

        return sample_info_matrix
        
    # Sort by DP_Score
    result_matrix_sorted = result_matrix.sort_values(by='DP_Score').reset_index(drop=True)
    
    # Mark outliers
    Disease_perturbation_scoring = mark_outliers(result_matrix_sorted)

    return Disease_perturbation_scoring, diff_matrix
    
# ==============================
# plot_TOP10_gene_pairs_bar_chart 
# ==============================
def plot_TOP10_gene_pairs_bar_chart(reversal_gene_pairs, folder_path):
    # Calculate the number of rows
    num_rows = len(reversal_gene_pairs)
    
    # Determine the number of rows to extract
    top_n = min(10, num_rows)
    
    # Generate the Gene_pair column by concatenating the first and second columns with "-"
    reversal_gene_pairs["Gene_pair"] = reversal_gene_pairs["Gene1"] + "-" + reversal_gene_pairs["Gene2"]
    
    # Extract the top_n rows of Gene_pair and ImportanceScore
    top_n_result = reversal_gene_pairs.iloc[:top_n][["Gene_pair", "ImportanceScore"]].reset_index(drop=True)
  
    # Extract as a list
    Gene_pair = top_n_result["Gene_pair"].tolist()
    ImportanceScore = top_n_result["ImportanceScore"].tolist()
    
    # Dynamically calculate the figure height based on the number of data points
    fig_height = top_n * 0.3 + 1  
    
    # Create a horizontal bar chart
    plt.figure(figsize=(4, fig_height))
    bar_height = 0.8
    bars = plt.barh(Gene_pair, ImportanceScore, color='#007a99', edgecolor='black', height=bar_height)
    plt.grid(False)
    
    # Add title and labels
    plt.title('Top 10 Gene pairs', fontsize=14, fontweight='bold') 
    plt.xlabel('ImportanceScore', fontsize=12, labelpad=10)
    
    # Adjust layout and font
    plt.yticks(fontsize=10)
    plt.xticks(fontsize=10)
    
    # Invert the y-axis to arrange bars from top to bottom
    plt.gca().invert_yaxis()
    
    # Remove the top and right borders
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    
    # Bold the X-axis and Y-axis lines
    plt.gca().spines['bottom'].set_linewidth(2)
    plt.gca().spines['bottom'].set_color('black')
    plt.gca().spines['left'].set_linewidth(2) 
    plt.gca().spines['left'].set_color('black')
    
    # Add data labels
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.02, bar.get_y() + bar.get_height()/2, f'{width:.3f}', 
                 va='center', ha='left', fontsize=9, color='black')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    file_path = os.path.join(folder_path, "TOP10_gene_pairs_bar_chart.pdf")
    plt.savefig(file_path, format='pdf', dpi=600, bbox_inches='tight')   

    png_path = os.path.join(folder_path, "TOP10_gene_pairs_bar_chart.png")
    plt.savefig(png_path, format='png', dpi=300, bbox_inches='tight')
        
# ==============================
#    plot_DP_score_bar_chart 
# ==============================
def plot_DP_score_bar_chart(Disease_perturbation_scoring, colors, folder_path):
    # Group the data and extract, then sort in ascending order
    group_scores = Disease_perturbation_scoring.groupby('Rank').apply(lambda group: sorted(group['DP_Score'])).to_dict()
    class_mapping = Disease_perturbation_scoring.drop_duplicates(subset=['Rank'])[['Rank', 'Class']].set_index('Rank')['Class'].to_dict()
    class_group_scores = {class_mapping[rank]: scores for rank, scores in group_scores.items()}

    # Calculate the total number of samples
    total_samples = len(Disease_perturbation_scoring)

    # Dynamically adjust the figure width based on the total number of samples
    fig_width = 8 + total_samples * 0.025 

    # Create a bar chart
    plt.figure(figsize=(fig_width, 4))
    plt.ylim(-0.1, 1.1)
    plt.yticks(fontsize=10)

    # Set the width of the bars
    bar_width = 1

    # Loop through each group of data
    x = 0
    for i, (classname, scores) in enumerate(class_group_scores.items()):
        group_length = len(scores)
        x_pos = np.arange(x, x + group_length)
        scores = [x + 0.1 for x in scores]
        plt.bar(x_pos, scores, width=bar_width, color=colors[i], edgecolor='black', linewidth=bar_width * 0.1, label=classname, bottom=-0.1)
        x += group_length

    # Hide X-axis tick labels
    plt.xticks([])

    # Add denser grid lines
    plt.grid(True, linestyle='--', alpha=0.7)

    # Add axis labels
    plt.ylabel('DP_Score', fontsize=12)

    # Add legend
    plt.legend(title='Class', fontsize=10, loc='upper left')

    # Get the current axes
    ax = plt.gca()

    # Set border color to black and make it bold
    ax.spines['top'].set_linewidth(1)
    ax.spines['top'].set_color('black')
    ax.spines['bottom'].set_linewidth(1)
    ax.spines['bottom'].set_color('black')
    ax.spines['left'].set_linewidth(1)
    ax.spines['left'].set_color('black')
    ax.spines['right'].set_linewidth(1)
    ax.spines['right'].set_color('black')

    # Save the figure
    file_path = os.path.join(folder_path, "DP_score_bar_chart.pdf")
    plt.savefig(file_path, format='pdf', dpi=600, bbox_inches='tight') 

    png_path = os.path.join(folder_path, "DP_score_bar_chart.png")
    plt.savefig(png_path, format='png', dpi=300, bbox_inches='tight')

# ==============================
#     plot_DP_score_boxplot
# ==============================
def plot_DP_score_boxplot(Disease_perturbation_scoring, colors, folder_path):
    # Sort by values in the 'Rank' column
    Disease_perturbation_scoring_sorted = Disease_perturbation_scoring.sort_values(by='Rank')

    # Extract DP_Score values corresponding to each Rank
    ranks = Disease_perturbation_scoring_sorted['Rank'].unique()
    data_by_rank = [Disease_perturbation_scoring_sorted[Disease_perturbation_scoring_sorted['Rank'] == rank]['DP_Score'].values for rank in ranks]

    # Extract Class names corresponding to each Rank
    class_names = [Disease_perturbation_scoring_sorted[Disease_perturbation_scoring_sorted['Rank'] == rank]['Class'].iloc[0] for rank in ranks]
    
    # Dynamically adjust the figure width based on the total number of samples
    total_groups = len(ranks)
    fig_width = 0.5 + total_groups * 1

    # Create a boxplot
    plt.figure(figsize=(fig_width, 3.5))
    plt.ylim(-0.1, 1.1)
    plt.yticks(fontsize=10)

    # Plot the boxplot
    boxplots = plt.boxplot(
        data_by_rank,
        positions=ranks,
        widths=0.7,
        patch_artist=True,
        boxprops=dict(facecolor='white', color='black'),
        medianprops=dict(color='black'),
        whiskerprops=dict(color='black'),
        capprops=dict(color='black'),
        flierprops=dict(marker='') 
    )

    # Set the color of the boxplot
    for i, patch in enumerate(boxplots['boxes']):
        color = colors[i] 
        patch.set_facecolor(color)  
        patch.set_edgecolor('black') 

    # Plot scatter points
    for i, rank in enumerate(ranks):
        scatter_color = colors[i] 
        rank_data = Disease_perturbation_scoring_sorted[Disease_perturbation_scoring_sorted['Rank'] == rank]
        plt.scatter(
            np.random.normal(rank, 0.04, len(rank_data)), 
            rank_data['DP_Score'],
            color=scatter_color,
            edgecolor='black',
            linewidths=1,  
            alpha=0.7,
            s=30,
            zorder=10
        )

    #  Set axis labels and title
    plt.ylabel('DP_Score', fontsize=12)

    # Set x-axis ticks and labels
    plt.xticks(ranks, class_names, fontsize=10)
    plt.xlim(ranks[0] - 0.5, ranks[-1] + 0.5)

    # Set border color to black and make it bold
    ax = plt.gca()
    ax.spines['top'].set_linewidth(1)
    ax.spines['top'].set_color('black')
    ax.spines['bottom'].set_linewidth(1)
    ax.spines['bottom'].set_color('black')
    ax.spines['left'].set_linewidth(1)
    ax.spines['left'].set_color('black')
    ax.spines['right'].set_linewidth(1)
    ax.spines['right'].set_color('black')

    # Add grid lines
    plt.grid(True, linestyle='--', alpha=0.7)

    # Save the chart
    file_path = os.path.join(folder_path, "DP_score_boxplot.pdf")
    plt.savefig(file_path, format='pdf', dpi=600, bbox_inches='tight') 

    png_path = os.path.join(folder_path, "DP_score_boxplot.png")
    plt.savefig(png_path, format='png', dpi=300, bbox_inches='tight')

# ==============================
# plot_DP_score_with_sample_information 
# ==============================
def plot_DP_score_with_sample_information(Disease_perturbation_scoring, colors, folder_path, sample_info_category=None, sample_category=None, data_type=None):
    # 1. If none of the three parameters are provided, do not process
    if sample_info_category is None and sample_category is None and data_type is None:
        return

    # 2. If the parameters are incomplete, show an error message
    if not (sample_info_category and sample_category and data_type):
        raise ValueError("Please provide sample_info_category, sample_category, and data_type parameters together!")
    
    # 3. Check if sample_info_category exists
    if sample_info_category not in Disease_perturbation_scoring.columns:
        raise ValueError("Invalid sample information category input!")
    
    # 4. Check if sample_category exists
    if sample_category not in Disease_perturbation_scoring['Class'].unique():
        raise ValueError("Invalid sample category input!")

    # 5. Retrieve scores and corresponding sample information data for the specified sample category
    selected_scores_info = Disease_perturbation_scoring[Disease_perturbation_scoring['Class'] == sample_category][['DP_Score', sample_info_category]]
    
    # 6. Plotting
    if data_type.lower() == "discrete":
        # Adjust data
        data_class = selected_scores_info[sample_info_category].unique()
        data_class_index = np.arange(len(data_class))
        data_by_class = [selected_scores_info[selected_scores_info[sample_info_category] == dataclass]['DP_Score'].values for dataclass in data_class]

        # Dynamically adjust the figure width based on the total number of categories
        total_groups = len(data_class_index)
        fig_width = 0.5 + total_groups * 1
        
        # Create a boxplot
        plt.figure(figsize=(fig_width, 3.5))
        plt.ylim(0, 1)
        plt.yticks(fontsize=10)

        # Create a boxplot
        boxplots = plt.boxplot(
            data_by_class,
            positions=data_class_index,
            widths=0.7,
            patch_artist=True,
            boxprops=dict(facecolor='white', color='black'),
            medianprops=dict(color='black'),
            whiskerprops=dict(color='black'),
            capprops=dict(color='black'),
            flierprops=dict(marker='')  
        )
        
        # Set boxplot colors
        for i, patch in enumerate(boxplots['boxes']):
            color = colors[i] 
            patch.set_facecolor(color)  
            patch.set_edgecolor('black') 
            
        # Plot scatter points
        for i, dataclass in enumerate(data_class):
            data = pd.Series(data_by_class[i])
            scatter_color = colors[i] 
            class_data = selected_scores_info[selected_scores_info[sample_info_category] == dataclass]
            plt.scatter(
                np.random.normal(i, 0.04, len(class_data)), 
                data,
                color=scatter_color,
                edgecolor='black',
                linewidths=1,  
                alpha=0.7,
                s=30,
                zorder=10
            )
            
        # Configure axis settings
        class_names = data_class.tolist()
        plt.ylabel('DP_Score', fontsize=12)
        plt.xticks(data_class_index, class_names, fontsize=10)
        plt.xlim(data_class_index[0] - 0.5, data_class_index[-1] + 0.5)

        # Set border color to black and make it bold
        ax = plt.gca()
        ax.spines['top'].set_linewidth(1)
        ax.spines['top'].set_color('black')
        ax.spines['bottom'].set_linewidth(1)
        ax.spines['bottom'].set_color('black')
        ax.spines['left'].set_linewidth(1)
        ax.spines['left'].set_color('black')
        ax.spines['right'].set_linewidth(1)
        ax.spines['right'].set_color('black')

        # Set chart title including Spearman correlation coefficient and p-value
        ax.set_title(f'{sample_category}: DP_Score vs {sample_info_category}', fontsize=12, fontweight='bold')
        
        # Add grid lines
        plt.grid(True, linestyle='--', alpha=0.7)
    
        # Save the figure
        file_path = os.path.join(folder_path, "DP_score_with_sample_information.pdf")
        plt.savefig(file_path, format='pdf', dpi=600, bbox_inches='tight') 

        png_path = os.path.join(folder_path, "DP_score_with_sample_information.png")
        plt.savefig(png_path, format='png', dpi=300, bbox_inches='tight')

    elif data_type.lower() == "continuous":
        fig, ax = plt.subplots(figsize=(4.9, 4))

        selected_scores = selected_scores_info['DP_Score']
        selected_info = selected_scores_info[sample_info_category]
        
        # Draw scatter plot
        scatter = ax.scatter(selected_scores, selected_info, c=selected_scores, cmap='viridis', edgecolor='k', alpha=0.7, s=50)

        # Add color bar indicating the mapping between color and value
        cbar = plt.colorbar(scatter)
        cbar.ax.tick_params(labelsize=10)
        cbar.set_label('DP_Score', fontsize=12)

        rho, p_value = spearmanr(selected_scores, selected_info)

        # Set chart title including Spearman correlation coefficient and p-value
        ax.set_title(f'{sample_category}: DP_Score vs {sample_info_category}\nSpearman ρ = {rho:.2f}, p = {p_value:.3f}', fontsize=12, fontweight='bold')

        # Add grid lines with specific line style and transparency
        ax.grid(True, linestyle='--', alpha=0.7)

        # Set axis labels
        ax.set_xlabel('DP_Score', fontsize=12)
        ax.set_ylabel(sample_info_category, fontsize=12)

        # Adjust axis tick label font size
        ax.tick_params(axis='both', which='major', labelsize=10)

        # Save the figure
        file_path = os.path.join(folder_path, "DP_score_with_sample_information.pdf")
        plt.savefig(file_path, format='pdf', dpi=600, bbox_inches='tight') 

        png_path = os.path.join(folder_path, "DP_score_with_sample_information.png")
        plt.savefig(png_path, format='png', dpi=300, bbox_inches='tight')

    else:
        raise ValueError("Error in data_type parameter, please enter 'Discrete' or 'Continuous'!")
        
# ==============================
#           DPS_Tool
# ==============================
def DPS_Tool(expression_matrix_input, sample_info_input, negative_category, positive_category, folder_path,
             reversal_ratio_threshold=0.5, remove_duplicate_gene_pairs=False, gene_set_input=None,
             sample_info_category=None, sample_category=None, data_type=None):
    """
    DPS_Tool(Disease Perturbation Scoring Tool):A Function for Disease Perturbation Scoring

    Input Parameters:
    1. expression_matrix_input (Expression Matrix):
       - CSV file
       - Gene expression data, including either coding or non-coding genes
       - The first column must be Gene symbol (column name: "Symbol"), and the remaining columns are expression levels for each sample (column names: sample names)
       - The number of sample classes should be between 2 and 10, and both the negative and positive classes must each have ≥10 samples
       - The number of genes must be greater than 100
       - Expression values can be normalized or raw (e.g., Count, TPM, FPKM, etc.)
       - Each gene must have non-zero expression in at least 80% of the samples
    2. sample_info_input (Sample Information Matrix):
       - CSV file
       - First column: sample name (column name: "Sample"),
       - Second column: sample class label (column name: "Class"),
       - Third column: sample rank value indicating severity from negative to positive samples using integers starting from 0 (column name: "Rank")
       - Additional sample information (e.g., sex, age) can be included in other columns (either discrete or continuous), but must not contain any NA values
    3. negative_category (Negative Class):
       - The category representing negative samples used for analysis
       - Must exist in the "Class" column of the sample information matrix
    4. positive_category (Positive Class):
       - The category representing positive samples used for analysis
       - Must exist in the "Class" column of the sample information matrix
    5. folder_path (Output Path)
    6. reversal_ratio_threshold (Reversal Ratio Threshold):
       - Threshold used to extract reversed gene pairs
       - Value must be ≥ 0.3 and ≤ 1, default is 0.5
    7. remove_duplicate_gene_pairs (Remove Duplicate Gene Pairs):
       - By default, duplicates are not removed
       - If enabled, for gene pairs with the same gene(s), only the one with the highest reversal ratio will be retained
    8. gene_set_input (Gene Set) (Optional):
       - CSV file
       - A single-column file where the column name is the gene set name
       - Gene symbols in the column must exist in the "Symbol" column of the expression matrix
    9. sample_info_category (Sample Information Category) (Optional):
       - Column name in the sample info matrix to be used for correlation analysis
       - Must be provided together with sample_category and data_type
    10. sample_category (Sample Category) (Optional):
       - Sample class used for correlation analysis
       - Must exist in the "Class" column of the sample information matrix
       - Must be provided together with sample_info_category and data_type
    11. data_type (Data Type) (Optional):
       - Type of the sample information for correlation analysi
       - Must be either "Discrete" or "Continuous"
       - Must be provided together with sample_info_category and sample_category

    Output:
    1. Gene Pairs Table:
    - Columns: [Gene1, Gene2, ReversalRatio, ImportanceScore]
    - Sorted in descending order by ImportanceScore
    2. DP_score Table:
    - Based on the sample information matrix, with two additional columns: [DP_Score, Outlier]
    3. Bar Plot of Top 10 Gene Pairs by Importance Score
    4. Bar Plot of Disease Perturbation Scores
    5. Boxplot of Disease Perturbation Scores Grouped by Sample Class
    6. If sample_info_category, sample_category, and data_type are provided: Additional boxplot or correlation plot will be generated

    Example Dataset:
    Transcriptome data from 58 pancreatic islet samples from patients undergoing pancreatectomy:
    - 30 with T2D (Type 2 Diabetes)
    - 28 non-diabetic (ND)
    - Includes fasting glucose levels and gene sets related to β-cell identity and maturity
    """

    # ------------------------------
    # 1. Import expression matrix
    # ------------------------------
    expr_df = pd.read_csv(expression_matrix_input, sep=',')
    
    # ------------------------------
    # 2. Import sample information matrix
    # -----------------------------
    sample_df = pd.read_csv(sample_info_input, sep=',')
        
    # ------------------------------
    # 3. Adjust matrix order and obtain negative and positive sample counts
    # ------------------------------
    negative_samples = sample_df[sample_df['Class'] == negative_category]['Sample'].tolist()
    positive_samples = sample_df[sample_df['Class'] == positive_category]['Sample'].tolist()
    
    # Extract expression matrix for negative and positive samples
    expr_df1 = expr_df[['Symbol'] + negative_samples + positive_samples]
    negative_samples_num = len(negative_samples)
    positive_samples_num = len(positive_samples)

    # ------------------------------
    # 4. Extract reversed gene pairs
    # ------------------------------
    reverse_gene_pairs_reslut = Reverse_gene_pairs(expr_df1, negative_samples_num, positive_samples_num, reversal_ratio_threshold, remove_duplicate_gene_pairs, gene_set_input)

    # ------------------------------
    # 5. Calculate disease perturbation scores and export the score table
    # ------------------------------
    # Calculate disease perturbation scores
    expr_df = expr_df.set_index(expr_df.columns[0]) 
    Disease_perturbation_scoring, diff_matrix = DP_Score(reverse_gene_pairs_reslut, expr_df, sample_df)

    # Export disease perturbation score table
    file_path = os.path.join(folder_path, "DP_score_table.csv")
    Disease_perturbation_scoring.to_csv(file_path)

    # ------------------------------
    # 6. Calculate ImportanceScore of gene pairs and export reversed gene pairs table
    # ------------------------------
    # 1. Get sample names where Rank == 0
    rank_0_samples = Disease_perturbation_scoring.loc[Disease_perturbation_scoring['Rank'] == 0, 'Sample']
    
    # 2. Subset expression matrix
    matrix_A = diff_matrix[rank_0_samples] 
    matrix_B = diff_matrix.drop(columns=rank_0_samples)  
    
    # 3. Compute ImportanceScore
    count_A = (matrix_A < 0).sum(axis=1)  
    count_B = (matrix_B >= 0).sum(axis=1)  
    total_samples = expr_df.shape[1]  
    importance_score = (count_A + count_B) / total_samples  
    
    # 4. Add ImportanceScore to reverse_gene_pairs_result
    reverse_gene_pairs_reslut = reverse_gene_pairs_reslut.reset_index(drop=True)
    reverse_gene_pairs_reslut['ImportanceScore'] = importance_score
    
    # 5. Sort by ImportanceScore in descending order
    reverse_gene_pairs_reslut = reverse_gene_pairs_reslut.sort_values(by='ImportanceScore', ascending=False).reset_index(drop=True)
    
    # 6. Export reversed gene pairs table
    file_path = os.path.join(folder_path, "Gene_pairs_table.csv")
    reverse_gene_pairs_reslut.to_csv(file_path)

    # ------------------------------
    # 7. Plot bar chart of TOP 10 gene pairs
    # ------------------------------
    TOP10_gene_pairs_bar_chart = plot_TOP10_gene_pairs_bar_chart(reverse_gene_pairs_reslut, folder_path)
    plt.close() 
    
    # ------------------------------
    # 10. Plot score bar chart
    # ------------------------------
    # Define color list
    colors = [
        '#AEC7E8', '#FFBB78', '#98DF8A', '#FF9896', 
        '#C5B0D5', '#C49C94', '#F7B6D2', '#C7C7C7', 
        '#DBDB8D', '#9EDAE5'
    ]
    
    DP_score_bar_chart = plot_DP_score_bar_chart(Disease_perturbation_scoring, colors, folder_path)
    plt.close() 

    # ------------------------------
    # 11. Plot score boxplot
    # ------------------------------
    DP_score_boxplot = plot_DP_score_boxplot(Disease_perturbation_scoring, colors, folder_path)
    plt.close() 
    
    # ------------------------------
    # 12. Analyze scores in relation to sample information
    # ------------------------------
    DP_score_with_sample_information = plot_DP_score_with_sample_information(Disease_perturbation_scoring, colors, folder_path, sample_info_category=sample_info_category, sample_category=sample_category, data_type=data_type)
    plt.close() 
    
    # ------------------------------
    # 13. Output results
    # ------------------------------
    Reverse_gene_pairs_result = reverse_gene_pairs_reslut.iloc[:, :-1]

def main():
    try:
        parser = argparse.ArgumentParser(description='DPS-Tool Analysis Script')
        parser.add_argument('--expression_matrix', required=True, help='Path to expression matrix file')
        parser.add_argument('--sample_info', required=True, help='Path to sample information file')
        parser.add_argument('--negative_class', required=True, help='Negative sample class')
        parser.add_argument('--positive_class', required=True, help='Positive sample class')
        parser.add_argument('--output_dir', required=True, help='Output directory')
        parser.add_argument('--reversion_threshold', type=float, required=True, help='Reversal ratio threshold')
        parser.add_argument('--deduplicate', choices=['True', 'False'], required=True, help='Whether to deduplicate gene pairs')
        parser.add_argument('--gene_set_file', default=None, help='Path to gene set file (optional)')
        parser.add_argument('--sample_info_category', default=None, help='Sample information category (optional)')
        parser.add_argument('--sample_category', default=None, help='Sample category (optional)')
        parser.add_argument('--data_type', default=None, help='Data type (optional)')

        args = parser.parse_args()

        # Convert string to boolean
        deduplicate = args.deduplicate == 'True'

        DPS_Tool(
            args.expression_matrix,
            args.sample_info, 
            args.negative_class,
            args.positive_class,
            args.output_dir,
            args.reversion_threshold,
            deduplicate,     
            args.gene_set_file, 
            args.sample_info_category, 
            args.sample_category, 
            args.data_type
            )

        # Update task status to 'completed'
        task_id = os.path.basename(args.output_dir)
        with open(f"task_status/{task_id}.status", "w") as f:
            f.write("completed")

    except Exception as e:
        # Update task status to 'failed'
        task_id = os.path.basename(args.output_dir)
        with open(f"task_status/{task_id}.status", "w") as f:
            f.write(f"failed: {str(e)}")    
                
if __name__ == '__main__':
    main()