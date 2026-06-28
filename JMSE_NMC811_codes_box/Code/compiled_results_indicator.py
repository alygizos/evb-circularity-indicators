"""
Compiled Results Indicator Plot
Reads cumulative_results_indicators.csv and creates comparison bar plot
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'Arial'

def plot_compiled_indicators(csv_file='cumulative_results_indicators.csv',
                             save_path='compiled_indicators_comparison.png',
                             dpi=300,
                             figsize=(14, 7)):
    """
    Read cumulative results CSV and create comparison bar plot with error bars.

    Parameters:
    -----------
    csv_file : str
        Path to cumulative results CSV file
    save_path : str
        Path to save the output plot
    dpi : int
        Resolution of saved plot
    figsize : tuple
        Figure size (width, height)
    """

    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        print("Please run the individual indicator scripts first to generate the cumulative results.")
        return

    # Read CSV
    df = pd.read_csv(csv_file)

    print("\n" + "="*70)
    print("COMPILED CIRCULARITY INDICATORS")
    print("="*70)

    # Extract data
    indicators = df['Indicator'].tolist()
    means = df['Mean'].tolist()
    ci_lowers = df['CI_Lower'].tolist()
    ci_uppers = df['CI_Upper'].tolist()

    # Calculate error bars
    errors_lower = [means[i] - ci_lowers[i] for i in range(len(means))]
    errors_upper = [ci_uppers[i] - means[i] for i in range(len(means))]

    # Print summary
    print("\nIndicator Summary:")
    print("-"*70)
    for i, ind in enumerate(indicators):
        print(f"{ind:6s}: {means[i]:.4f}  (95% CI: [{ci_lowers[i]:.4f}, {ci_uppers[i]:.4f}])")
    print("="*70)

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Define colors for each indicator
    color_map = {
        'PCI': '#3498db',   # Blue
        'CI': '#2ecc71',    # Green
        'CEI': '#e74c3c',   # Red
        'ECPI': '#9b59b6',  # Purple
        'M': '#f39c12',     # Orange
        'R': '#1abc9c',     # Turquoise
        'E': '#e67e22'      # Dark Orange
    }

    colors = [color_map.get(ind, '#95a5a6') for ind in indicators]

    # Create bars
    x_pos = np.arange(len(indicators))
    bars = ax.bar(x_pos, means, color=colors, alpha=0.8,
                  edgecolor='black', linewidth=1.5, width=0.6)

    # Add error bars
    ax.errorbar(x_pos, means,
                yerr=[errors_lower, errors_upper],
                fmt='none',
                ecolor='black',
                elinewidth=2.5,
                capsize=10,
                capthick=2.5,
                zorder=10)

    # Customize plot
    ax.set_xlabel('Circularity Indicator', fontsize=16, fontweight='bold')
    ax.set_ylabel('Indicator Value', fontsize=16, fontweight='bold')
    ax.set_title('Comparison of Circularity Indicators\n(with 95% Confidence Intervals)',
                 fontsize=18, fontweight='bold', pad=20)

    # Set x-axis
    ax.set_xticks(x_pos)
    ax.set_xticklabels(indicators, fontsize=14, fontweight='bold')

    # Set y-axis
    ax.set_ylim(0, max(means) * 1.35)
    ax.tick_params(axis='y', labelsize=12)

    # Add value labels on bars
    for i, (bar, mean_val, err_up) in enumerate(zip(bars, means, errors_upper)):
        ax.text(bar.get_x() + bar.get_width()/2.,
                mean_val + err_up + max(means) * 0.03,
                f'{mean_val:.4f}',
                ha='center', va='bottom',
                fontsize=13, fontweight='bold')

    # Add grid
    ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.8)
    ax.set_axisbelow(True)

    # Tight layout
    plt.tight_layout()

    # Save figure
    plt.savefig(save_path, dpi=dpi, bbox_inches='tight')

    print(f"\n{'='*70}")
    print(f"Comparison plot saved to: {save_path}")
    print(f"{'='*70}\n")

    return fig, ax


if __name__ == "__main__":
    print("\n" + "="*70)
    print("CIRCULARITY INDICATORS COMPILATION SCRIPT")
    print("="*70)
    print("\nThis script reads cumulative results from:")
    print("  cumulative_results_indicators.csv")
    print("\nand creates a comparison bar plot with error bars.")
    print("="*70)

    # Create comparison plot
    fig, ax = plot_compiled_indicators(
        csv_file='cumulative_results_indicators.csv',
        save_path='compiled_indicators_comparison.png',
        dpi=300,
        figsize=(14, 7)
    )

    if fig is not None:
        print("="*70)
        print("COMPILATION COMPLETE!")
        print("="*70)
        print("\nNote: To update the plot, run the individual indicator scripts:")
        print("  - pci/pci_indicator_v2.py")
        print("  - ci/ci_indicator.py")
        print("  - cei/cei_indicator.py")
        print("  - ecpi/ecpi_indicator.py")
        print("  - mre/mre_indicator.py")
        print("="*70)
