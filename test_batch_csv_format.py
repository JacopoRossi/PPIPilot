"""
Test script to verify CSV format generation
"""
import pandas as pd
import os

def test_csv_format():
    """Test the CSV format with sample data"""
    
    # Create sample dataframe similar to what ppinatjson.py produces
    sample_data = [
        {
            'Name': 'Average time from Declaration SUBMITTED by EMPLOYEE to Declaration APPROVED by ADMINISTRATION',
            'Metric': 'The average of the duration between activity \'Declaration SUBMITTED by EMPLOYEE\' and activity \'Declaration APPROVED by ADMINISTRATION\'',
            'Value': '2 days, 14:16:11.181887',
            'Agrupation': ''
        },
        {
            'Name': 'Total time for Declaration APPROVED by ADMINISTRATION across all cases',
            'Metric': 'The sum of the duration between activity Declaration APPROVED by ADMINISTRATION and the end of the case',
            'Value': '76387 days, 9:04:32',
            'Agrupation': ''
        },
        {
            'Name': 'Average time for Declaration APPROVED by ADMINISTRATION grouped by org:role',
            'Metric': 'The average of the duration between activity \'Declaration APPROVED by ADMINISTRATION\' and the end of case grouped by the last value of org:role',
            'Value': 'ADMINISTRATION:NaT',
            'Agrupation': '{"ADMINISTRATION":null,"EMPLOYEE":1212853258,"MISSING":null,"SUPERVISOR":517170500,"UNDEFINED":824069599}'
        }
    ]
    
    df = pd.DataFrame(sample_data)
    
    # Test CSV generation
    output_file = "test_output.csv"
    rows_to_write = []
    
    # Add header
    rows_to_write.append("Name;Metric;Value;Agrupation;Colonna77")
    rows_to_write.append(";ERROR: computing metric {};;;")
    
    # Add data rows
    for idx, row in df.iterrows():
        name = str(row.get('Name', '')) if pd.notna(row.get('Name', '')) else ''
        metric = str(row.get('Metric', '')) if pd.notna(row.get('Metric', '')) else ''
        value = str(row.get('Value', '')) if pd.notna(row.get('Value', '')) else ''
        agrupation = str(row.get('Agrupation', '')) if pd.notna(row.get('Agrupation', '')) else ''
        
        # Clean up 'nan' strings
        if name == 'nan':
            name = ''
        if metric == 'nan':
            metric = ''
        if value == 'nan':
            value = ''
        if agrupation == 'nan':
            agrupation = ''
        
        colonna77 = 'A'
        row_str = f"{name};{metric};{value};{agrupation};{colonna77}"
        rows_to_write.append(row_str)
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        for row in rows_to_write:
            f.write(row + '\n')
    
    print(f"✅ Test CSV created: {output_file}")
    print(f"📊 Number of data rows: {len(df)}")
    print(f"📄 Total lines in CSV: {len(rows_to_write)}")
    
    # Display first few lines
    print("\n📝 First 5 lines of CSV:")
    with open(output_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i < 5:
                print(f"  {i+1}: {line.rstrip()}")
    
    # Clean up
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"\n🧹 Test file removed")

if __name__ == "__main__":
    test_csv_format()
