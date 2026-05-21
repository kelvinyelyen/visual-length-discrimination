"""
THE INSIGHT
Goal: Analyze psychophysics data to extract the Point of Subjective Equality (PSE) 
      and Just Noticeable Difference (JND) with publication-grade metrics and visuals.
"""
import os
import sys
import json
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import norm

RATIOS = [0.90, 0.95, 0.98, 1.0, 1.02, 1.05, 1.10]

def psychometric_function(x, mu, sigma):
    """Cumulative normal distribution function representing psychometric responses."""
    return norm.cdf(x, loc=mu, scale=sigma)

def find_latest_session():
    """Finds the most recently modified session folder in the data directory."""
    if not os.path.exists("data"):
        return None
    sessions = [os.path.join("data", d) for d in os.listdir("data") if os.path.isdir(os.path.join("data", d))]
    sessions = [s for s in sessions if os.path.basename(s).startswith("session_")]
    if not sessions:
        return None
    return max(sessions, key=os.path.getmtime)

def run_analysis(session_dir=None):
    """
    Performs psychometric curve fitting, computes confidence intervals,
    saves scientific plots, and auto-generates a markdown report.
    """
    print("\n" + "=" * 60)
    print("           PSYCHOMETRIC CURVE FITTING & ANALYSIS            ")
    print("=" * 60)
    
    # 1. Locate Target Data
    if not session_dir:
        session_dir = find_latest_session()
        
    if session_dir:
        csv_path = os.path.join(session_dir, "raw_data.csv")
        metadata_path = os.path.join(session_dir, "session_metadata.json")
        print(f"[Data] Targeting Session Directory: {session_dir}")
    else:
        # Fallback to root files if no session directory exists yet
        csv_path = "my_psychophysics_data.csv"
        metadata_path = None
        session_dir = "."
        print("[Data] Using default root data file.")

    if not os.path.exists(csv_path):
        print(f"[Error] Data file not found at: {csv_path}")
        print("Please run the experiment task first to generate data.")
        return None

    # 2. Load and Aggregate Data
    df = pd.read_csv(csv_path)
    
    # Compute proportions and standard errors (binomial error bars)
    summary = df.groupby('ratio')['response'].agg(['mean', 'count']).reset_index()
    summary.rename(columns={'mean': 'p_longer', 'count': 'n'}, inplace=True)
    
    # Standard Error of Binomial Proportion: SE = sqrt(p * (1-p) / n)
    # Clip probability to avoid zero standard error for 0% or 100% responses
    p_clipped = np.clip(summary['p_longer'], 0.05, 0.95)
    summary['se'] = np.sqrt(p_clipped * (1 - p_clipped) / summary['n'])

    x_data = summary['ratio'].to_numpy()
    y_data = summary['p_longer'].to_numpy()
    se_data = summary['se'].to_numpy()

    # 3. Fit Cumulative Normal Distribution (CDF)
    try:
        # Initial guess: mu = 1.0 (no bias), sigma = 0.05 (clean acuity)
        popt, pcov = curve_fit(psychometric_function, x_data, y_data, p0=[1.0, 0.05])
        pse, sigma = popt
        # JND is the distance from 50% to 75% on normal CDF: sigma * z_score(0.75)
        jnd = sigma * 0.6745
        fit_success = True
    except Exception as e:
        print(f"[Warn] Curve fitting failed ({e}). Using robust median estimators.")
        pse = np.median(df[df['response'] == 1]['ratio']) if len(df[df['response'] == 1]) > 0 else 1.0
        sigma = 0.1
        jnd = sigma * 0.6745
        fit_success = False

    # 4. Goodness of Fit (R-Squared)
    y_pred = psychometric_function(x_data, pse, sigma)
    ss_res = np.sum((y_data - y_pred) ** 2)
    ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    print(f"\n[Results] Curve Fit status: {'SUCCESS' if fit_success else 'FAILED'}")
    print(f"[Results] PSE (Bias):        {pse:.4f} (Ideal is 1.0)")
    print(f"[Results] JND (Acuity):      {jnd:.4f} (Lower is better)")
    print(f"[Results] R² Goodness:       {r_squared:.4f}")

    # 5. Scientific Matplotlib Plotting
    plt.figure(figsize=(9, 6.5), dpi=150)
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Modern cohesive theme styles
    primary_color = '#111111'
    fit_curve_color = '#d63031'
    highlight_color = '#0984e3'
    jnd_zone_color = '#2ecc71'
    
    # Plot JND Shaded Zone [PSE - JND, PSE + JND]
    plt.axvspan(pse - jnd, pse + jnd, color=jnd_zone_color, alpha=0.08, 
                label=f'JND Zone (±{jnd:.3f})')
    
    # Plot empirical data points with standard error bars
    plt.errorbar(x_data, y_data, yerr=se_data, fmt='o', color=primary_color,
                 ecolor=primary_color, elinewidth=1.5, capsize=4, ms=7,
                 label='Empirical Data (mean ± SE)', zorder=5)

    # Plot fitted psychometric curve
    x_smooth = np.linspace(0.85, 1.15, 200)
    y_smooth = psychometric_function(x_smooth, pse, sigma)
    plt.plot(x_smooth, y_smooth, '-', color=fit_curve_color, linewidth=2.5,
             label=f'Fitted Normal CDF (R² = {r_squared:.2f})')

    # Visual indicators (horizontal & vertical projection lines)
    plt.axvline(pse, color=highlight_color, linestyle='--', linewidth=1.5,
                label=f'PSE = {pse:.3f} (Bias)')
    plt.axhline(0.5, color='gray', linestyle=':', linewidth=1)
    
    # Labels and Titles
    plt.title('2AFC Visual Length Discrimination Psychometric Curve', fontsize=14, pad=15, fontweight='bold')
    plt.xlabel('Stimulus Spatial Ratio (Test / Standard)', fontsize=11, labelpad=10)
    plt.ylabel('Probability of Responding "Test is Longer"', fontsize=11, labelpad=10)
    
    # Limits & Ticks
    plt.xlim(0.87, 1.13)
    plt.ylim(-0.05, 1.05)
    plt.xticks(RATIOS)
    
    plt.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='#e2e8f0', fontsize=9.5)
    plt.tight_layout()

    # Save visualization to session directory
    curve_plot_path = os.path.join(session_dir, "psychometric_curve.png")
    plt.savefig(curve_plot_path, dpi=200)
    plt.close()
    
    print(f"[Output] Scientific plot saved: {curve_plot_path}")

    # 6. Generate Self-Contained Markdown Report
    metadata = {}
    if metadata_path and os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
            
    generate_report(session_dir, metadata, pse, jnd, r_squared, fit_success)
    
    # 7. Update Metadata JSON with calculated values
    if metadata_path and os.path.exists(metadata_path):
        metadata['pse'] = round(pse, 4)
        metadata['jnd'] = round(jnd, 4)
        metadata['r_squared'] = round(r_squared, 4)
        metadata['fit_success'] = fit_success
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=4)
            
    return pse, jnd

def generate_report(session_dir, metadata, pse, jnd, r_squared, fit_success):
    """Generates a structured, publication-grade markdown summary report of the session."""
    report_content = f"""# Psychophysics Session Analysis Report

**Session ID:** `{metadata.get('session_id', 'N/A')}`
**Participant ID:** `{metadata.get('participant_id', 'N/A')}`
**Date/Time:** `{metadata.get('timestamp', 'N/A')}`

---

## 1. Executive Summary

This automated report presents the psychophysical assessment of visual length discrimination. By applying the **Method of Constant Stimuli** under a **Two-Alternative Forced Choice (2AFC)** paradigm, we mapped the participant's sensory responses onto a cumulative normal distribution model to isolate behavioral indices of early cortical spatial coding.

| Metric | Measured Value | Ideal / Reference | Scientific Interpretation |
| :--- | :---: | :---: | :--- |
| **PSE** (Bias) | `{pse:.4f}` | `1.0000` | Point of Subjective Equality. Values < 1.0 indicate a left-stimulus bias. |
| **JND** (Sensitivity) | `{jnd:.4f}` | Lower is better | Just Noticeable Difference. Represents absolute sensory noise limit. |
| **R²** (Goodness of Fit) | `{r_squared:.4f}` | `1.0000` | Explained variance by the Gaussian Cumulative Normal model. |
| **Accuracy** (Overall) | `{metadata.get('overall_accuracy', 0.0) * 100:.2f}%` | — | Percent correct across all non-ambiguous ratios. |
| **Mean RT** (Reaction Time) | `{metadata.get('mean_rt_sec', 0.0):.3f} s` | — | Average latency to render spatial judgment. |

---

## 2. Psychometric Curve Fitting

The visualization below represents the fitted psychometric curve. Raw data points represent the empirical probability of responding "Test stimulus is longer" at each ratio level, with binomial standard error bars indicating trial-by-trial variance.

![Psychometric Curve](psychometric_curve.png)

*The shaded green zone represents the **JND Threshold Zone** ($[PSE - JND, PSE + JND]$), reflecting the spatial interval where sensory noise dominates and makes discrimination uncertain.*

---

## 3. Psychophysical Interpretations

1. **Sensory Bias (PSE = {pse:.4f}):**
   - {"The participant exhibits virtually zero spatial bias. Spatial perception is accurately calibrated with physical line length." if abs(pse - 1.0) <= 0.015 else f"The participant demonstrates a slight spatial bias of {abs(pse - 1.0) * 100:.2f}% towards the {'left' if pse < 1.0 else 'right'} side stimulus. This suggests a slight cortical imbalance or hemispheric attention bias."}

2. **Visual Resolution Limit (JND = {jnd:.4f}):**
   - A JND of `{jnd:.4f}` implies that a length difference of **`{jnd * 100:.2f}%`** is required for the visual system to distinguish the test line from the standard line with 75% accuracy. This indicates {"high spatial acuity" if jnd < 0.05 else "standard spatial acuity" if jnd < 0.09 else "high internal neural noise / low spatial sensitivity during this session"}.

3. **Speed-Accuracy Dynamics:**
   - The average decision latency of `{metadata.get('mean_rt_sec', 0.0):.3f} seconds` represents the time required to settle on a sensory decision. Portfolio analysis of reaction times can indicate whether cognitive control or fatigue influenced sensory thresholds.
"""
    report_path = os.path.join(session_dir, "report.md")
    with open(report_path, 'w') as f:
        f.write(report_content.strip())
    print(f"[Output] Automated Markdown report generated: {report_path}")

if __name__ == '__main__':
    run_analysis()