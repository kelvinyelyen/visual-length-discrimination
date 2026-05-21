#!/usr/bin/env python3
"""
THE HUBLINK
Goal: Provide a premium, interactive terminal menu to run experiments,
      analyze sessions, and track historical results.
"""
import os
import sys
import json
import glob
from datetime import datetime
import pandas as pd

# Import modular pipeline components
try:
    from task import run_experiment
    from analysis import run_analysis, find_latest_session
except ImportError:
    # Handle if run from outside the main directory
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from task import run_experiment
    from analysis import run_analysis, find_latest_session

# Visual Formatting Utilities
CLR_HEADER = '\033[95m'
CLR_BLUE = '\033[94m'
CLR_GREEN = '\033[92m'
CLR_WARNING = '\033[93m'
CLR_FAIL = '\033[91m'
CLR_END = '\033[0m'
CLR_BOLD = '\033[1m'

def print_banner():
    """Prints a clean header for the workspace."""
    print("\n" + "=" * 80)
    print("            VISUAL ACUITY & PSYCHOPHYSICS EXPERIMENTAL SYSTEM")
    print("=" * 80)

def get_menu_choice():
    """Renders menu options and captures validated inputs."""
    print(f"\n{CLR_BOLD}SELECT OPERATIONAL MODULE:{CLR_END}")
    print(f"[{CLR_GREEN}1{CLR_END}] Run New Visual Psychophysics Session")
    print(f"[{CLR_GREEN}2{CLR_END}] Run Analysis on LATEST Session")
    print(f"[{CLR_GREEN}3{CLR_END}] Select & Analyze Specific Past Session")
    print(f"[{CLR_GREEN}4{CLR_END}] View Historical Performance Dashboard")
    print(f"[{CLR_GREEN}5{CLR_END}] Exit Platform")
    
    choice = input(f"\n{CLR_BOLD}Enter selection [1-5]: {CLR_END}").strip()
    return choice

def handle_run_experiment():
    """Wraps task launch with automatic follow-up analysis prompt."""
    print(f"\n{CLR_GREEN}>>> Starting Experimental Psychophysics Window <<<{CLR_END}")
    session_dir = run_experiment()
    
    if session_dir:
        # Offer immediate curve fitting
        print(f"\n{CLR_BOLD}Session successfully recorded.{CLR_END}")
        analyze_now = input("Would you like to run the psychometric analysis curve fit now? [Y/n]: ").strip().lower()
        if analyze_now != 'n':
            run_analysis(session_dir)

def handle_analyze_latest():
    """Runs analysis directly on the most recent session folder."""
    latest = find_latest_session()
    if not latest:
        print(f"\n{CLR_FAIL}[Error] No session directories found in 'data/'. Please run a session first.{CLR_END}")
        return
    
    run_analysis(latest)

def handle_analyze_specific():
    """Displays lists of past sessions for selective manual analysis."""
    if not os.path.exists("data"):
        print(f"\n{CLR_FAIL}[Error] No session directories found.{CLR_END}")
        return
        
    sessions = [d for d in os.listdir("data") if os.path.isdir(os.path.join("data", d))]
    sessions = sorted([s for s in sessions if s.startswith("session_")], reverse=True)
    
    if not sessions:
        print(f"\n{CLR_FAIL}[Error] No session directories found.{CLR_END}")
        return
        
    print(f"\n{CLR_BOLD}AVAILABLE HISTORICAL SESSIONS:{CLR_END}")
    for idx, s in enumerate(sessions):
        print(f"[{CLR_GREEN}{idx + 1}{CLR_END}] {s}")
        
    try:
        sel = input(f"\nSelect a session number [1-{len(sessions)}]: ").strip()
        sel_idx = int(sel) - 1
        if 0 <= sel_idx < len(sessions):
            target_dir = os.path.join("data", sessions[sel_idx])
            run_analysis(target_dir)
        else:
            print(f"{CLR_FAIL}Invalid selection.{CLR_END}")
    except ValueError:
        print(f"{CLR_FAIL}Please enter a valid numeric choice.{CLR_END}")

def handle_history_dashboard():
    """
    Parses and aggregates all session JSON metadata to output a professional
    performance tracking spreadsheet-style report in the console.
    """
    if not os.path.exists("data"):
        print(f"\n{CLR_WARNING}[Info] No data directory found yet. History dashboard is empty.{CLR_END}")
        return
        
    session_paths = glob.glob(os.path.join("data", "session_*", "session_metadata.json"))
    
    if not session_paths:
        print(f"\n{CLR_WARNING}[Info] No session metadata found. Run some sessions to view history!{CLR_END}")
        return
        
    print(f"\n{CLR_HEADER}{CLR_BOLD}" + "=" * 90)
    print("                     HISTORICAL SENSORY PERFORMANCE DASHBOARD                       ")
    print("=" * 90 + f"{CLR_END}")
    
    records = []
    for path in session_paths:
        try:
            with open(path, 'r') as f:
                meta = json.load(f)
                
            # Formatting timestamp
            dt = datetime.fromisoformat(meta.get('timestamp'))
            formatted_date = dt.strftime('%Y-%m-%d %H:%M')
            
            records.append({
                'Date/Time': formatted_date,
                'Participant': meta.get('participant_id', 'N/A'),
                'Trials': f"{meta.get('completed_trials', 0)}/{meta.get('total_trials', 0)}",
                'Accuracy': f"{meta.get('overall_accuracy', 0.0) * 100:.1f}%",
                'Avg RT': f"{meta.get('mean_rt_sec', 0.0):.2f}s",
                'PSE (Bias)': f"{meta.get('pse', 1.0):.4f}" if 'pse' in meta else 'Unanalyzed',
                'JND (Acuity)': f"{meta.get('jnd', 0.0):.4f}" if 'jnd' in meta else 'Unanalyzed'
            })
        except Exception as e:
            continue
            
    # Sort chronologically by date
    df_history = pd.DataFrame(records).sort_values(by='Date/Time', ascending=False)
    
    # Render table nicely
    print(df_history.to_string(index=False))
    print(f"\n{CLR_HEADER}" + "=" * 90 + f"{CLR_END}")

def main():
    """Main execution control loop."""
    print_banner()
    
    while True:
        try:
            choice = get_menu_choice()
            if choice == '1':
                handle_run_experiment()
            elif choice == '2':
                handle_analyze_latest()
            elif choice == '3':
                handle_analyze_specific()
            elif choice == '4':
                handle_history_dashboard()
            elif choice == '5':
                print(f"\n{CLR_GREEN}Exiting Psychophysics Platform. Goodbye!{CLR_END}\n")
                break
            else:
                print(f"{CLR_FAIL}Invalid option. Please enter a number between 1 and 5.{CLR_END}")
        except KeyboardInterrupt:
            print(f"\n\n{CLR_WARNING}Session interrupted. Exiting...{CLR_END}\n")
            break

if __name__ == '__main__':
    main()
