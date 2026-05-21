# Visual Length Discrimination & Sensory Noise Modeling

> A Two-Alternative Forced Choice (2AFC) psychophysics platform designed to quantify visual sensory noise, spatial discrimination limits, and perceptual bias in the human visual cortex.

---

## 1. Scientific Background & Paradigm

Spatial length discrimination is a fundamental probe of the early visual pathway. The receptive fields in the primary visual cortex (V1) and secondary visual cortex (V2) act as spatial filters, extracting local orientation, size, and boundary signals. However, visual perception is not a perfect transmission of physical inputs; it is corrupted by **internal neural noise** (variability in neural firing rates).

To isolate this internal noise behavioral output, this project implements a rigorous visual psychophysics instrument:

### The Two-Alternative Forced Choice (2AFC) Paradigm
In a 2AFC paradigm, a standard stimulus (200 pixels) and a variable test stimulus ($200 \times \text{Ratio}$) are presented simultaneously. The participant is forced to make a binary judgment: *"Which stimulus is longer?"*
- **Why 2AFC?** Unlike single-stimulus detection tasks, 2AFC controls for shifting subjective decision criteria (e.g., a participant being overly conservative or liberal in reporting "longer"), isolating pure sensory performance.

### Spatial and Temporal Constraints
- **400ms Flash Exposure:** Stimuli are flashed on screen for exactly 400 milliseconds. This temporal window is critical: it is shorter than the average latency to plan and execute a voluntary eye movement (saccade). This prevents the participant from physically "scanning" or using eye movements as a physical ruler, forcing the visual cortex to rely solely on parallel spatial filters.
- **Hemispheric Balance:** Standard and test stimuli are randomly mapped to the left or right hemispheres on a trial-by-trial basis, canceling out motor response biases (e.g., right-hand dominance) or hemispheric attentional asymmetry.

---

## 2. Mathematical Modeling of Perception

The brain's sensory decision-making is modeled as a cumulative probability curve. If internal neural noise is normally distributed, the probability $P$ of a participant responding that the **Test** stimulus is longer than the **Standard** stimulus as a function of the spatial ratio $x$ is modeled using the **Cumulative Distribution Function (CDF)** of a Gaussian distribution:

$$P(\text{Test} > \text{Standard} \mid x) = \Phi\left(\frac{x - \mu}{\sigma}\right) = \frac{1}{\sqrt{2\pi}\sigma} \int_{-\infty}^{x} e^{-\frac{(t-\mu)^2}{2\sigma^2}} dt$$

Where:
* **$\mu$ (Point of Subjective Equality - PSE):** The ratio $x$ at which the participant responds "Test is longer" exactly 50% of the time ($P = 0.5$).
  - **No Bias ($\mu = 1.0$):** Perceptual reality matches physical reality.
  - **Left/Right Bias ($\mu \neq 1.0$):** Indicates a constant perceptual distortion (e.g., standard line is consistently perceived as longer or shorter due to attention or hemispheric neglect).
* **$\sigma$ (Sensory Standard Deviation):** The slope of the psychometric curve, representing the magnitude of internal visual noise.
* **Just Noticeable Difference (JND):** The absolute sensory threshold, defined as the stimulus change required to elevate discrimination performance from chance (50%) to 75% accuracy. In terms of the normal CDF:
  
$$JND = \sigma \cdot \Phi^{-1}(0.75) \approx 0.6745 \cdot \sigma$$

---

## 3. Directory Structure & Architecture

The codebase is structured as a modular package as follows:

```
visual-length-discrimination/
│
├── data/                                 # Central database for all session records
│   └── session_YYYYMMDD_HHMMSS_ID/       # Dynamic session isolated folder
│       ├── raw_data.csv                  # Raw trial responses with reaction times (RT)
│       ├── session_metadata.json         # Session parameters, accuracy, RT, and fit results
│       ├── psychometric_curve.png        # High-DPI scientific CDF plot with JND zone
│       └── report.md                     # Auto-generated scientific markdown report
│
├── venv/                                 # Isolated Python 3.11 virtual environment
├── task.py                               # PsychoPy psychophysical experiment routine
├── analysis.py                           # Scientific analysis, CDF fitting, and error mapping
├── run.py                                # Main interactive terminal platform hub
├── requirements.txt                      # Package dependencies
└── README.md                             # Project documentation (this file)
```

---

## 4. Feature Highlights

### Automated Reporting
For every session completed, the system automatically runs a curve-fitting pipeline to output a structured scientific report inside the session folder, embedding a custom high-resolution plot and contextual scientific interpretations based on measured thresholds.

### Binomial Confidence Interval Mapping
Instead of raw points, the analysis pipeline computes the **Standard Error of Binomial Proportions** for each ratio's empirical data:
$$SE = \sqrt{\frac{p(1-p)}{n}}$$
These are mapped on the plot as vertical error bars, visualizing confidence levels across different difficulty intervals.

### Latency (Reaction Time) Tracking
Tracks precise response latency (in milliseconds) from visual onset, opening up research capabilities for speed-accuracy trade-off analysis.

---

## 5. Getting Started & Usage

### Setup Environment
This package requires Python 3.11 for optimal PsychoPy compatibility. Install the platform dependencies:
```bash
# Create venv and activate
python3.11 -m venv venv
source venv/bin/activate

# Install required science & rendering wheels
pip install -r requirements.txt
pip install json_tricks arabic_reshaper freetype-py glfw psychtoolbox
```

### Launching the Hub
Run the interactive console dashboard to access the entire suite of features:
```bash
./run.py
```
From the interactive CLI menu, you can:
1. **Launch a New Session:** Prompts for participant details and launches the PsychoPy window.
2. **Analyze Latest:** Fits the psychometric curve to the most recent run instantly.
3. **Select History:** Re-analyze any specific historical run from the archive.
4. **Historical Dashboard:** View a spreadsheet-style timeline of your accuracy, reaction times, PSE, and JND improvements across days.
