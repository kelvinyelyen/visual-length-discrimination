# Visual Length Discrimination

> A Two-Alternative Forced Choice (2AFC) psychophysics instrument for measuring internal visual noise and Just Noticeable Difference (JND).

## Overview
While theoretical models compute the internal dynamics of the visual cortex, this project measures the behavioral output of those systems. It utilizes the Method of Constant Stimuli to determine the quantitative threshold of internal visual noise required to disrupt spatial perception.

## The Instrument
The experiment (`experiment.py`) operates under strict visual constraints to isolate early cortical processing and prevent saccadic scanning.

* **Paradigm:** 2AFC (Two-Alternative Forced Choice)
* **Method:** Constant Stimuli (7 fixed spatial ratios)
* **Exposure:** 400ms stimulus flash
* **Control:** Randomized spatial presentation to eliminate hemispheric bias

## The Analysis
The analysis module (`analysis.py`) translates binary behavioral responses into a continuous model of perception by fitting a psychometric curve to the data. It extracts two core metrics:

1. **Point of Subjective Equality (PSE):** The spatial ratio at which the visual system is entirely guessing ($P = 0.5$).
2. **Just Noticeable Difference (JND):** The standard deviation of the curve, representing the absolute threshold of internal visual noise.
