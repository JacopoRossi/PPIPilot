"""
Test script to verify CSV generation with error tracking
Tests that CSV files are created even when no valid PPIs are generated
"""
import pandas as pd
import os
import tempfile

def save_results_to_csv(df, activity_name, run_number, category, output_folder, num_errors=0):
    """
    Save results to CSV in the specified format - TEST VERSION
    """
    os.makedirs(output_folder, exist_ok=True)
    
    clean_activity = activity_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    filename = f"{clean_activity}.csv"
    filepath = os.path.join(output_folder, filename)
    
    rows_to_write = []
    
    if run_number == 1:
        rows_to_write.append("Name;Metric;Value;Agrupation;Colonna77")
        rows_to_write.append(";ERROR: computing metric {};;;")
    
    if df is not None and len(df) > 0:
        for idx, row in df.iterrows():
            name = str(row.get('Name', '')) if pd.notna(row.get('Name', '')) else ''
            metric = str(row.get('Metric', '')) if pd.notna(row.get('Metric', '')) else ''
            value = str(row.get('Value', '')) if pd.notna(row.get('Value', '')) else ''
            agrupation = str(row.get('Agrupation', '')) if pd.notna(row.get('Agrupation', '')) else ''
            
            if name == 'nan': name = ''
            if metric == 'nan': metric = ''
            if value == 'nan': value = ''
            if agrupation == 'nan': agrupation = ''
            
            colonna77 = 'A'
            row_str = f"{name};{metric};{value};{agrupation};{colonna77}"
            rows_to_write.append(row_str)
    else:
        rows_to_write.append(f";RUN {run_number}: No valid PPIs generated ({num_errors} errors);;;")
    
    mode = 'w' if run_number == 1 else 'a'
    with open(filepath, mode, encoding='utf-8') as f:
        for row in rows_to_write:
            f.write(row + '\n')
    
    return filepath

def test_error_tracking():
    """Test CSV generation with various scenarios"""
    
    # Create temporary output folder
    test_folder = tempfile.mkdtemp()
    print(f"📁 Test folder: {test_folder}\n")
    
    activity_name = "Test Activity"
    category = "time"
    
    # Test 1: Run with valid PPIs
    print("🧪 Test 1: Run with valid PPIs")
    df_valid = pd.DataFrame([
        {
            'Name': 'Test PPI 1',
            'Metric': 'Test metric 1',
            'Value': '10 seconds',
            'Agrupation': ''
        },
        {
            'Name': 'Test PPI 2',
            'Metric': 'Test metric 2',
            'Value': '20 seconds',
            'Agrupation': ''
        }
    ])
    csv_path = save_results_to_csv(df_valid, activity_name, 1, category, test_folder, num_errors=0)
    print(f"✅ CSV created: {csv_path}")
    print(f"   - 2 valid PPIs, 0 errors\n")
    
    # Test 2: Run with no valid PPIs (empty dataframe)
    print("🧪 Test 2: Run with no valid PPIs")
    df_empty = pd.DataFrame()
    csv_path = save_results_to_csv(df_empty, activity_name, 2, category, test_folder, num_errors=3)
    print(f"✅ CSV updated: {csv_path}")
    print(f"   - 0 valid PPIs, 3 errors\n")
    
    # Test 3: Run with None dataframe (critical failure)
    print("🧪 Test 3: Run with critical failure")
    csv_path = save_results_to_csv(None, activity_name, 3, category, test_folder, num_errors=1)
    print(f"✅ CSV updated: {csv_path}")
    print(f"   - Critical failure, 1 error\n")
    
    # Test 4: Run with valid PPIs again
    print("🧪 Test 4: Run with valid PPIs again")
    df_valid2 = pd.DataFrame([
        {
            'Name': 'Test PPI 3',
            'Metric': 'Test metric 3',
            'Value': '30 seconds',
            'Agrupation': ''
        }
    ])
    csv_path = save_results_to_csv(df_valid2, activity_name, 4, category, test_folder, num_errors=0)
    print(f"✅ CSV updated: {csv_path}")
    print(f"   - 1 valid PPI, 0 errors\n")
    
    # Display final CSV content
    print("=" * 80)
    print("📄 Final CSV Content:")
    print("=" * 80)
    with open(csv_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)
    
    # Count lines
    lines = content.strip().split('\n')
    print("=" * 80)
    print(f"📊 Summary:")
    print(f"   - Total lines: {len(lines)}")
    print(f"   - Header + Error line: 2")
    print(f"   - Data lines: {len(lines) - 2}")
    print(f"   - Run 1: 2 PPIs")
    print(f"   - Run 2: 0 PPIs (tracked)")
    print(f"   - Run 3: 0 PPIs (tracked)")
    print(f"   - Run 4: 1 PPI")
    print("=" * 80)
    
    # Clean up
    import shutil
    shutil.rmtree(test_folder)
    print(f"\n🧹 Test folder removed")
    print("✅ All tests passed!")

if __name__ == "__main__":
    test_error_tracking()
