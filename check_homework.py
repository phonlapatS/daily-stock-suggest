"""
ตรวจการบ้านวันศุกร์ที่ผ่านมา
"""
import pandas as pd
from datetime import datetime, timedelta
from core.performance import verify_forecast
from tvDatafeed import TvDatafeed

print("="*80)
print("Check Homework: Verify forecasts from Friday")
print("="*80)

# Load performance log
log_file = "logs/performance_log.csv"
try:
    df = pd.read_csv(log_file)
    print(f"\nLoaded {len(df)} forecasts from log file")
    
    # Show pending forecasts
    today = datetime.now().strftime('%Y-%m-%d')
    pending = df[(df['actual'] == 'PENDING') & (df['target_date'] <= today)]
    
    print(f"\nPending forecasts (target_date <= {today}): {len(pending)}")
    if not pending.empty:
        print("\nPending forecasts:")
        print(pending[['target_date', 'symbol', 'forecast', 'prob']].to_string(index=False))
    
    # Show verified forecasts from last week
    last_friday = datetime.now() - timedelta(days=(datetime.now().weekday() + 3) % 7)
    if last_friday.weekday() != 4:  # If not Friday, find last Friday
        days_since_friday = (datetime.now().weekday() - 4) % 7
        if days_since_friday == 0:
            days_since_friday = 7
        last_friday = datetime.now() - timedelta(days=days_since_friday)
    
    last_friday_str = last_friday.strftime('%Y-%m-%d')
    print(f"\nLast Friday: {last_friday_str}")
    
    friday_forecasts = df[df['scan_date'] == last_friday_str]
    print(f"\nForecasts from {last_friday_str}: {len(friday_forecasts)}")
    if not friday_forecasts.empty:
        print(friday_forecasts[['symbol', 'forecast', 'prob', 'actual', 'correct']].to_string(index=False))
    
    # Verify pending forecasts
    print("\n" + "="*80)
    print("Verifying pending forecasts...")
    print("="*80)
    
    try:
        tv = TvDatafeed()
        result = verify_forecast(tv=tv)
        
        if result:
            verified = result.get('verified', 0)
            correct = result.get('correct', 0)
            incorrect = result.get('incorrect', 0)
            
            if verified > 0:
                accuracy = (correct / verified * 100) if verified > 0 else 0
                print(f"\nResults:")
                print(f"  Verified: {verified} forecasts")
                print(f"  Correct: {correct}")
                print(f"  Incorrect: {incorrect}")
                print(f"  Accuracy: {accuracy:.1f}%")
            else:
                print("\nNo pending forecasts to verify")
    except Exception as e:
        print(f"\nError verifying: {e}")
    
    # Show summary
    verified_all = df[df['actual'] != 'PENDING']
    if not verified_all.empty:
        correct_all = verified_all[verified_all['correct'] == 1]
        accuracy_all = (len(correct_all) / len(verified_all) * 100) if len(verified_all) > 0 else 0
        print(f"\n" + "="*80)
        print("Overall Summary:")
        print(f"  Total verified: {len(verified_all)}")
        print(f"  Correct: {len(correct_all)}")
        print(f"  Accuracy: {accuracy_all:.1f}%")
        print("="*80)
    
except FileNotFoundError:
    print(f"\nError: {log_file} not found")
    print("No forecasts to check")
except Exception as e:
    print(f"\nError: {e}")

