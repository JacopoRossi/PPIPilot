import streamlit as st
import pandas as pd
import pm4py
import openai
from openai import OpenAI
from fromLogtoPPI_prompt_pipeline_goal import exec, exec_with_fallback
import json
import os
from io import BytesIO
import json
import logging
import sys
import os
import shutil
from colorama import Fore
import tempfile

import ppinatjson as pp


#logger = logging.getLogger(__name__)



# Crear un objeto Namespace y asignar los valores deseados
st.set_page_config(layout="wide")

col0, col1, col2 = st.columns(3)

# Función para leer un archivo XES desde un archivo temporal
def read_xes_from_uploaded_file(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xes") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
    log = pm4py.read_xes(tmp_path)
    os.remove(tmp_path)  # Elimina el archivo temporal
    return log


def send_data():

    st.session_state.client = OpenAI(
        api_key=key,
            )
    
    log = read_xes_from_uploaded_file(xes_file)
    if log is not None:
        
        st.session_state.varianti=pm4py.llm.abstract_variants(log)
        st.session_state.dataframe = pm4py.convert_to_dataframe(log)
        dict_activities = pm4py.get_event_attribute_values(log, "concept:name")
        dict_dates=pm4py.get_event_attribute_values(log, "time:timestamp")
        st.session_state.fecha_min = min(dict_dates).date()
        st.session_state.fecha_max = max(dict_dates).date()
        st.session_state.activities = list(dict_activities.keys())
        attribute=pm4py.llm.abstract_log_attributes(log)
        res_attribute=(attribute.split("\n"))

        st.session_state.attribute_array=[]
        attribute_string=""
        for instance in res_attribute:
            st.session_state.attribute_array.append(instance.split("  ")[0])
            attribute_string=attribute_string+(instance.split("  ")[0])+", "

        attribute_string=attribute_string[:-2]
        st.session_state.file_uploaded=True
    else:
        st.error("There has been a problem uploading the file")

if "activities" not in st.session_state:
    st.session_state["activities"] = []

if "client" not in st.session_state:
    st.session_state["client"] = []

if "varianti" not in st.session_state:
    st.session_state["varianti"] = []

if "dataframe" not in st.session_state:
    st.session_state["dataframe"] = []

if "attribute_Array" not in st.session_state:
    st.session_state["attribute_array"] = []

if "file_uploaded" not in st.session_state:
    st.session_state["file_uploaded"] = False

if "file_path" not in st.session_state:
    st.session_state["file_path"] = None

if "file_path_time" not in st.session_state:
    st.session_state["file_path_time"] = None

if "file_path_occurrency" not in st.session_state:
    st.session_state["file_path_occurrency"] = None

if "batch_size" not in st.session_state:
    st.session_state["batch_size"] = 25

if "batch_size_sin_error" not in st.session_state:
    st.session_state["batch_size_sin_error"] = 25

if "batch_size" not in st.session_state:
    st.session_state["batch_size_gt"] = 25

if "batch_size_sin_error" not in st.session_state:
    st.session_state["batch_size_sin_error_gt"] = 25

if "ejecutado_final" not in st.session_state:
    st.session_state["ejecutado_final"] = False

if "df" not in st.session_state:
    st.session_state["df"] = None

if "df_sin_error" not in st.session_state:
    st.session_state["df_sin_error"] = None

if "df_gt" not in st.session_state:
    st.session_state["df_gt"] = None

if "df_sin_error_gt" not in st.session_state:
    st.session_state["df_sin_error_gt"] = None

if "time_grouper" not in st.session_state:
    st.session_state["time_grouper"] = False

if "fecha_min" not in st.session_state:
    st.session_state['fecha_min'] = None
if "fecha_max" not in st.session_state:
    st.session_state['fecha_max'] = None

if "fallback_executed" not in st.session_state:
    st.session_state["fallback_executed"] = False

if "fallback_file_path" not in st.session_state:
    st.session_state["fallback_file_path"] = None

if "fallback_file_path_time" not in st.session_state:
    st.session_state["fallback_file_path_time"] = None

if "fallback_file_path_occurrency" not in st.session_state:
    st.session_state["fallback_file_path_occurrency"] = None

if "custom_direction" not in st.session_state:
    st.session_state["custom_direction"] = ""

# Alternative analysis results storage
if "fallback_batch_size" not in st.session_state:
    st.session_state["fallback_batch_size"] = 25

if "fallback_df_sin_error" not in st.session_state:
    st.session_state["fallback_df_sin_error"] = None

if "fallback_df" not in st.session_state:
    st.session_state["fallback_df"] = None

if "fallback_batch_size_sin_error" not in st.session_state:
    st.session_state["fallback_batch_size_sin_error"] = 25

if "fallback_batch_size_gt" not in st.session_state:
    st.session_state["fallback_batch_size_gt"] = 25

if "fallback_df_sin_error_gt" not in st.session_state:
    st.session_state["fallback_df_sin_error_gt"] = None

if "fallback_df_gt" not in st.session_state:
    st.session_state["fallback_df_gt"] = None

if "fallback_batch_size_sin_error_gt" not in st.session_state:
    st.session_state["fallback_batch_size_sin_error_gt"] = 25

if "fallback_time_grouper" not in st.session_state:
    st.session_state["fallback_time_grouper"] = False

with st.expander("Click to complete the form"):
    col0, col1 = st.columns(2)
    with col0:
        key = st.text_input("Set OpenAI key", type="password")
    with col1:
        xes_file = st.file_uploader('Select a file to upload the event log', type=['xes'])
    desc = st.text_area("Write the description:")
    confirm = st.button("OK", on_click=send_data)

if st.session_state.file_uploaded:
    col00, col11 = st.columns(2)
    with col00:
        ppis = st.selectbox('Choose a category', ["time","occurrency","both"],)
    with col11:
        act = st.selectbox("Choose an activity:", st.session_state.activities)
    goal = st.text_area("Organizational goal")
    
    col01, col02, col03 = st.columns(3)
    with col02:
        boton = st.button("Send options selected")
    
    if boton:
        # Clear previous results when new options are selected
        st.session_state.ejecutado_final = False
        st.session_state.time_grouper = False
        st.session_state.file_path = None
        st.session_state.file_path_time = None
        st.session_state.file_path_occurrency = None
        st.session_state.df = None
        st.session_state.df_sin_error = None
        st.session_state.df_gt = None
        st.session_state.df_sin_error_gt = None
        st.session_state.batch_size = 25
        st.session_state.batch_size_sin_error = 25
        st.session_state.batch_size_gt = 25
        st.session_state.batch_size_sin_error_gt = 25
        
        if ppis == "both":
            ls_cat = ["time","occurrency"]
            for el in ls_cat:
                cod_json = exec(st.session_state.dataframe,act,st.session_state.varianti, 
                st.session_state.activities, el, desc, goal, st.session_state.attribute_array,
                    xes_file.name, st.session_state.client)
                current_directory = os.path.dirname(__file__)
                current_directory_con_slashes = current_directory.replace("\\", "/")
                if el=="time":
                    st.session_state.file_path_time = os.path.join(current_directory_con_slashes, cod_json).replace("\\","/")
                else: 
                    st.session_state.file_path_occurrency = os.path.join(current_directory_con_slashes, cod_json).replace("\\","/")
        
        else:
            cod_json = exec(st.session_state.dataframe,act,st.session_state.varianti, 
                st.session_state.activities, ppis, desc, goal, st.session_state.attribute_array,
                    xes_file.name, st.session_state.client)
            
            
            current_directory = os.path.dirname(__file__)
            current_directory_con_slashes = current_directory.replace("\\", "/")
        
            # Construir la ruta completa al archivo JSON
            st.session_state.file_path = os.path.join(current_directory_con_slashes, cod_json).replace("\\","/")
            #st.write("File_path", st.session_state.file_path)

if st.session_state.file_path is not None or st.session_state.file_path_time is not None and st.session_state.file_path_occurrency is not None:
    if not st.session_state.ejecutado_final:
        if ppis == "occurrency":

            st.session_state.batch_size,st.session_state.df_sin_error, st.session_state.df, st.session_state.batch_size_sin_error = pp.exec_final_perc(xes_file,st.session_state.file_path)
        
        elif ppis == "time":

            st.session_state.batch_size,st.session_state.df_sin_error, st.session_state.df, st.session_state.batch_size_sin_error = pp.exec_final_time(xes_file,st.session_state.file_path)
        
        else:
            
            st.session_state.batch_size,st.session_state.df_sin_error, st.session_state.df, st.session_state.batch_size_sin_error = pp.exec_final_both(xes_file,st.session_state.file_path_time, st.session_state.file_path_occurrency)
        

        st.session_state.ejecutado_final = True
        

    columna1, columna2 = st.columns(2)
    with columna1:
        selector = st.toggle("Debug ON")
        timegroup = st.toggle("Time group")
    if timegroup:

        with columna2:
            period_aliases = {
                'Week':'W',  # Weekly frequency
                'Month':'M',  # Month end frequency
                'Year': 'Y',  # Year end frequency
                'Hourly': 'H',  # Hourly frequency
                'Minutely': 'T',  # Minutely frequency
                'Secondly':'S',  # Secondly frequency
            }

            # Crear el selector de period aliases con Streamlit
            selected_alias_key = st.selectbox("Select Period Alias:", list(period_aliases.keys()))

            # Obtener el valor seleccionado del diccionario
            selected_alias = period_aliases[selected_alias_key]

            # Permitir al usuario ingresar un número
            number = st.number_input("Enter a number:", value=1, min_value=1, step=1)

            # Mostrar el period alias y el número seleccionado
            st.write("You selected:", number, selected_alias_key)
            boton_tiempo = st.button("OK selected alias")
        if boton_tiempo:
            st.session_state.time_grouper = True
            if ppis == "both":

                st.session_state.batch_size_gt,st.session_state.df_sin_error_gt, st.session_state.df_gt, st.session_state.batch_size_sin_error_gt = pp.exec_final_both(xes_file,st.session_state.file_path_time, st.session_state.file_path_occurrency, time_group=str(number)+selected_alias)

            elif ppis=="time":

                st.session_state.batch_size_gt,st.session_state.df_sin_error_gt, st.session_state.df_gt, st.session_state.batch_size_sin_error_gt = pp.exec_final_time(xes_file,st.session_state.file_path, time_group=str(number)+selected_alias)

            elif ppis == "occurrency":

                st.session_state.batch_size_gt,st.session_state.df_sin_error_gt, st.session_state.df_gt, st.session_state.batch_size_sin_error_gt = pp.exec_final_perc(xes_file,st.session_state.file_path, time_group=str(number)+selected_alias)
            

    

    if selector and not timegroup: 
        

        edited_df = st.data_editor(
                st.session_state.df[["Name", 'Metric','Value']],
            column_config={

            },
        disabled=["Name", 'Metric','Value'],
        hide_index=True,
        use_container_width = True,
            height= int(35.2*(st.session_state.batch_size+1))
        )
    elif selector and timegroup and st.session_state.time_grouper:
        
        edited_df = st.data_editor(
            st.session_state.df_gt[['Name','Metric', 'Last Interval Value','Group By','agrupation']],
                column_config={
                "agrupation": st.column_config.LineChartColumn("Trend [{} - {}]".format(st.session_state.fecha_min, st.session_state.fecha_max),
                width = "medium",
                y_min = 0,
                y_max = 3)

            },
            disabled=["Name", 'Metric','Last Interval Value','Group By', 'Agrupation'],
            hide_index=True,
            use_container_width = True,
            height= int(35.2*(st.session_state.batch_size_gt+1))
            )
        
    elif not selector and timegroup and st.session_state.time_grouper:
        
        edited_df = st.data_editor(
            st.session_state.df_sin_error_gt[['Metric', 'Last Interval Value','Group By','agrupation']],
                column_config={
                "agrupation": st.column_config.LineChartColumn("Trend [{} - {}]".format(st.session_state.fecha_min, st.session_state.fecha_max),
                width = "medium",
                y_min = 0,
                y_max = 3)

            },
            disabled=["Name", 'Metric','Last Interval Value','Group By', 'Agrupation'],
            hide_index=True,
            use_container_width = True,
            height= int(35.2*(st.session_state.batch_size_sin_error_gt+1))
            )

    elif not selector and not timegroup:

        edited_df= st.data_editor(
            st.session_state.df_sin_error[['Metric', 'Value']],
            column_config={

            },
        disabled=['Metric','Value'],
        hide_index=True,
        use_container_width = True,
            height= int(35.2*(st.session_state.batch_size_sin_error+1))

        )

    else:
        
        edited_df= st.data_editor(
            st.session_state.df_sin_error[['Metric','Value']],
            column_config={

            },
        disabled=['Metric','Value'],
        hide_index=True,
        use_container_width = True,
            height= int(35.2*(st.session_state.batch_size_sin_error+1))

        )

    # Alternative Analysis Options - Only show after main results are available
    if st.session_state.ejecutado_final:
        st.markdown("---")
        st.markdown("### 🔄 Alternative Analysis")
        
        # Alternative Analysis Options
        with st.expander("🔄 Alternative Analysis Options", expanded=False):
            st.markdown("**Custom Direction for Alternative Analysis:**")
            custom_direction = st.text_area(
                "Write your personalized instructions for the Alternative PPI discovery:",
                placeholder="e.g., Focus on identifying bottlenecks in approval processes, or analyze resource allocation patterns, or discover compliance-related timing issues...",
                help="These custom instructions will be added to the Alternative analysis prompt to guide the LLM in discovering specific types of PPIs you're interested in.",
                key="Alternative_custom_direction"
            )
            st.session_state.custom_direction = custom_direction
        
        col_enh1, col_enh2, col_enh3 = st.columns(3)
        with col_enh2:
            boton_fallback = st.button("🔄 Run Alternative Analysis", help="Run additional PPI discovery with alternative approaches and custom directions")
        
        if boton_fallback:
            # Clear previous fallback results
            st.session_state.fallback_executed = False
            st.session_state.fallback_file_path = None
            st.session_state.fallback_file_path_time = None
            st.session_state.fallback_file_path_occurrency = None
            st.session_state.fallback_batch_size = 25
            st.session_state.fallback_df_sin_error = None
            st.session_state.fallback_df = None
            st.session_state.fallback_batch_size_sin_error = 25
            st.session_state.fallback_batch_size_gt = 25
            st.session_state.fallback_df_sin_error_gt = None
            st.session_state.fallback_df_gt = None
            st.session_state.fallback_batch_size_sin_error_gt = 25
            st.session_state.fallback_time_grouper = False
            
            with st.spinner("Running Alternative PPI analysis with alternative approaches..."):
                if ppis == "both":
                    ls_cat = ["time","occurrency"]
                    for el in ls_cat:
                        cod_json_fallback = exec_with_fallback(st.session_state.dataframe, act, st.session_state.varianti, 
                            st.session_state.activities, el, desc, goal, st.session_state.attribute_array,
                            xes_file.name, st.session_state.client, st.session_state.custom_direction)
                        current_directory = os.path.dirname(__file__)
                        current_directory_con_slashes = current_directory.replace("\\", "/")
                        if el=="time":
                            st.session_state.fallback_file_path_time = os.path.join(current_directory_con_slashes, cod_json_fallback).replace("\\","/")
                        else: 
                            st.session_state.fallback_file_path_occurrency = os.path.join(current_directory_con_slashes, cod_json_fallback).replace("\\","/")
                else:
                    cod_json_fallback = exec_with_fallback(st.session_state.dataframe, act, st.session_state.varianti, 
                        st.session_state.activities, ppis, desc, goal, st.session_state.attribute_array,
                        xes_file.name, st.session_state.client, st.session_state.custom_direction)
                    
                    current_directory = os.path.dirname(__file__)
                    current_directory_con_slashes = current_directory.replace("\\", "/")
                    st.session_state.fallback_file_path = os.path.join(current_directory_con_slashes, cod_json_fallback).replace("\\","/")
            
            st.session_state.fallback_executed = True
            st.success("✅ Alternative analysis completed! Additional PPIs have been discovered using alternative approaches.")

# Display fallback results if available
if st.session_state.fallback_executed and (st.session_state.fallback_file_path is not None or 
    (st.session_state.fallback_file_path_time is not None and st.session_state.fallback_file_path_occurrency is not None)):
    
    st.markdown("---")
    st.markdown("### 🔄 Alternative Analysis Results")
    if st.session_state.custom_direction.strip():
        st.markdown("*Additional PPIs discovered using alternative approaches with **custom directions***")
        with st.expander("📝 Custom Direction Used", expanded=False):
            st.markdown(f"**Your custom instruction:** {st.session_state.custom_direction}")
    else:
        st.markdown("*Additional PPIs discovered using alternative approaches*")
    
    # Process fallback results only once and store in session state
    if st.session_state.fallback_df is None:
        try:
            if ppis == "occurrency" and st.session_state.fallback_file_path:
                st.session_state.fallback_batch_size, st.session_state.fallback_df_sin_error, st.session_state.fallback_df, st.session_state.fallback_batch_size_sin_error = pp.exec_final_perc(xes_file, st.session_state.fallback_file_path)
            elif ppis == "time" and st.session_state.fallback_file_path:
                st.session_state.fallback_batch_size, st.session_state.fallback_df_sin_error, st.session_state.fallback_df, st.session_state.fallback_batch_size_sin_error = pp.exec_final_time(xes_file, st.session_state.fallback_file_path)
            elif ppis == "both" and st.session_state.fallback_file_path_time and st.session_state.fallback_file_path_occurrency:
                st.session_state.fallback_batch_size, st.session_state.fallback_df_sin_error, st.session_state.fallback_df, st.session_state.fallback_batch_size_sin_error = pp.exec_final_both(xes_file, st.session_state.fallback_file_path_time, st.session_state.fallback_file_path_occurrency)
        except Exception as e:
            st.error(f"Error processing Alternative analysis results: {str(e)}")
            st.stop()
    
    col_fallback1, col_fallback2 = st.columns(2)
    with col_fallback1:
        fallback_selector = st.toggle("Alternative Debug ON", key="fallback_debug")
        fallback_timegroup = st.toggle("Alternative Time Group", key="fallback_timegroup")
            
    if fallback_timegroup:
        with col_fallback2:
            period_aliases = {
                'Week':'W',  # Weekly frequency
                'Month':'M',  # Month end frequency
                'Year': 'Y',  # Year end frequency
                'Hourly': 'H',  # Hourly frequency
                'Minutely': 'T',  # Minutely frequency
                'Secondly':'S',  # Secondly frequency
            }

            # Crear el selector de period aliases con Streamlit
            selected_alias_key_fallback = st.selectbox("Select Period Alias for Alternative:", list(period_aliases.keys()), key="fallback_period_alias")

            # Obtener el valor seleccionado del diccionario
            selected_alias_fallback = period_aliases[selected_alias_key_fallback]

            # Permitir al usuario ingresar un número
            number_fallback = st.number_input("Enter a number for Alternative:", value=1, min_value=1, step=1, key="fallback_number")

            # Mostrar el period alias y el número seleccionado
            st.write("Alternative - You selected:", number_fallback, selected_alias_key_fallback)
            boton_tiempo_fallback = st.button("OK Alternative Time Group", key="fallback_time_ok")
        
        if boton_tiempo_fallback:
            st.session_state.fallback_time_grouper = True
            # Only process time group if not already processed
            if st.session_state.fallback_df_gt is None:
                if ppis == "both" and st.session_state.fallback_file_path_time and st.session_state.fallback_file_path_occurrency:
                    st.session_state.fallback_batch_size_gt, st.session_state.fallback_df_sin_error_gt, st.session_state.fallback_df_gt, st.session_state.fallback_batch_size_sin_error_gt = pp.exec_final_both(xes_file, st.session_state.fallback_file_path_time, st.session_state.fallback_file_path_occurrency, time_group=str(number_fallback)+selected_alias_fallback)
                elif ppis=="time" and st.session_state.fallback_file_path:
                    st.session_state.fallback_batch_size_gt, st.session_state.fallback_df_sin_error_gt, st.session_state.fallback_df_gt, st.session_state.fallback_batch_size_sin_error_gt = pp.exec_final_time(xes_file, st.session_state.fallback_file_path, time_group=str(number_fallback)+selected_alias_fallback)
                elif ppis == "occurrency" and st.session_state.fallback_file_path:
                    st.session_state.fallback_batch_size_gt, st.session_state.fallback_df_sin_error_gt, st.session_state.fallback_df_gt, st.session_state.fallback_batch_size_sin_error_gt = pp.exec_final_perc(xes_file, st.session_state.fallback_file_path, time_group=str(number_fallback)+selected_alias_fallback)
            
    # Display logic for Alternative analysis results
    if fallback_selector and not fallback_timegroup:
        st.markdown("**Alternative Analysis - Detailed View:**")
        fallback_edited_df = st.data_editor(
            st.session_state.fallback_df[["Name", 'Metric','Value']],
            column_config={},
            disabled=["Name", 'Metric','Value'],
            hide_index=True,
            use_container_width=True,
            height=int(35.2*(st.session_state.fallback_batch_size+1)),
            key="fallback_detailed"
        )
    elif fallback_selector and fallback_timegroup and st.session_state.fallback_time_grouper and st.session_state.fallback_df_gt is not None:
        st.markdown("**Alternative Analysis - Detailed Time Grouped View:**")
        fallback_edited_df = st.data_editor(
            st.session_state.fallback_df_gt[['Name','Metric', 'Last Interval Value','Group By','agrupation']],
            column_config={
                "agrupation": st.column_config.LineChartColumn("Alternative Trend [{} - {}]".format(st.session_state.fecha_min, st.session_state.fecha_max),
                width = "medium",
                y_min = 0,
                y_max = 3)
            },
            disabled=["Name", 'Metric','Last Interval Value','Group By', 'Agrupation'],
            hide_index=True,
            use_container_width=True,
            height=int(35.2*(st.session_state.fallback_batch_size_gt+1)),
            key="fallback_detailed_timegroup"
        )
    elif not fallback_selector and fallback_timegroup and st.session_state.fallback_time_grouper and st.session_state.fallback_df_sin_error_gt is not None:
        st.markdown("**Alternative Analysis - Clean Time Grouped View:**")
        fallback_edited_df = st.data_editor(
            st.session_state.fallback_df_sin_error_gt[['Metric', 'Last Interval Value','Group By','agrupation']],
            column_config={
                "agrupation": st.column_config.LineChartColumn("Alternative Trend [{} - {}]".format(st.session_state.fecha_min, st.session_state.fecha_max),
                width = "medium",
                y_min = 0,
                y_max = 3)
            },
            disabled=["Name", 'Metric','Last Interval Value','Group By', 'Agrupation'],
            hide_index=True,
            use_container_width=True,
            height=int(35.2*(st.session_state.fallback_batch_size_sin_error_gt+1)),
            key="fallback_clean_timegroup"
        )
    else:
        st.markdown("**Alternative Analysis - Clean View:**")
        fallback_edited_df = st.data_editor(
            st.session_state.fallback_df_sin_error[['Metric', 'Value']],
            column_config={},
            disabled=['Metric','Value'],
            hide_index=True,
            use_container_width=True,
            height=int(35.2*(st.session_state.fallback_batch_size_sin_error+1)),
            key="fallback_clean"
        )
            
            


