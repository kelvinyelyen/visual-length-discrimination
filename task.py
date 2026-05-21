"""
THE INSTRUMENT
Goal: Measure the internal noise in your visual cortex.
Method: Constant Stimuli (randomized fixed levels) with Reaction Time tracking.
"""
import os
import sys
import json
import random
from datetime import datetime
from psychopy import visual, core, event
import pandas as pd

# --- PARAMETERS & CONSTANTS ---
STANDARD_PX = 200 
RATIOS = [0.90, 0.95, 0.98, 1.0, 1.02, 1.05, 1.10]

def run_experiment(participant=None, trials_per_level=None):
    """
    Runs the 2AFC visual length discrimination experiment.
    Tracks responses, correctness, and reaction times.
    """
    print("\n" + "=" * 60)
    print("       VISUAL LENGTH DISCRIMINATION PSYCHOPHYSICS TASK       ")
    print("=" * 60)
    
    # 1. Configuration & Session Init
    if not participant:
        participant = input("Enter Participant ID (e.g. SUB01, initials): ").strip()
        if not participant:
            participant = "anonymous"
            
    if not trials_per_level:
        try:
            reps_input = input("Enter trials per level (default 10, total 70): ").strip()
            trials_per_level = int(reps_input) if reps_input else 10
        except ValueError:
            trials_per_level = 10
            print("Invalid input. Defaulting to 10 trials per level.")

    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{participant}"
    session_dir = os.path.join("data", session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    print(f"\n[Init] Directory created: {session_dir}")
    print("[Init] Initializing visual stimulus window...")
    
    # 2. Window & Stimuli Setup
    # Non-fullscreen window for ease of development/testing, but can be made full screen
    win = visual.Window([1000, 600], color=[-1, -1, -1], units='pix', fullscr=False) 
    
    # Create the left/right stimulus lines and standard fixation cross
    line_L = visual.Line(win, start=(-150, 0), end=(-50, 0), lineWidth=5, lineColor='white')
    line_R = visual.Line(win, start=(50, 0), end=(150, 0), lineWidth=5, lineColor='white')
    fixation = visual.TextStim(win, text='+', color='grey', height=30)
    
    # 3. Generate Design Matrix (Trial List)
    trials = []
    for r in RATIOS:
        for i in range(trials_per_level):
            trials.append({
                'ratio': r, 
                'std_side': random.choice(['left', 'right'])
            })
    random.shuffle(trials) 
    
    # 4. Instructions Screen
    instr_text = (
        "VISUAL LENGTH DISCRIMINATION\n\n"
        "Instructions:\n"
        "A fixation cross (+) will appear. Keep your eyes on it.\n"
        "Two white lines will flash briefly on either side.\n"
        "Determine which line is LONGER.\n\n"
        "Controls:\n"
        "Press 'F' key if the LEFT line was longer.\n"
        "Press 'J' key if the RIGHT line was longer.\n"
        "Press 'ESC' key at any time to exit early.\n\n"
        "Press SPACE to start the experiment."
    )
    visual.TextStim(win, text=instr_text, color='white', height=18, wrapWidth=800).draw()
    win.flip()
    
    keys = event.waitKeys(keyList=['space', 'escape'])
    if 'escape' in keys:
        win.close()
        print("[Abort] Experiment cancelled before start.")
        return None
        
    # 5. Main Experimental Loop
    data = []
    aborted = False
    
    for idx, t in enumerate(trials):
        # Graceful check between trials
        if event.getKeys(keyList=['escape']):
            aborted = True
            break
            
        # Define line geometry for this trial
        std_len = STANDARD_PX
        test_len = STANDARD_PX * t['ratio']
        
        # Side assignment
        if t['std_side'] == 'left':
            len_L, len_R = std_len, test_len
        else:
            len_L, len_R = test_len, std_len
            
        # Draw and center lines relative to their display fields (-250 and +250 px)
        line_L.start, line_L.end = (-250 - len_L/2, 0), (-250 + len_L/2, 0)
        line_R.start, line_R.end = ( 250 - len_R/2, 0), ( 250 + len_R/2, 0)
        
        # A. Pre-stimulus Fixation (Reset visual attention)
        fixation.draw()
        win.flip()
        core.wait(0.5)
        
        # B. Stimulus Flash (400ms exposure prevents saccadic scanning)
        line_L.draw()
        line_R.draw()
        fixation.draw()
        win.flip()
        
        # Start RT clock precisely at stimulus onset
        rt_clock = core.Clock()
        
        core.wait(0.4)
        
        # C. Post-stimulus Blank (Wait for response)
        fixation.draw()
        win.flip()
        
        # D. Get Response and Latency
        keys = event.waitKeys(keyList=['f', 'j', 'escape'])
        rt = rt_clock.getTime()
        
        if 'escape' in keys:
            aborted = True
            break
            
        resp = keys[0]
        
        # E. Performance Logic
        # Was the TEST stimulus perceived as longer? (1 = Yes, 0 = No)
        perceived_test_longer = 0
        if t['std_side'] == 'left' and resp == 'j': perceived_test_longer = 1
        if t['std_side'] == 'right' and resp == 'f': perceived_test_longer = 1
        
        # Accuracy check (objective correctness)
        is_correct = 0
        if t['ratio'] > 1.0 and perceived_test_longer == 1:
            is_correct = 1
        elif t['ratio'] < 1.0 and perceived_test_longer == 0:
            is_correct = 1
        elif t['ratio'] == 1.0:
            is_correct = 1  # 50/50 baseline
            
        data.append({
            'trial_index': idx + 1,
            'ratio': t['ratio'],
            'std_side': t['std_side'],
            'response': perceived_test_longer,
            'keypress': resp,
            'rt_sec': round(rt, 4),
            'correct': is_correct
        })
        
    win.close()
    
    # 6. Data Saving & Metadata Generation
    if len(data) == 0:
        print("[Abort] No trials completed. Session data not saved.")
        return None
        
    df_data = pd.DataFrame(data)
    raw_csv_path = os.path.join(session_dir, "raw_data.csv")
    df_data.to_csv(raw_csv_path, index=False)
    
    # Save session metadata
    metadata = {
        'session_id': session_id,
        'participant_id': participant,
        'timestamp': datetime.now().isoformat(),
        'standard_px': STANDARD_PX,
        'trials_per_level': trials_per_level,
        'total_trials': len(trials),
        'completed_trials': len(data),
        'aborted_early': aborted,
        'overall_accuracy': round(df_data['correct'].mean(), 4),
        'mean_rt_sec': round(df_data['rt_sec'].mean(), 4)
    }
    
    metadata_path = os.path.join(session_dir, "session_metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)
        
    print("\n" + "=" * 60)
    print("                     SESSION SUMMARY                        ")
    print("=" * 60)
    print(f"Status:       {'ABORTED EARLY' if aborted else 'FULLY COMPLETED'}")
    print(f"Directory:    {session_dir}")
    print(f"Trials Done:  {len(data)} / {len(trials)}")
    print(f"Accuracy:     {metadata['overall_accuracy'] * 100:.2f}%")
    print(f"Avg Latency:  {metadata['mean_rt_sec']:.3f} seconds")
    print("=" * 60 + "\n")
    
    return session_dir

if __name__ == '__main__':
    run_experiment()