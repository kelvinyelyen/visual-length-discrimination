#!/usr/bin/env python3
"""
THE GENERATOR
Goal: Generate mock session data to demonstrate the 
      psychometric analysis, binomial plotting, and historical dashboard 
      features without requiring manual trial clicks.
"""
import os
import json
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from analysis import run_analysis

# Ratios tested in the experiment
RATIOS = [0.90, 0.95, 0.98, 1.0, 1.02, 1.05, 1.10]

def simulate_responses(mu, sigma, trials_per_level=10):
    """Simulates responses based on a cumulative normal psychometric function."""
    data = []
    trial_idx = 1
    
    for r in RATIOS:
        # Probability of responding "Test is longer"
        # Using cumulative normal distribution
        z = (r - mu) / sigma
        p_test_longer = 1 / (1 + np.exp(-1.7 * z))  # Clean logistic approximation of Normal CDF
        
        for _ in range(trials_per_level):
            # Roll for response
            response = 1 if random.random() < p_test_longer else 0
            
            # Keypress matching
            std_side = random.choice(['left', 'right'])
            if std_side == 'left':
                keypress = 'j' if response == 1 else 'f'
            else:
                keypress = 'f' if response == 1 else 'j'
                
            # Simulate realistic human reaction times (log-normal distribution)
            rt = float(np.random.lognormal(mean=-0.5, sigma=0.3))  # centering around 500-800ms
            
            # Correctness logic
            is_correct = 0
            if r > 1.0 and response == 1:
                is_correct = 1
            elif r < 1.0 and response == 0:
                is_correct = 1
            elif r == 1.0:
                is_correct = 1
                
            data.append({
                'trial_index': trial_idx,
                'ratio': r,
                'std_side': std_side,
                'response': response,
                'keypress': keypress,
                'rt_sec': round(rt, 4),
                'correct': is_correct
            })
            trial_idx += 1
            
    return data

def generate_demo_data():
    print("=" * 60)
    print("             DEMO DATA GENERATOR FOR VISUAL ACUITY            ")
    print("=" * 60)
    
    # Session 1: High Noise / Early Session (e.g. yesterday)
    # mu = 0.975 (left side bias), sigma = 0.08 (highly noisy/insensitive)
    t1 = datetime.now() - timedelta(days=1)
    s1_id = f"session_{t1.strftime('%Y%m%d_%H%M%S')}_SUB01"
    s1_dir = os.path.join("data", s1_id)
    os.makedirs(s1_dir, exist_ok=True)
    
    d1 = simulate_responses(mu=0.975, sigma=0.08, trials_per_level=12)
    df1 = pd.DataFrame(d1)
    df1.to_csv(os.path.join(s1_dir, "raw_data.csv"), index=False)
    
    meta1 = {
        'session_id': s1_id,
        'participant_id': 'SUB01',
        'timestamp': t1.isoformat(),
        'standard_px': 200,
        'trials_per_level': 12,
        'total_trials': len(d1),
        'completed_trials': len(d1),
        'aborted_early': False,
        'overall_accuracy': round(df1['correct'].mean(), 4),
        'mean_rt_sec': round(df1['rt_sec'].mean(), 4)
    }
    with open(os.path.join(s1_dir, "session_metadata.json"), 'w') as f:
        json.dump(meta1, f, indent=4)
        
    print(f"\n[1/2] Generated early session for SUB01: {s1_dir}")
    run_analysis(s1_dir)
    
    # Session 2: Low Noise / Trained Session (e.g. today)
    # mu = 1.002 (perfect spatial calibration), sigma = 0.04 (high acuity, twice as sensitive!)
    t2 = datetime.now()
    s2_id = f"session_{t2.strftime('%Y%m%d_%H%M%S')}_SUB01"
    s2_dir = os.path.join("data", s2_id)
    os.makedirs(s2_dir, exist_ok=True)
    
    d2 = simulate_responses(mu=1.002, sigma=0.04, trials_per_level=12)
    df2 = pd.DataFrame(d2)
    df2.to_csv(os.path.join(s2_dir, "raw_data.csv"), index=False)
    
    meta2 = {
        'session_id': s2_id,
        'participant_id': 'SUB01',
        'timestamp': t2.isoformat(),
        'standard_px': 200,
        'trials_per_level': 12,
        'total_trials': len(d2),
        'completed_trials': len(d2),
        'aborted_early': False,
        'overall_accuracy': round(df2['correct'].mean(), 4),
        'mean_rt_sec': round(df2['rt_sec'].mean(), 4)
    }
    with open(os.path.join(s2_dir, "session_metadata.json"), 'w') as f:
        json.dump(meta2, f, indent=4)
        
    print(f"\n[2/2] Generated trained session for SUB01: {s2_dir}")
    run_analysis(s2_dir)
    
    print("\n" + "=" * 60)
    print(" MOCK DATA GENERATION COMPLETE! ")
    print(" You can now run `./run.py` and view choice [4] for a real ")
    print(" timeline of learning, or check data/ for scientific reports. ")
    print("=" * 60 + "\n")

if __name__ == '__main__':
    generate_demo_data()
