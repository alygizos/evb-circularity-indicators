from typing import Sequence
import math
import numpy as np
import csv
import os
import matplotlib.pyplot as plt
import seaborn as sns

def compute_ecpi(m_in_circular, m_in_virgin,
                 m_out_circular, m_out_linear,
                 LCA_emissions_circular, LCA_emissions_linear):

    """
    ECPI (Carmona Aparicio et al., 2025)

    Parameters:
    -----------
    m_in_circular : array-like
        Array of circular input masses for [aluminium, cobalt, copper, graphite,
        lithium, manganese, nickel, steel]
    m_in_virgin : array-like
        Array of virgin input masses for same materials
    m_out_circular : array-like
        Array of circular output masses for same materials
    m_out_linear : array-like
        Array of linear output masses for same materials
    LCA_emissions_circular : float
        Total LCA emissions for circular pathway
    LCA_emissions_linear : float
        Total LCA emissions for linear pathway

    Formula:
    --------
    α_in  = sum(m_in_circular) / (sum(m_in_circular) + sum(m_in_virgin))
    α_out = sum(m_out_circular) / (sum(m_out_circular) + sum(m_out_linear))
    α     = α_in * α_out
    β     = 1 - (LCA_emissions_circular / LCA_emissions_linear)
    ECPI  = α * β
    """

    # Sum the mass arrays for each flow
    total_m_in_circular = np.sum(m_in_circular)
    total_m_in_virgin = np.sum(m_in_virgin)
    total_m_out_circular = np.sum(m_out_circular)
    total_m_out_linear = np.sum(m_out_linear)

    # Calculate alpha components using summed masses
    alpha_inflow = total_m_in_circular / (total_m_in_virgin)
    alpha_out    = total_m_out_circular / (total_m_out_linear)
    alpha        = alpha_inflow * alpha_out

    # Calculate beta using singular LCA emission values
    beta         = 1 - (LCA_emissions_circular / LCA_emissions_linear)

    # Calculate ECPI
    ecpi         = alpha * beta

    print(alpha,beta)

    return ecpi, alpha_inflow, alpha_out, beta


def load_ecpi_data_from_csv(csv_path='ECPI_indicator_alpha_sum.csv'):
    """
    Load ECPI data from CSV file.

    Parameters
    ----------
    csv_path : str
        Path to CSV file

    Returns
    -------
    dict
        Dictionary with arrays for m_in_circular, m_in_virgin, m_out_circular,
        m_out_linear, and scalars for LCA emissions
    """
    m_in_virgin = []
    m_in_circular = []
    m_out_linear = []
    m_out_circular = []
    LCA_emissions_circular = None
    LCA_emissions_linear = None

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['material'] == 'LCA_emissions_circular':
                LCA_emissions_circular = float(row['m_in_virgin'])
            elif row['material'] == 'LCA_emissions_linear':
                LCA_emissions_linear = float(row['m_in_virgin'])
            else:
                m_in_virgin.append(float(row['m_in_virgin']))
                m_in_circular.append(float(row['m_in_circular']))
                m_out_linear.append(float(row['m_out_linear']))
                m_out_circular.append(float(row['m_out_circular']))
    print(LCA_emissions_circular, LCA_emissions_linear)
    return {
        'm_in_circular': np.array(m_in_circular),
        'm_in_virgin': np.array(m_in_virgin),
        'm_out_circular': np.array(m_out_circular),
        'm_out_linear': np.array(m_out_linear),
        'LCA_emissions_circular': LCA_emissions_circular,
        'LCA_emissions_linear': LCA_emissions_linear
    }


def print_ecpi_results(data, ecpi, alpha_in, alpha_out, beta):

    print("\n" + "="*80)
    print("ECPI (Environmental Circular Performance Index) RESULTS")
    print("="*80)
    print("\nInput/Output Mass Flows:")
    print("-"*80)
    print(f"  Total m_in_circular:    {np.sum(data['m_in_circular']):.4f} kg")
    print(f"  Total m_in_virgin:      {np.sum(data['m_in_virgin']):.4f} kg")
    print(f"  Total m_out_circular:   {np.sum(data['m_out_circular']):.4f} kg")
    print(f"  Total m_out_linear:     {np.sum(data['m_out_linear']):.4f} kg")
    print("-"*80)
    print(f"\nLCA Emissions:")
    print(f"  Circular pathway:       {data['LCA_emissions_circular']:.4f} kg CO2-eq")
    print(f"  Linear pathway:         {data['LCA_emissions_linear']:.4f} kg CO2-eq")
    print("-"*80)
    print(f"\nECPI Components:")
    print(f"  α_in (inflow):          {alpha_in:.4f}")
    print(f"  α_out (outflow):        {alpha_out:.4f}")
    print(f"  α (product):            {alpha_in * alpha_out:.4f}")
    print(f"  β (emissions):          {beta:.4f}")
    print("-"*80)
    print(f"\nECPI (Final):             {ecpi:.4f}")
    print(f"ECPI Percentage:          {ecpi*100:.2f}%")
    print("="*80 + "\n")


def plot_ecpi_bar_chart(ecpi_value, save_path='ecpi_bar_chart.png', dpi=300, figsize=(6, 6)):
    """
    Create journal-quality bar plot for ECPI (cumulative result).

    Parameters
    ----------
    ecpi_value : float
        Computed ECPI value
    save_path : str
        Path to save figure
    dpi : int
        Resolution
    figsize : tuple
        Figure size
    """
    # Set publication-quality style
    sns.set_style("whitegrid")
    sns.set_context("paper", font_scale=1.5)

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)

    # Create bar
    colors = ['#9b59b6']  # Purple color for ECPI
    bars = ax.bar([0], [ecpi_value], color=colors, edgecolor='black',
                   linewidth=1.2, alpha=0.8, width=0.5)

    # Customize plot
    ax.set_ylabel('ECPI Value', fontweight='bold', fontsize=14)
    ax.set_title('Environmental Circular Performance Index\n(Carmona Aparicio et al., 2025)',
                 fontweight='bold', fontsize=14, pad=20)

    # Set x-axis
    ax.set_xticks([0])
    ax.set_xticklabels(['Cumulative ECPI'])

    # Add value label on top of bar
    height = bars[0].get_height()
    ax.text(0, height, f'{ecpi_value:.4f}\n({ecpi_value*100:.2f}%)',
            ha='center', va='bottom', fontsize=12, fontweight='bold')

    # Add grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    # Set y-axis limits
    ax.set_ylim(0, max(1.0, ecpi_value * 1.15))

    plt.tight_layout()
    plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
    print(f"\nECPI bar chart saved to: {save_path}")
    plt.show()

    return fig, ax


def monte_carlo_ecpi(csv_path='ECPI_indicator_alpha_sum.csv', n_samples=1000,
                     uncertainty_pct=0.05, confidence_level=0.95):
    """
    Perform Monte Carlo simulation for ECPI uncertainty analysis.
    Varies m_in_circular and m_out_circular parameters.

    Parameters
    ----------
    csv_path : str
        Path to CSV file
    n_samples : int
        Number of MC samples
    uncertainty_pct : float
        Uncertainty percentage (0.05 = 5%)
    confidence_level : float
        Confidence level (0.95 = 95%)

    Returns
    -------
    dict
        Statistics for ECPI
    """
    # Load base data
    base_data = load_ecpi_data_from_csv(csv_path)

    # Storage for results
    mc_results = []

    # Monte Carlo sampling
    for _ in range(n_samples):
        # Perturb m_in_circular
        std_dev = np.abs(base_data['m_in_circular'] * uncertainty_pct)
        perturbed_m_in_circular = np.maximum(0.0,
            np.random.normal(base_data['m_in_circular'], std_dev))

        # Perturb m_out_circular
        std_dev = np.abs(base_data['m_out_circular'] * uncertainty_pct)
        perturbed_m_out_circular = np.maximum(0.0,
            np.random.normal(base_data['m_out_circular'], std_dev))

        # Compute ECPI with perturbed parameters
        ecpi, _, _, _ = compute_ecpi(
            perturbed_m_in_circular,
            base_data['m_in_virgin'],
            perturbed_m_out_circular,
            base_data['m_out_linear'],
            base_data['LCA_emissions_circular'],
            base_data['LCA_emissions_linear']
        )
        mc_results.append(ecpi)

    # Calculate statistics
    alpha = 1 - confidence_level
    values_array = np.array(mc_results)
    mean_val = np.mean(values_array)
    std_val = np.std(values_array)
    lower_ci = np.percentile(values_array, alpha/2 * 100)
    upper_ci = np.percentile(values_array, (1 - alpha/2) * 100)

    stats = {
        'mean': mean_val,
        'std': std_val,
        'lower_ci': lower_ci,
        'upper_ci': upper_ci,
        'error_bar': (mean_val - lower_ci, upper_ci - mean_val)
    }

    return stats, mc_results


def plot_ecpi_with_error_bars(csv_path='ECPI_indicator_alpha_sum.csv', n_samples=1000,
                              uncertainty_pct=0.05, save_path='ecpi_with_error_bars.png',
                              dpi=300, figsize=(6, 6)):
    """
    Create ECPI bar plot with Monte Carlo error bars.

    Parameters
    ----------
    csv_path : str
        Path to CSV file
    n_samples : int
        Number of MC samples
    uncertainty_pct : float
        Uncertainty percentage
    save_path : str
        Path to save figure
    dpi : int
        Resolution
    figsize : tuple
        Figure size
    """
    print(f"\nRunning Monte Carlo simulation with {n_samples} samples...")
    stats, mc_results = monte_carlo_ecpi(csv_path, n_samples, uncertainty_pct)

    # Set style
    sns.set_style("whitegrid")
    sns.set_context("paper", font_scale=1.5)

    fig, ax = plt.subplots(figsize=figsize)

    # Prepare data
    mean = stats['mean']
    error_lower = stats['error_bar'][0]
    error_upper = stats['error_bar'][1]

    # Create color
    colors = ['#9b59b6']  # Purple

    # Create bar plot with error bars
    bars = ax.bar([0], [mean], color=colors, edgecolor='black',
                   linewidth=1.2, alpha=0.8, width=0.5)
    ax.errorbar([0], [mean], yerr=[[error_lower], [error_upper]],
                fmt='none', ecolor='black', capsize=5, capthick=2, linewidth=2)

    # Customize plot
    ax.set_ylabel('ECPI Value', fontweight='bold', fontsize=14)
    ax.set_title(f'ECPI with 95% Confidence Intervals\n(Monte Carlo: {n_samples} samples, {uncertainty_pct*100}% uncertainty)',
                 fontweight='bold', fontsize=14, pad=20)

    # Set x-axis
    ax.set_xticks([0])
    ax.set_xticklabels(['Cumulative ECPI'])

    # Add value label
    ax.text(0, mean, f'{mean:.4f}\n({mean*100:.2f}%)',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

    # Add grid
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    # Set y-axis limits
    ax.set_ylim(0, max(1.0, mean * 1.2))

    plt.tight_layout()
    plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
    print(f"ECPI bar chart with error bars saved to: {save_path}")
    plt.show()

    # Print statistics
    print("\n" + "=" * 70)
    print("MONTE CARLO SIMULATION RESULTS")
    print("=" * 70)
    print(f"\nCumulative ECPI:")
    print(f"  Mean ECPI:   {stats['mean']:.6f}")
    print(f"  Std Dev:     {stats['std']:.6f}")
    print(f"  95% CI:      [{stats['lower_ci']:.6f}, {stats['upper_ci']:.6f}]")
    print(f"  Percentage:  {stats['mean']*100:.2f}% ± {stats['std']*100:.2f}%")
    print("=" * 70)

    return fig, ax, stats


def tornado_plot_ecpi(csv_path='ECPI_indicator_alpha_sum.csv', variation_pct=0.05,
                     save_path='ecpi_tornado.png', dpi=300, figsize=(10, 6)):
    """
    Create tornado plot for ECPI sensitivity analysis.
    Varies m_in_circular and m_out_circular.

    Parameters
    ----------
    csv_path : str
        Path to CSV file
    variation_pct : float
        Percentage variation (±5%)
    save_path : str
        Path to save figure
    dpi : int
        Resolution
    figsize : tuple
        Figure size
    """
    # Load base data
    base_data = load_ecpi_data_from_csv(csv_path)

    # Compute base ECPI
    base_ecpi, _, _, _ = compute_ecpi(
        base_data['m_in_circular'],
        base_data['m_in_virgin'],
        base_data['m_out_circular'],
        base_data['m_out_linear'],
        base_data['LCA_emissions_circular'],
        base_data['LCA_emissions_linear']
    )

    # Parameters to analyze
    param_names = ['m_in_circular', 'm_out_circular']

    impacts = {}

    for param in param_names:
        if param == 'm_in_circular':
            # High variation
            modified_m_in_circular_high = base_data['m_in_circular'] * (1 + variation_pct)
            ecpi_high, _, _, _ = compute_ecpi(
                modified_m_in_circular_high,
                base_data['m_in_virgin'],
                base_data['m_out_circular'],
                base_data['m_out_linear'],
                base_data['LCA_emissions_circular'],
                base_data['LCA_emissions_linear']
            )

            # Low variation
            modified_m_in_circular_low = base_data['m_in_circular'] * (1 - variation_pct)
            ecpi_low, _, _, _ = compute_ecpi(
                modified_m_in_circular_low,
                base_data['m_in_virgin'],
                base_data['m_out_circular'],
                base_data['m_out_linear'],
                base_data['LCA_emissions_circular'],
                base_data['LCA_emissions_linear']
            )

        else:  # m_out_circular
            # High variation
            modified_m_out_circular_high = base_data['m_out_circular'] * (1 + variation_pct)
            ecpi_high, _, _, _ = compute_ecpi(
                base_data['m_in_circular'],
                base_data['m_in_virgin'],
                modified_m_out_circular_high,
                base_data['m_out_linear'],
                base_data['LCA_emissions_circular'],
                base_data['LCA_emissions_linear']
            )

            # Low variation
            modified_m_out_circular_low = base_data['m_out_circular'] * (1 - variation_pct)
            ecpi_low, _, _, _ = compute_ecpi(
                base_data['m_in_circular'],
                base_data['m_in_virgin'],
                modified_m_out_circular_low,
                base_data['m_out_linear'],
                base_data['LCA_emissions_circular'],
                base_data['LCA_emissions_linear']
            )

        impacts[param] = {
            'base': base_ecpi,
            'low': ecpi_low,
            'high': ecpi_high,
            'impact_low': ecpi_low - base_ecpi,
            'impact_high': ecpi_high - base_ecpi,
            'range': abs(ecpi_high - ecpi_low)
        }

    # Sort by impact
    sorted_params = sorted(impacts.items(), key=lambda x: x[1]['range'], reverse=True)

    # Create tornado plot
    sns.set_style("whitegrid")
    sns.set_context("paper", font_scale=1.3)

    fig, ax = plt.subplots(figsize=figsize)

    # Prepare data
    param_labels = [p[0].replace('_', ' ').title() for p in sorted_params]
    low_impacts = [p[1]['impact_low'] for p in sorted_params]
    high_impacts = [p[1]['impact_high'] for p in sorted_params]

    y_pos = np.arange(len(param_labels))

    # Create horizontal bars
    bars_low = ax.barh(y_pos, low_impacts, height=0.4, align='center',
                       color='#d73027', alpha=0.8, label=f'-{variation_pct*100}%')
    bars_high = ax.barh(y_pos, high_impacts, height=0.4, align='center',
                        color='#4575b4', alpha=0.8, label=f'+{variation_pct*100}%')

    # Add vertical line at base
    ax.axvline(x=0, color='black', linestyle='-', linewidth=2)

    # Customize
    ax.set_yticks(y_pos)
    ax.set_yticklabels(param_labels)
    ax.set_xlabel('Change in ECPI', fontweight='bold', fontsize=14)
    ax.set_title(f'Tornado Plot: ECPI Mass Flow Sensitivity\n(Base ECPI: {base_ecpi:.4f}, ±{variation_pct*100}% variation)',
                 fontweight='bold', fontsize=14, pad=20)

    # Add value labels
    for i, (low, high) in enumerate(zip(low_impacts, high_impacts)):
        if abs(low) > 0.001:
            ax.text(low, i, f' {low:.4f}', ha='right' if low < 0 else 'left',
                   va='center', fontsize=10, fontweight='bold')
        if abs(high) > 0.001:
            ax.text(high, i, f' {high:.4f}', ha='left' if high > 0 else 'right',
                   va='center', fontsize=10, fontweight='bold')

    # Grid
    ax.xaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)

    # Legend
    ax.legend(loc='best', frameon=True, shadow=True, fontsize=11)

    plt.tight_layout()
    plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
    print(f"\nTornado plot saved to: {save_path}")
    plt.show()

    # Print results
    print("\n" + "=" * 70)
    print("TORNADO ANALYSIS RESULTS - ECPI")
    print("=" * 70)
    print(f"Base ECPI: {base_ecpi:.6f}")
    print(f"\nParameter impacts (±{variation_pct*100}% variation):")
    print("-" * 70)
    print(f"{'Parameter':<20} {'Low Impact':<15} {'High Impact':<15} {'Range':<15}")
    print("-" * 70)
    for param, data in sorted_params:
        print(f"{param:<20} {data['impact_low']:>14.6f} {data['impact_high']:>14.6f} {data['range']:>14.6f}")
    print("=" * 70)

    return impacts, sorted_params


if __name__ == "__main__":
    """
    ECPI Analysis with visualization and uncertainty quantification.

    MONTE CARLO PARAMETERS:
    - Distribution: Normal (Gaussian)
    - Uncertainty: 5% std dev of mass flows
    - Samples: 1000
    - Confidence: 95%
    - Parameters varied: m_in_circular, m_out_circular

    SENSITIVITY ANALYSIS PARAMETERS:
    - Variation: ±5% around base values
    - Parameters: m_in_circular, m_out_circular
    """
    # Load data from CSV
    csv_file = 'ECPI_indicator_alpha_sum.csv'

    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        print("Please ensure the CSV file is in the same directory as this script.")
    else:
        # Task 1: Compute and print results
        print("\n" + "="*70)
        print("TASK 1: COMPUTING AND PRINTING ECPI RESULTS")
        print("="*70)

        data = load_ecpi_data_from_csv(csv_file)
        ecpi, alpha_in, alpha_out, beta = compute_ecpi(
            data['m_in_circular'],
            data['m_in_virgin'],
            data['m_out_circular'],
            data['m_out_linear'],
            data['LCA_emissions_circular'],
            data['LCA_emissions_linear']
        )
        print_ecpi_results(data, ecpi, alpha_in, alpha_out, beta)

        # Task 2: Create bar plot
        print("\n" + "="*70)
        print("TASK 2: CREATING BAR PLOT")
        print("="*70)
        plot_ecpi_bar_chart(ecpi)

        # Task 3: Monte Carlo with error bars
        print("\n" + "="*70)
        print("TASK 3: MONTE CARLO SIMULATION WITH ERROR BARS")
        print("="*70)
        print("Monte Carlo Parameters:")
        print("  - Distribution: Normal (Gaussian)")
        print("  - Uncertainty: 5% std dev on mass flows")
        print("  - Samples: 1000")
        print("  - Confidence: 95%")
        print("  - Parameters: m_in_circular, m_out_circular")
        fig, ax, stats = plot_ecpi_with_error_bars(n_samples=1000, uncertainty_pct=0.05)

        # Save cumulative ECPI results to common CSV
        import csv
        cumulative_csv_path = os.path.join('..', 'cumulative_results_indicators.csv')

        # Extract ECPI stats
        ecpi_mean = stats['mean']
        ecpi_lower = stats['lower_ci']
        ecpi_upper = stats['upper_ci']

        # Check if file exists to determine if we need headers
        file_exists = os.path.exists(cumulative_csv_path)

        # Read existing data if file exists
        existing_data = {}
        if file_exists:
            with open(cumulative_csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_data[row['Indicator']] = row

        # Update with ECPI data
        existing_data['ECPI'] = {
            'Indicator': 'ECPI',
            'Mean': f'{ecpi_mean:.6f}',
            'CI_Lower': f'{ecpi_lower:.6f}',
            'CI_Upper': f'{ecpi_upper:.6f}'
        }

        # Write back to CSV
        with open(cumulative_csv_path, 'w', newline='') as f:
            fieldnames = ['Indicator', 'Mean', 'CI_Lower', 'CI_Upper']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for indicator in ['PCI', 'CI', 'CEI', 'ECPI']:
                if indicator in existing_data:
                    writer.writerow(existing_data[indicator])

        print(f"\nECPI results saved to {cumulative_csv_path}")

        # Task 4: Tornado plot for sensitivity analysis
        print("\n" + "="*70)
        print("TASK 4: TORNADO PLOT (±5% MASS FLOW VARIATION)")
        print("="*70)
        impacts, sorted_params = tornado_plot_ecpi(variation_pct=0.05)

        print("\n" + "="*70)
        print("ALL TASKS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nGenerated files:")
        print("  - ecpi_bar_chart.png (basic bar plot)")
        print("  - ecpi_with_error_bars.png (Monte Carlo error bars)")
        print("  - ecpi_tornado.png (mass flow sensitivity tornado plot)")
        print("="*70)