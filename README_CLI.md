# PPIPilot - Batch Execution CLI Mode

## 📋 Overview

`interface_batch_cli.py` allows you to run PPIPilot batch analysis directly from the command line without any GUI. Perfect for:
- ✅ **Automated testing** - Run tests easily with different configurations
- ✅ **CI/CD pipelines** - Integrate into automated workflows
- ✅ **Batch processing** - Process multiple logs sequentially
- ✅ **Remote execution** - Run on servers without display

## 🚀 Quick Start

### 1. Create Configuration File

Copy the template and modify it with your settings:

```bash
cp config_batch_template.json config_batch.json
```

Edit `config_batch.json` with your parameters:

```json
{
  "llm_provider": "openai",
  "llm_model": "gpt-4-0125-preview",
  "api_key": "sk-your-api-key-here",
  "xes_file_path": "logs/my_process.xes",
  "description": "Employee declaration process",
  "goal": "Reduce processing time",
  "ppi_category": "time",
  "output_folder": "quantitative_assessment/batch_results",
  "num_runs_per_activity": 10,
  "activities": ["all"],
  "max_level1_iterations": 2,
  "max_level2_iterations": 2,
  "save_debug_logs": false
}
```

### 2. Run the Analysis

```bash
python interface_batch_cli.py config_batch.json
```

Or using the `--config` flag:

```bash
python interface_batch_cli.py --config config_batch.json
```

### 3. View Results

Results are saved in the output folder with the following structure:

```
quantitative_assessment/batch_results/
└── time/
    └── results_run_20241116_214530/
        ├── execution_log_20241116_214530.txt
        ├── summary.csv
        ├── Activity_1/
        │   ├── run_01_iteration_01_withoutErrors.csv
        │   ├── run_01_iteration_01_withErrors.csv
        │   ├── run_02_iteration_01_withoutErrors.csv
        │   └── ...
        └── Activity_2/
            └── ...
```

## 📖 Configuration Parameters

### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `llm_provider` | string | LLM provider name | `"openai"`, `"anthropic"`, `"ollama"` |
| `llm_model` | string | Model name | `"gpt-4-0125-preview"` |
| `api_key` | string | API key for the LLM provider | `"sk-..."` |
| `xes_file_path` | string | Path to XES event log file | `"logs/process.xes"` |
| `ppi_category` | string | Type of PPIs to generate | `"time"`, `"occurrency"`, `"both"` |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `description` | string | `""` | Process description |
| `goal` | string | `""` | Organizational goal |
| `output_folder` | string | `"quantitative_assessment/batch_results"` | Output directory |
| `num_runs_per_activity` | integer | `10` | Number of runs per activity |
| `activities` | array | `["all"]` | Activities to analyze |
| `max_level1_iterations` | integer | `2` | Max Level 1 iterations |
| `max_level2_iterations` | integer | `2` | Max Level 2 iterations |
| `save_debug_logs` | boolean | `false` | Save debug logs |

## 🎯 Usage Examples

### Example 1: Analyze All Activities (Time PPIs)

```json
{
  "llm_provider": "openai",
  "llm_model": "gpt-4-0125-preview",
  "api_key": "sk-...",
  "xes_file_path": "logs/declarations.xes",
  "description": "Employee declaration process",
  "goal": "Reduce processing time",
  "ppi_category": "time",
  "num_runs_per_activity": 10,
  "activities": ["all"]
}
```

```bash
python interface_batch_cli.py config_time.json
```

### Example 2: Analyze Specific Activities (Occurrency PPIs)

```json
{
  "llm_provider": "openai",
  "llm_model": "gpt-4-0125-preview",
  "api_key": "sk-...",
  "xes_file_path": "logs/declarations.xes",
  "ppi_category": "occurrency",
  "num_runs_per_activity": 5,
  "activities": [
    "Declaration SUBMITTED by EMPLOYEE",
    "Declaration APPROVED by SUPERVISOR"
  ]
}
```

```bash
python interface_batch_cli.py config_occurrency.json
```

### Example 3: Quick Test with Debug Logs

```json
{
  "llm_provider": "openai",
  "llm_model": "gpt-4-0125-preview",
  "api_key": "sk-...",
  "xes_file_path": "logs/test.xes",
  "ppi_category": "time",
  "num_runs_per_activity": 2,
  "activities": ["Declaration SUBMITTED by EMPLOYEE"],
  "save_debug_logs": true
}
```

```bash
python interface_batch_cli.py config_test.json
```

### Example 4: Multiple Configurations in Sequence

Create multiple config files and run them sequentially:

```bash
# Run time analysis
python interface_batch_cli.py config_time.json

# Run occurrency analysis
python interface_batch_cli.py config_occurrency.json

# Run both analysis
python interface_batch_cli.py config_both.json
```

Or create a batch script:

**Windows (run_all.bat):**
```batch
@echo off
echo Running Time Analysis...
python interface_batch_cli.py config_time.json
if %errorlevel% neq 0 exit /b %errorlevel%

echo Running Occurrency Analysis...
python interface_batch_cli.py config_occurrency.json
if %errorlevel% neq 0 exit /b %errorlevel%

echo All analyses completed!
```

**Linux/Mac (run_all.sh):**
```bash
#!/bin/bash
set -e

echo "Running Time Analysis..."
python interface_batch_cli.py config_time.json

echo "Running Occurrency Analysis..."
python interface_batch_cli.py config_occurrency.json

echo "All analyses completed!"
```

## 📊 Output Files

### Execution Log

`execution_log_YYYYMMDD_HHMMSS.txt` - Complete log of the execution with timestamps and progress.

Example:
```
2024-11-16 21:45:30 - INFO - ================================================================================
2024-11-16 21:45:30 - INFO - 🚀 PPIPilot - Batch Execution CLI Mode
2024-11-16 21:45:30 - INFO - ================================================================================
2024-11-16 21:45:30 - INFO - 
📋 Configuration:
2024-11-16 21:45:30 - INFO -    LLM Provider: openai
2024-11-16 21:45:30 - INFO -    Model: gpt-4-0125-preview
...
```

### Summary CSV

`summary.csv` - Aggregated results for all activities.

Format:
```
Activity;Total PPIs;Total Errors;Success Rate;Avg PPIs/Run
Declaration SUBMITTED by EMPLOYEE;120;5;95.0%;12.0
Declaration APPROVED by SUPERVISOR;115;8;92.0%;11.5
```

### Activity Results

For each activity, two CSV files per run/iteration:

**`run_XX_iteration_YY_withoutErrors.csv`** - Only valid PPIs
```
Name;Metric;Value;Agrupation;Colonna77
;ERROR: computing metric {};;;
Average time from start to Declaration SUBMITTED;time;417.5;None;A
```

**`run_XX_iteration_YY_withErrors.csv`** - All PPIs including errors
```
Name;Metric;Value;Agrupation;Colonna77
;ERROR: computing metric {};;;
Average time from start to Declaration SUBMITTED;time;417.5;None;A
Invalid PPI;time;ERROR;None;A
```

## 🔧 Advanced Usage

### Environment Variables

You can use environment variables for sensitive data:

```bash
# Set API key as environment variable
export OPENAI_API_KEY="sk-..."

# Modify config to use environment variable (requires script modification)
```

### Parallel Execution

Run multiple analyses in parallel (different config files):

```bash
# Terminal 1
python interface_batch_cli.py config_time.json

# Terminal 2
python interface_batch_cli.py config_occurrency.json
```

### Custom Output Naming

Organize outputs by experiment:

```json
{
  "output_folder": "experiments/experiment_001",
  "num_runs_per_activity": 20
}
```

### Integration with CI/CD

**GitHub Actions example:**

```yaml
name: PPIPilot Batch Analysis

on:
  push:
    branches: [ main ]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run batch analysis
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python interface_batch_cli.py config_batch.json
      
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: ppi-results
          path: quantitative_assessment/batch_results/
```

## 🐛 Troubleshooting

### Error: Configuration file not found

```
❌ Error: Configuration file not found: config_batch.json
```

**Solution:** Check the file path and ensure the config file exists.

### Error: Missing required fields

```
❌ Configuration Error: Missing required fields in config: api_key, xes_file_path
```

**Solution:** Add all required fields to your configuration file.

### Error: XES file not found

```
❌ Error reading XES file: XES file not found: logs/process.xes
```

**Solution:** Verify the XES file path in your configuration.

### Error: No valid activities to analyze

```
❌ No valid activities to analyze
```

**Solution:** Check that the activities specified in the config exist in the event log.

### Execution interrupted

Press `Ctrl+C` to interrupt execution:

```
⚠️  Execution interrupted by user
```

## 📝 Tips & Best Practices

1. **Start Small**: Test with 1-2 runs before running full batch
   ```json
   "num_runs_per_activity": 2,
   "activities": ["Activity 1"]
   ```

2. **Use Debug Logs**: Enable for troubleshooting
   ```json
   "save_debug_logs": true
   ```

3. **Organize Configs**: Use descriptive names
   ```
   config_time_10runs.json
   config_occurrency_5runs.json
   config_test_quick.json
   ```

4. **Version Control**: Track your config files in git (but exclude API keys!)
   ```gitignore
   # .gitignore
   config_batch.json  # Contains API key
   ```

5. **Monitor Progress**: Tail the execution log in real-time
   ```bash
   tail -f quantitative_assessment/batch_results/time/results_run_*/execution_log_*.txt
   ```

## 🆚 CLI vs GUI Comparison

| Feature | CLI (`interface_batch_cli.py`) | GUI (`interface_batch.py`) |
|---------|-------------------------------|---------------------------|
| **Interface** | Command line | Streamlit web interface |
| **Configuration** | JSON file | Interactive forms |
| **Automation** | ✅ Easy | ❌ Manual |
| **CI/CD Integration** | ✅ Yes | ❌ No |
| **Remote Execution** | ✅ Yes | ⚠️ Requires port forwarding |
| **Real-time Monitoring** | Log file | Live progress bars |
| **Ease of Use** | Requires config file | Point and click |
| **Best For** | Automated testing, batch jobs | Interactive exploration |

## 📚 Related Documentation

- **TESTING_GUIDE.md** - Testing features and error injection
- **README.md** - Main PPIPilot documentation
- **interface_batch.py** - GUI version of batch execution

## 🤝 Support

For issues or questions:
1. Check the execution log for detailed error messages
2. Enable debug logs for troubleshooting
3. Verify your configuration file format
4. Check that all dependencies are installed

## 📄 License

Same license as PPIPilot main project.
