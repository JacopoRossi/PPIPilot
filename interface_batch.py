import streamlit as st
import pandas as pd
import pm4py
import openai
from openai import OpenAI
import fromLogtoPPI_prompt_pipeline_goal as pipeline
from fromLogtoPPI_prompt_pipeline_goal import exec, auto_correct_errors_with_retry
import json
import os
from io import BytesIO
import logging
import sys
import tempfile
from datetime import datetime
import ppinatjson as pp

# ============================================================================
# BATCH EXECUTION CONFIGURATION
# ============================================================================
NUM_RUNS_PER_ACTIVITY = 10  # Number of runs for each activity
MAX_LEVEL1_ITERATIONS = 2  # Maximum iterations for Level 1 (Re-translation)
MAX_LEVEL2_ITERATIONS = 2  # Maximum iterations for Level 2 (Error correction)

# DEBUG/TESTING FLAGS
SAVE_PROMPTS_AND_RESPONSES = False
PROMPTS_LOG_FOLDER = "debug_prompts_log"
# ============================================================================

# Set the debug flags in the pipeline module
pipeline.SAVE_PROMPTS_AND_RESPONSES = SAVE_PROMPTS_AND_RESPONSES
pipeline.PROMPTS_LOG_FOLDER = PROMPTS_LOG_FOLDER

st.set_page_config(layout="wide")

# Function to read XES file
def read_xes_from_uploaded_file(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xes") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
    log = pm4py.read_xes(tmp_path)
    os.remove(tmp_path)
    return log

# Wrapper function to execute PPIs and save intermediate results
def execute_and_save_iterations(xes_file, file_path, ppis, activities, attributes, client,
                                activity_name, run_num, output_folder,
                                max_level1_iterations=2, max_level2_iterations=2):
    """
    Execute PPIs with error correction and save results after each iteration
    """
    import ppinatjson as pp
    
    iteration_num = 1
    all_saved_files = []
    
    # Initial execution
    if ppis == "occurrency":
        batch_size, df_sin_error, df, batch_size_sin_error, errors_captured = pp.exec_final_perc(xes_file, file_path)
    elif ppis == "time":
        batch_size, df_sin_error, df, batch_size_sin_error, errors_captured = pp.exec_final_time(xes_file, file_path)
    else:  # both
        batch_size, df_sin_error, df, batch_size_sin_error, errors_captured = pp.exec_final_both(xes_file, None, 
                                                                                                   json_path_time=file_path,
                                                                                                   json_path_occurrency=file_path)
    
    # Save initial iteration
    num_ppis = len(df_sin_error) if df_sin_error is not None else 0
    num_errors = len(errors_captured) if errors_captured else 0
    print(f"   📝 Saving results for activity: '{activity_name}'")
    csv_paths = save_results_to_csv(df_sin_error, df, activity_name, run_num, ppis, output_folder, num_errors, iteration=iteration_num)
    all_saved_files.extend(csv_paths)
    print(f"   💾 Saved 2 files: withoutErrors and withErrors")
    print(f"   📊 {num_ppis} PPIs, {num_errors} errors")
    
    # If there are errors, run full correction with auto_correct_errors_with_retry
    if num_errors > 0:
        batch_size, df_sin_error, df, batch_size_sin_error, errors_captured, total_iterations = auto_correct_errors_with_retry(
            xes_file, file_path, ppis, activities, attributes, client,
            max_level1_iterations=max_level1_iterations,
            max_level2_iterations=max_level2_iterations
        )
        
        # Save final corrected result
        if total_iterations > 1:
            num_ppis = len(df_sin_error) if df_sin_error is not None else 0
            num_errors = len(errors_captured) if errors_captured else 0
            csv_paths = save_results_to_csv(df_sin_error, df, activity_name, run_num, ppis, output_folder, num_errors, iteration=total_iterations)
            all_saved_files.extend(csv_paths)
            print(f"   💾 Saved 2 files for final iteration {total_iterations}: {num_ppis} PPIs, {num_errors} errors")
        
        return batch_size, df_sin_error, df, batch_size_sin_error, errors_captured, total_iterations, all_saved_files
    else:
        return batch_size, df_sin_error, df, batch_size_sin_error, errors_captured, 1, all_saved_files

# Function to save results in CSV format
def save_results_to_csv(df_without_errors, df_with_errors, activity_name, run_number, category, output_folder, num_errors=0, iteration=1):
    """
    Save results to CSV in the specified format:
    Name;Metric;Value;Agrupation;Colonna77
    
    Saves TWO files:
    1. _withoutErrors.csv - Only valid PPIs (df_without_errors)
    2. _withErrors.csv - All PPIs including errors (df_with_errors)
    
    The format follows the example:
    - First line: Name;Metric;Value;Agrupation;Colonna77
    - Second line: ;ERROR: computing metric {};;;
    - Following lines: actual PPI data
    
    Note: Each run and iteration gets its own file
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

# Function to process data
def send_data():
    st.session_state.client = OpenAI(api_key=key)
    
    log = read_xes_from_uploaded_file(xes_file)
    if log is not None:
        st.session_state.varianti = pm4py.llm.abstract_variants(log)
        st.session_state.dataframe = pm4py.convert_to_dataframe(log)
        dict_activities = pm4py.get_event_attribute_values(log, "concept:name")
        dict_dates = pm4py.get_event_attribute_values(log, "time:timestamp")
        st.session_state.fecha_min = min(dict_dates).date()
        st.session_state.fecha_max = max(dict_dates).date()
        st.session_state.activities = list(dict_activities.keys())
        attribute = pm4py.llm.abstract_log_attributes(log)
        res_attribute = (attribute.split("\n"))

        st.session_state.attribute_array = []
        attribute_string = ""
        for instance in res_attribute:
            st.session_state.attribute_array.append(instance.split("  ")[0])
            attribute_string = attribute_string + (instance.split("  ")[0]) + ", "

        attribute_string = attribute_string[:-2]
        st.session_state.file_uploaded = True
    else:
        st.error("There has been a problem uploading the file")

# Initialize session state
if "activities" not in st.session_state:
    st.session_state["activities"] = []
if "client" not in st.session_state:
    st.session_state["client"] = []
if "varianti" not in st.session_state:
    st.session_state["varianti"] = []
if "dataframe" not in st.session_state:
    st.session_state["dataframe"] = []
if "attribute_array" not in st.session_state:
    st.session_state["attribute_array"] = []
if "file_uploaded" not in st.session_state:
    st.session_state["file_uploaded"] = False
if "fecha_min" not in st.session_state:
    st.session_state['fecha_min'] = None
if "fecha_max" not in st.session_state:
    st.session_state['fecha_max'] = None

# UI Layout
st.title("🔄 PPIPilot - Batch Execution Mode")
st.markdown("---")

with st.expander("📋 Configuration", expanded=True):
    col0, col1 = st.columns(2)
    with col0:
        key = st.text_input("Set OpenAI key", type="password")
    with col1:
        xes_file = st.file_uploader('Select a file to upload the event log', type=['xes'])
    desc = st.text_area("Write the description:")
    goal = st.text_area("Organizational goal:")
    confirm = st.button("✅ Load Configuration", on_click=send_data)

if st.session_state.file_uploaded:
    st.success(f"✅ File loaded successfully! Found {len(st.session_state.activities)} activities.")
    
    col00, col11, col22 = st.columns(3)
    with col00:
        ppis = st.selectbox('Choose a category', ["time", "occurrency"])
    with col11:
        output_folder = st.text_input("Output folder for results", value="quantitative_assessment/batch_results")
    with col22:
        num_runs = st.number_input("Number of runs per activity", min_value=1, max_value=100, value=10, step=1)
    
    # Activity selection
    st.markdown("---")
    st.markdown("### 🎯 Activity Selection")
    
    use_all_activities = st.checkbox("✅ Analyze all activities", value=True)
    
    if use_all_activities:
        selected_activities = st.session_state.activities
        st.info(f"📊 Will analyze **all {len(selected_activities)} activities**")
    else:
        selected_activities = st.multiselect(
            "Select specific activities to analyze:",
            options=st.session_state.activities,
            default=st.session_state.activities[:1] if len(st.session_state.activities) > 0 else []
        )
        if len(selected_activities) > 0:
            st.info(f"📊 Will analyze **{len(selected_activities)} selected activities**")
        else:
            st.warning("⚠️ Please select at least one activity")
    
    st.markdown("---")
    st.markdown(f"### 🚀 Ready to execute {num_runs} runs for each of the {len(selected_activities)} selected activities")
    
    boton = st.button("▶️ Start Batch Execution", type="primary", disabled=(len(selected_activities) == 0))
    
    if boton:
        # Create timestamp for this batch run
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_output_folder = os.path.join(output_folder, ppis, f"results_run_{timestamp}")
        
        st.markdown("---")
        st.markdown("## 📊 Execution Progress")
        
        # Progress tracking
        total_executions = len(selected_activities) * num_runs
        progress_bar = st.progress(0)
        status_text = st.empty()
        execution_counter = 0
        
        # Summary statistics
        summary_data = []
        
        # Iterate through each selected activity
        for activity_idx, act in enumerate(selected_activities):
            st.markdown(f"### 🎯 Activity {activity_idx + 1}/{len(selected_activities)}: `{act}`")
            
            activity_results = []
            
            # Execute num_runs times for this activity
            for run_num in range(1, num_runs + 1):
                execution_counter += 1
                progress = execution_counter / total_executions
                progress_bar.progress(progress)
                status_text.text(f"Processing: {act} - Run {run_num}/{num_runs} ({execution_counter}/{total_executions})")
                
                try:
                    # Generate PPIs
                    print(f"\n🔄 Generating JSON for activity: {act}, Run: {run_num}")
                    cod_json = exec(
                        st.session_state.dataframe, act, st.session_state.varianti,
                        st.session_state.activities, ppis, desc, goal,
                        st.session_state.attribute_array, xes_file.name,
                        st.session_state.client, inject_test_errors=False, test_retry_mechanism=False
                    )
                    
                    print(f"   📄 Generated JSON file: {cod_json}")
                    
                    current_directory = os.path.dirname(__file__)
                    current_directory_con_slashes = current_directory.replace("\\", "/")
                    file_path = os.path.join(current_directory_con_slashes, cod_json).replace("\\", "/")
                    
                    # Execute PPIs with automatic error correction and save each iteration
                    batch_size, df_sin_error, df, batch_size_sin_error, errors_captured, iteration_count, saved_files = execute_and_save_iterations(
                        xes_file, file_path, ppis,
                        st.session_state.activities, st.session_state.attribute_array, st.session_state.client,
                        act, run_num, batch_output_folder,
                        max_level1_iterations=MAX_LEVEL1_ITERATIONS,
                        max_level2_iterations=MAX_LEVEL2_ITERATIONS
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
                        print(f"✅ Run {run_num} completed: {num_ppis} PPIs generated, {num_errors} errors")
                    else:
                        activity_results.append({
                            'run': run_num,
                            'ppis': 0,
                            'errors': num_errors,
                            'status': '⚠️'
                        })
                        print(f"⚠️ Run {run_num} completed: No PPIs generated, {num_errors} errors")
                
                except Exception as e:
                    # Save CSV even for critical failures
                    csv_paths = save_results_to_csv(
                        None, None, act, run_num, ppis, batch_output_folder, num_errors=1, iteration=1
                    )
                    
                    activity_results.append({
                        'run': run_num,
                        'ppis': 0,
                        'errors': 1,
                        'status': '❌'
                    })
                    print(f"❌ Run {run_num} failed: {str(e)}")
            
            # Display summary for this activity
            activity_df = pd.DataFrame(activity_results)
            total_ppis = activity_df['ppis'].sum()
            total_errors = activity_df['errors'].sum()
            success_rate = (activity_df['ppis'] > 0).sum() / num_runs * 100
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total PPIs", total_ppis)
            with col2:
                st.metric("Total Errors", total_errors)
            with col3:
                st.metric("Success Rate", f"{success_rate:.1f}%")
            with col4:
                st.metric("Avg PPIs/Run", f"{total_ppis/num_runs:.1f}")
            
            # Add to summary
            summary_data.append({
                'Activity': act,
                'Total PPIs': total_ppis,
                'Total Errors': total_errors,
                'Success Rate': f"{success_rate:.1f}%",
                'Avg PPIs/Run': f"{total_ppis/num_runs:.1f}"
            })
            
            st.markdown("---")
        
        # Final summary
        progress_bar.progress(1.0)
        status_text.text("✅ Batch execution completed!")
        
        st.markdown("## 📈 Final Summary")
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
        
        st.success(f"✅ All results saved to: `{batch_output_folder}`")
        st.balloons()

else:
    st.info("👆 Please load your configuration to start batch execution")
