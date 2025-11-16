#!/usr/bin/env python3
"""
PPIPilot - Batch Execution CLI Mode

This script allows running batch PPI analysis from the command line using a configuration file.
No GUI required - perfect for automated testing and CI/CD pipelines.

Usage:
    python interface_batch_cli.py config_batch.json
    python interface_batch_cli.py --config path/to/config.json
"""

import argparse
import json
import sys
import os
import pandas as pd
import pm4py
from datetime import datetime
import tempfile
import logging
from pathlib import Path

# Import PPIPilot modules
import fromLogtoPPI_prompt_pipeline_goal as pipeline
from fromLogtoPPI_prompt_pipeline_goal import exec, auto_correct_errors_with_retry
import ppinatjson as pp
import llm_config


# ============================================================================
# LOGGING SETUP
# ============================================================================
def setup_logging(log_file=None):
    """Setup logging to console and optionally to file"""
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    return logging.getLogger(__name__)


# ============================================================================
# FILE OPERATIONS
# ============================================================================
def read_xes_file(file_path):
    """Read XES file and return event log"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"XES file not found: {file_path}")
    
    logger.info(f"📂 Reading XES file: {file_path}")
    log = pm4py.read_xes(file_path)
    logger.info(f"✅ XES file loaded successfully")
    return log


def save_results_to_csv(df_without_errors, df_with_errors, activity_name, run_number, category, output_folder, num_errors=0, iteration=1):
    """
    Save results to CSV in the specified format:
    Name;Metric;Value;Agrupation;Colonna77
    
    Saves TWO files:
    1. _withoutErrors.csv - Only valid PPIs (df_without_errors)
    2. _withErrors.csv - All PPIs including errors (df_with_errors)
    """
    
    # Clean activity name for folder
    clean_activity = activity_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    
    # Create activity subfolder
    activity_folder = os.path.join(output_folder, clean_activity)
    os.makedirs(activity_folder, exist_ok=True)
    
    saved_files = []
    
    # Helper function to write CSV
    def write_csv_file(df, filename_suffix, is_error_version=False):
        filename = f"run_{run_number:02d}_iteration_{iteration:02d}_{filename_suffix}.csv"
        filepath = os.path.join(activity_folder, filename)
        
        rows_to_write = []
        
        # Always add header
        rows_to_write.append("Name;Metric;Value;Agrupation;Colonna77")
        rows_to_write.append(";ERROR: computing metric {};;;")
        
        # Add data rows if dataframe has data
        if df is not None and len(df) > 0:
            for idx, row in df.iterrows():
                # Get values from dataframe
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
                
                # Determine Colonna77 value
                colonna77 = 'A'
                
                # Format the row
                row_str = f"{name};{metric};{value};{agrupation};{colonna77}"
                rows_to_write.append(row_str)
        else:
            # If no valid PPIs, add a comment line
            rows_to_write.append(f";No valid PPIs in this iteration ({num_errors} errors);;;")
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            for row in rows_to_write:
                f.write(row + '\n')
        
        return filepath
    
    # Save file WITHOUT errors (only valid PPIs)
    filepath_without = write_csv_file(df_without_errors, "withoutErrors")
    saved_files.append(filepath_without)
    
    # Save file WITH errors (all PPIs including errors)
    filepath_with = write_csv_file(df_with_errors, "withErrors")
    saved_files.append(filepath_with)
    
    return saved_files


# ============================================================================
# PPI EXECUTION
# ============================================================================
def execute_and_save_iterations(xes_file_path, log, file_path, ppis, activities, attributes, client,
                                activity_name, run_num, output_folder,
                                max_level1_iterations=2, max_level2_iterations=2, model="gpt-4-0125-preview"):
    """
    Execute PPIs with error correction and save results after each iteration
    """
    
    iteration_num = 1
    all_saved_files = []
    
    # Read the log for execution
    log_for_exec = pm4py.read_xes(xes_file_path)
    
    # Initial execution
    if ppis == "occurrency":
        batch_size, df_sin_error, df, batch_size_sin_error, errors_captured = pp.exec_final_perc(log_for_exec, file_path)
    elif ppis == "time":
        batch_size, df_sin_error, df, batch_size_sin_error, errors_captured = pp.exec_final_time(log_for_exec, file_path)
    else:  # both
        batch_size, df_sin_error, df, batch_size_sin_error, errors_captured = pp.exec_final_both(log_for_exec, None, 
                                                                                                   json_path_time=file_path,
                                                                                                   json_path_occurrency=file_path)
    
    # Save initial iteration
    num_ppis = len(df_sin_error) if df_sin_error is not None else 0
    num_errors = len(errors_captured) if errors_captured else 0
    logger.info(f"   📝 Saving results for activity: '{activity_name}'")
    csv_paths = save_results_to_csv(df_sin_error, df, activity_name, run_num, ppis, output_folder, num_errors, iteration=iteration_num)
    all_saved_files.extend(csv_paths)
    logger.info(f"   💾 Saved 2 files: withoutErrors and withErrors")
    logger.info(f"   📊 {num_ppis} PPIs, {num_errors} errors")
    
    # If there are errors, run full correction with auto_correct_errors_with_retry
    if num_errors > 0:
        batch_size, df_sin_error, df, batch_size_sin_error, errors_captured, total_iterations = auto_correct_errors_with_retry(
            log_for_exec, file_path, ppis, activities, attributes, client,
            max_level1_iterations=max_level1_iterations,
            max_level2_iterations=max_level2_iterations,
            model=model
        )
        
        # Save final corrected result
        if total_iterations > 1:
            num_ppis = len(df_sin_error) if df_sin_error is not None else 0
            num_errors = len(errors_captured) if errors_captured else 0
            csv_paths = save_results_to_csv(df_sin_error, df, activity_name, run_num, ppis, output_folder, num_errors, iteration=total_iterations)
            all_saved_files.extend(csv_paths)
            logger.info(f"   💾 Saved 2 files for final iteration {total_iterations}: {num_ppis} PPIs, {num_errors} errors")
        
        return batch_size, df_sin_error, df, batch_size_sin_error, errors_captured, total_iterations, all_saved_files
    else:
        return batch_size, df_sin_error, df, batch_size_sin_error, errors_captured, 1, all_saved_files


# ============================================================================
# CONFIGURATION LOADING
# ============================================================================
def normalize_provider_name(provider_name):
    """
    Normalize provider name to match LLMConfig.PROVIDERS keys
    Handles common variations and case-insensitive matching
    """
    # Mapping of common lowercase names to official names
    provider_mapping = {
        'openai': 'OpenAI',
        'qwen': 'Qwen (Alibaba Cloud)',
        'qwen (alibaba cloud)': 'Qwen (Alibaba Cloud)',
        'alibaba': 'Qwen (Alibaba Cloud)',
        'deepseek': 'DeepSeek',
        'anthropic': 'Anthropic',
        'ollama': 'Ollama',
        'azure_openai': 'Azure OpenAI',
        'azure openai': 'Azure OpenAI',
    }
    
    # Try exact match first
    if provider_name in llm_config.LLMConfig.PROVIDERS:
        return provider_name
    
    # Try lowercase mapping
    normalized = provider_mapping.get(provider_name.lower())
    if normalized and normalized in llm_config.LLMConfig.PROVIDERS:
        return normalized
    
    # Try case-insensitive match with available providers
    for available_provider in llm_config.LLMConfig.PROVIDERS.keys():
        if available_provider.lower() == provider_name.lower():
            return available_provider
    
    # Return original if no match found (will fail later with proper error)
    return provider_name


def load_config(config_path):
    """Load configuration from JSON file"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Validate required fields
    required_fields = ['llm_provider', 'llm_model', 'api_key', 'xes_file_path', 'ppi_category']
    missing_fields = [field for field in required_fields if field not in config]
    
    if missing_fields:
        raise ValueError(f"Missing required fields in config: {', '.join(missing_fields)}")
    
    # Normalize provider name
    config['llm_provider'] = normalize_provider_name(config['llm_provider'])
    
    # Set defaults for optional fields
    config.setdefault('description', '')
    config.setdefault('goal', '')
    config.setdefault('output_folder', 'quantitative_assessment/batch_results')
    config.setdefault('num_runs_per_activity', 10)
    config.setdefault('activities', ['all'])
    config.setdefault('max_level1_iterations', 2)
    config.setdefault('max_level2_iterations', 2)
    config.setdefault('save_debug_logs', False)
    
    return config


# ============================================================================
# MAIN EXECUTION
# ============================================================================
def run_batch_analysis(config):
    """Main function to run batch PPI analysis"""
    
    # Setup logging
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(config['output_folder'], config['ppi_category'], f"execution_log_{timestamp}.txt")
    global logger
    logger = setup_logging(log_file)
    
    logger.info("=" * 80)
    logger.info("🚀 PPIPilot - Batch Execution CLI Mode")
    logger.info("=" * 80)
    
    # Log configuration
    logger.info("\n📋 Configuration:")
    logger.info(f"   LLM Provider: {config['llm_provider']}")
    logger.info(f"   Model: {config['llm_model']}")
    logger.info(f"   XES File: {config['xes_file_path']}")
    logger.info(f"   PPI Category: {config['ppi_category']}")
    logger.info(f"   Runs per activity: {config['num_runs_per_activity']}")
    logger.info(f"   Output folder: {config['output_folder']}")
    
    # Setup debug logging if requested
    if config['save_debug_logs']:
        pipeline.SAVE_PROMPTS_AND_RESPONSES = True
        pipeline.PROMPTS_LOG_FOLDER = "debug_prompts_log"
        logger.info(f"   Debug logs: Enabled (folder: {pipeline.PROMPTS_LOG_FOLDER})")
    
    # Initialize LLM provider
    logger.info("\n🔧 Initializing LLM provider...")
    try:
        provider = llm_config.LLMConfig.create_provider(
            provider_name=config['llm_provider'],
            api_key=config['api_key'],
            model_name=config['llm_model']
        )
        client = provider.get_client()
        model = provider.get_model_name()
        logger.info(f"✅ LLM provider initialized: {config['llm_provider']} - {model}")
    except Exception as e:
        logger.error(f"❌ Error initializing LLM provider: {str(e)}")
        return 1
    
    # Load XES file
    try:
        log = read_xes_file(config['xes_file_path'])
    except Exception as e:
        logger.error(f"❌ Error reading XES file: {str(e)}")
        return 1
    
    # Extract log information
    logger.info("\n📊 Analyzing event log...")
    varianti = pm4py.llm.abstract_variants(log)
    dataframe = pm4py.convert_to_dataframe(log)
    dict_activities = pm4py.get_event_attribute_values(log, "concept:name")
    activities = list(dict_activities.keys())
    
    attribute = pm4py.llm.abstract_log_attributes(log)
    res_attribute = attribute.split("\n")
    attribute_array = [instance.split("  ")[0] for instance in res_attribute]
    
    logger.info(f"   Activities found: {len(activities)}")
    logger.info(f"   Attributes found: {len(attribute_array)}")
    
    # Determine which activities to analyze
    if config['activities'] == ['all'] or 'all' in config['activities']:
        selected_activities = activities
        logger.info(f"   📌 Will analyze ALL {len(selected_activities)} activities")
    else:
        selected_activities = [act for act in config['activities'] if act in activities]
        if len(selected_activities) < len(config['activities']):
            missing = set(config['activities']) - set(selected_activities)
            logger.warning(f"   ⚠️  Activities not found in log: {missing}")
        logger.info(f"   📌 Will analyze {len(selected_activities)} selected activities")
    
    if len(selected_activities) == 0:
        logger.error("❌ No valid activities to analyze")
        return 1
    
    # Create output folder
    batch_output_folder = os.path.join(
        config['output_folder'], 
        config['ppi_category'], 
        f"results_run_{timestamp}"
    )
    os.makedirs(batch_output_folder, exist_ok=True)
    logger.info(f"   📁 Output folder: {batch_output_folder}")
    
    # Execute batch analysis
    logger.info("\n" + "=" * 80)
    logger.info("🔄 Starting Batch Execution")
    logger.info("=" * 80)
    
    total_executions = len(selected_activities) * config['num_runs_per_activity']
    execution_counter = 0
    summary_data = []
    
    # Iterate through each selected activity
    for activity_idx, act in enumerate(selected_activities):
        logger.info(f"\n{'=' * 80}")
        logger.info(f"🎯 Activity {activity_idx + 1}/{len(selected_activities)}: {act}")
        logger.info(f"{'=' * 80}")
        
        activity_results = []
        
        # Execute num_runs times for this activity
        for run_num in range(1, config['num_runs_per_activity'] + 1):
            execution_counter += 1
            progress = (execution_counter / total_executions) * 100
            logger.info(f"\n▶️  Run {run_num}/{config['num_runs_per_activity']} - Progress: {progress:.1f}% ({execution_counter}/{total_executions})")
            
            try:
                # Generate PPIs
                logger.info(f"   🔄 Generating JSON for activity: {act}")
                cod_json = exec(
                    dataframe, act, varianti,
                    activities, config['ppi_category'], config['description'], config['goal'],
                    attribute_array, os.path.basename(config['xes_file_path']),
                    client, inject_test_errors=False, test_retry_mechanism=False,
                    model=model
                )
                
                logger.info(f"   📄 Generated JSON file: {cod_json}")
                
                current_directory = os.path.dirname(__file__)
                current_directory_con_slashes = current_directory.replace("\\", "/")
                file_path = os.path.join(current_directory_con_slashes, cod_json).replace("\\", "/")
                
                # Execute PPIs with automatic error correction and save each iteration
                batch_size, df_sin_error, df, batch_size_sin_error, errors_captured, iteration_count, saved_files = execute_and_save_iterations(
                    config['xes_file_path'], log, file_path, config['ppi_category'],
                    activities, attribute_array, client,
                    act, run_num, batch_output_folder,
                    max_level1_iterations=config['max_level1_iterations'],
                    max_level2_iterations=config['max_level2_iterations'],
                    model=model
                )
                
                # Get final results
                num_ppis = len(df_sin_error) if df_sin_error is not None else 0
                num_errors = len(errors_captured) if errors_captured else 0
                
                if num_ppis > 0:
                    activity_results.append({
                        'run': run_num,
                        'ppis': num_ppis,
                        'errors': num_errors,
                        'status': '✅'
                    })
                    logger.info(f"   ✅ Run {run_num} completed: {num_ppis} PPIs generated, {num_errors} errors")
                else:
                    activity_results.append({
                        'run': run_num,
                        'ppis': 0,
                        'errors': num_errors,
                        'status': '⚠️'
                    })
                    logger.info(f"   ⚠️  Run {run_num} completed: No PPIs generated, {num_errors} errors")
            
            except Exception as e:
                # Save CSV even for critical failures
                csv_paths = save_results_to_csv(
                    None, None, act, run_num, config['ppi_category'], batch_output_folder, num_errors=1, iteration=1
                )
                
                activity_results.append({
                    'run': run_num,
                    'ppis': 0,
                    'errors': 1,
                    'status': '❌'
                })
                logger.error(f"   ❌ Run {run_num} failed: {str(e)}")
        
        # Display summary for this activity
        activity_df = pd.DataFrame(activity_results)
        total_ppis = activity_df['ppis'].sum()
        total_errors = activity_df['errors'].sum()
        success_rate = (activity_df['ppis'] > 0).sum() / config['num_runs_per_activity'] * 100
        avg_ppis = total_ppis / config['num_runs_per_activity']
        
        logger.info(f"\n📊 Summary for activity '{act}':")
        logger.info(f"   Total PPIs: {total_ppis}")
        logger.info(f"   Total Errors: {total_errors}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        logger.info(f"   Avg PPIs/Run: {avg_ppis:.1f}")
        
        # Add to summary
        summary_data.append({
            'Activity': act,
            'Total PPIs': total_ppis,
            'Total Errors': total_errors,
            'Success Rate': f"{success_rate:.1f}%",
            'Avg PPIs/Run': f"{avg_ppis:.1f}"
        })
    
    # Final summary
    logger.info("\n" + "=" * 80)
    logger.info("📈 FINAL SUMMARY")
    logger.info("=" * 80)
    
    summary_df = pd.DataFrame(summary_data)
    logger.info("\n" + summary_df.to_string(index=False))
    
    # Save summary to CSV
    summary_path = os.path.join(batch_output_folder, "summary.csv")
    summary_df.to_csv(summary_path, index=False, sep=';')
    logger.info(f"\n💾 Summary saved to: {summary_path}")
    
    logger.info(f"\n✅ All results saved to: {batch_output_folder}")
    logger.info("\n" + "=" * 80)
    logger.info("🎉 Batch execution completed successfully!")
    logger.info("=" * 80)
    
    return 0


# ============================================================================
# CLI ENTRY POINT
# ============================================================================
def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='PPIPilot - Batch Execution CLI Mode',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python interface_batch_cli.py config_batch.json
  python interface_batch_cli.py --config path/to/config.json
  python interface_batch_cli.py -c my_config.json

Configuration file format (JSON):
  {
    "llm_provider": "openai",
    "llm_model": "gpt-4-0125-preview",
    "api_key": "sk-...",
    "xes_file_path": "path/to/log.xes",
    "description": "Process description",
    "goal": "Organizational goal",
    "ppi_category": "time",
    "output_folder": "quantitative_assessment/batch_results",
    "num_runs_per_activity": 10,
    "activities": ["all"],
    "max_level1_iterations": 2,
    "max_level2_iterations": 2,
    "save_debug_logs": false
  }
        """
    )
    
    parser.add_argument(
        'config_file',
        nargs='?',
        help='Path to configuration JSON file'
    )
    parser.add_argument(
        '-c', '--config',
        dest='config_file_alt',
        help='Path to configuration JSON file (alternative)'
    )
    
    args = parser.parse_args()
    
    # Determine config file path
    config_path = args.config_file or args.config_file_alt
    
    if not config_path:
        parser.print_help()
        print("\n❌ Error: Configuration file is required")
        return 1
    
    try:
        # Load configuration
        config = load_config(config_path)
        
        # Run batch analysis
        return run_batch_analysis(config)
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        return 1
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Execution interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
