# PPIPilot - Batch Execution Mode

## Overview
This document describes the batch execution mode for PPIPilot, which allows automated execution of PPI analysis for all activities in a log, with multiple runs per activity.

## Features

### 🔄 Automated Batch Processing
- **10 runs per activity**: Each activity in the log is analyzed 10 times
- **No display output**: Results are saved directly to CSV files without UI display
- **Automatic error correction**: Built-in error correction mechanism (Level 1 and Level 2)
- **Progress tracking**: Real-time progress bar and status updates

### 📊 Output Format
Results are saved in CSV format with semicolon (`;`) separator:

```
Name;Metric;Value;Agrupation;Colonna77
;ERROR: computing metric {};;;
Average time from Declaration SUBMITTED by EMPLOYEE to Declaration APPROVED by ADMINISTRATION;The average of the duration between activity 'Declaration SUBMITTED by EMPLOYEE' and activity 'Declaration APPROVED by ADMINISTRATION';2 days, 14:16:11.181887;;A
Total time for Declaration APPROVED by ADMINISTRATION across all cases;The sum of the duration between activity Declaration APPROVED by ADMINISTRATION and the end of the case;76387 days, 9:04:32;;B
;RUN 3: No valid PPIs generated (2 errors);;;
;RUN 5: No valid PPIs generated (1 errors);;;
...
```

**Note**: CSV files are created for **all runs**, even when no valid PPIs are generated. Failed runs are tracked with comment lines showing the run number and error count.

### 📁 File Organization
Results are organized by:
- **Category** (time/occurrency)
- **Timestamp** (run date and time)
- **Activity name** (one CSV file per activity)

Example structure:
```
quantitative_assessment/
└── batch_results/
    └── time/
        └── results_run_20241110_115430/
            ├── Declaration_SUBMITTED_by_EMPLOYEE.csv
            ├── Declaration_APPROVED_by_ADMINISTRATION.csv
            ├── Declaration_FINAL_APPROVED_by_SUPERVISOR.csv
            └── ...
```

## Usage

### 1. Start the Batch Interface
```bash
streamlit run interface_batch.py
```

### 2. Configure the Analysis
1. **OpenAI API Key**: Enter your OpenAI API key
2. **Upload XES File**: Select your event log file
3. **Description**: Provide a description of the process
4. **Organizational Goal**: Specify the organizational goal
5. **Category**: Choose between "time" or "occurrency"
6. **Output Folder**: Specify where to save results (default: `quantitative_assessment/batch_results`)

### 3. Execute Batch Analysis
Click the **"▶️ Start Batch Execution"** button to begin.

### 4. Monitor Progress
- **Progress Bar**: Shows overall completion percentage
- **Status Text**: Displays current activity and run number
- **Activity Summaries**: Shows metrics for each completed activity
  - Total PPIs generated
  - Total errors encountered
  - Success rate
  - Average PPIs per run

### 5. Review Results
After completion:
- **Final Summary Table**: Overview of all activities
- **CSV Files**: One file per activity in the output folder
- **Console Logs**: Detailed execution logs in the terminal

## Configuration Parameters

### In `interface_batch.py`:
```python
NUM_RUNS_PER_ACTIVITY = 10  # Number of runs for each activity
MAX_LEVEL1_ITERATIONS = 2   # Maximum Level 1 correction iterations
MAX_LEVEL2_ITERATIONS = 2   # Maximum Level 2 correction iterations
```

You can modify these parameters to adjust:
- Number of runs per activity
- Error correction aggressiveness

## CSV Format Details

### Columns:
1. **Name**: PPI name
2. **Metric**: Description of what the PPI measures
3. **Value**: Calculated value (time duration, percentage, count, etc.)
4. **Agrupation**: JSON string with grouped data (if applicable)
5. **Colonna77**: Classification column (A, B, C, D, etc.)

### Special Rows:
- **Header Row**: Column names
- **Error Row**: Placeholder for error information (`;ERROR: computing metric {};;;`)
- **Failed Run Rows**: Track runs with no valid PPIs (`;RUN X: No valid PPIs generated (Y errors);;;`)

### Value Formats:
- **Time durations**: `X days, HH:MM:SS.microseconds`
- **Grouped values**: `group_name:value`
- **Numeric values**: Standard numeric format
- **JSON aggregations**: `{"key1": value1, "key2": value2, ...}`

## Differences from Standard Interface

| Feature | Standard Interface | Batch Interface |
|---------|-------------------|-----------------|
| Display | Interactive tables | No display |
| Execution | Single activity | All activities |
| Runs | 1 per execution | 10 per activity |
| Output | UI display | CSV files |
| Progress | Spinner | Progress bar + metrics |
| Activity Selection | Manual | Automatic (all) |

## Error Handling

### Automatic Error Correction
The batch mode includes the same error correction mechanism as the standard interface:
1. **Level 1**: JSON re-translation (up to 2 iterations)
2. **Level 2**: Error-specific correction (up to 2 iterations)

### Error Tracking
- Errors are counted and reported in activity summaries
- Failed runs are marked with ⚠️ or ❌ status
- Success rate is calculated for each activity

## Performance Considerations

### Execution Time
- **Per activity**: ~2-5 minutes (depending on log size and complexity)
- **Total time**: `num_activities × 10 runs × avg_time_per_run`
- **Example**: 20 activities × 10 runs × 3 min = ~10 hours

### Recommendations
- Run batch mode overnight or during off-hours
- Monitor the first few activities to ensure correct configuration
- Check available disk space for output files
- Ensure stable internet connection for OpenAI API calls

## Troubleshooting

### Issue: No PPIs Generated
**Possible causes:**
- Invalid JSON structure
- Activity not found in log
- OpenAI API errors

**Solutions:**
- Check console logs for detailed error messages
- Verify activity names match exactly with log
- Check OpenAI API key and quota

### Issue: High Error Rate
**Possible causes:**
- Complex PPI definitions
- Insufficient log data
- Attribute mismatches

**Solutions:**
- Review generated JSON files
- Simplify organizational goal description
- Verify log attributes are correctly identified

### Issue: Slow Execution
**Possible causes:**
- Large log file
- Complex PPIs
- OpenAI API rate limits

**Solutions:**
- Reduce `NUM_RUNS_PER_ACTIVITY`
- Use smaller log sample for testing
- Check OpenAI API rate limits

## Output Analysis

### Recommended Workflow
1. **Check Success Rates**: Identify activities with low success rates
2. **Review CSV Files**: Examine generated PPIs for quality
3. **Compare Runs**: Analyze variation across 10 runs
4. **Aggregate Results**: Combine data for statistical analysis

### Statistical Analysis
With 10 runs per activity, you can:
- Calculate mean and standard deviation of PPI values
- Identify outliers and anomalies
- Assess consistency of PPI generation
- Evaluate reliability of different PPI types

## Example Usage

```bash
# 1. Start the interface
streamlit run interface_batch.py

# 2. In the browser:
#    - Enter OpenAI API key
#    - Upload: Domestic_Declarations.xes
#    - Description: "Employee expense declaration process"
#    - Goal: "Minimize approval time and maximize compliance"
#    - Category: "time"
#    - Output: "quantitative_assessment/batch_results"
#    - Click "Start Batch Execution"

# 3. Wait for completion (monitor progress)

# 4. Results will be in:
#    quantitative_assessment/batch_results/time/results_run_YYYYMMDD_HHMMSS/
```

## Notes

- The batch interface is designed for quantitative assessment and research purposes
- Each run is independent and uses the same configuration
- Results may vary slightly between runs due to OpenAI's non-deterministic nature
- CSV files can be easily imported into Excel, Python, R, or other analysis tools
- The format is compatible with the existing PPIPilot result structure

## Support

For issues or questions:
1. Check console logs for detailed error messages
2. Review the `TESTING_GUIDE.md` for debugging tips
3. Verify configuration parameters
4. Check OpenAI API status and quota
