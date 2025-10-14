import pm4py
import os
from datetime import datetime
import warnings
import openai
from openai import OpenAI
import json
import streamlit as st
import tempfile

# Ignore all warnings
warnings.filterwarnings("ignore")



def get_completion(client,prompt, model="gpt-4-0125-preview"):  # Here we can change model name
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,  # Temperature
    )
    
    completion = response.choices[0].message.content
    
    return completion


def check_activity_applicable(dataframe, my_activity, type):
    applicable = True
    dict_types = {"time": "time:timestamp", "costs": "Costs", "frequency": "NO", "percentage": "NO"}

    if dict_types[type] == "NO":
        return applicable
    else:
        for index, row in dataframe.iterrows():
            if (row["concept:name"] == my_activity and (dict_types[type] not in dataframe.columns or row[dict_types[type]] is None)):
                applicable = False
        return applicable
    

def findPPI(dataframe, my_activity, list_variants, activities, type, description, goal,nome_file,client):
    if my_activity in activities:


        if(1):
            prompt_path = '1_prompt_description_goal/prompt_' + type + '.txt'

            try:
                with open(prompt_path, 'r') as file:
                    prompt = file.read()
                    response = get_completion(client, prompt.format(dataframe,activities,list_variants,description,goal,my_activity))

                    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{nome_file}_{type}_goal.txt", mode='w+', dir=tempfile.gettempdir()) as temp_file:
                        temp_file.write(my_activity + "\n")
                        temp_file.write(response + "\n\n")
                        temp_file_path = temp_file.name

            except FileNotFoundError:
                print("The file does not exist or you have selected a wrong type.")

        else:
            response = "You can't find PPIs of this category, since there are no data in the log."
            print(response)

    else:
        response = "The activity is not in the log."
        print(response)

    return response, temp_file_path


def translatePPI(listPPI,activities,attributes, nome_file, type,client):

    prompt_path = '2_prompt/prompt_' + type + '.txt'
    try:
        with open(prompt_path, 'r') as file:
            prompt = file.read()
            response = get_completion(client, prompt.format(listPPI,activities,attributes))
            print(response)
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{nome_file}_{type}_2_prompt.txt", mode='w+', dir=tempfile.gettempdir()) as temp_file:
                temp_file.write(response + "\n\n")
                temp_file_path = temp_file.name

    except FileNotFoundError:
        print("The file does not exist or you have selected a wrong type.")
        response = None
        temp_file_path = None

    return response,temp_file_path


def extract_ppi_json(file_path_input,category):

    line_before=""

    with open(file_path_input, 'r') as file:
        line_array = file.readlines()

    array_temp_json=[]
    data_dict_array=[]
    namePPI=""
    #for single_line in line_array:
    for i in range(len(line_array)):
        if(i==len(line_array)-1):

            data_dict = {}
                
            for item in array_temp_json:
                if len(item.split(": "))>2:
                    key=item.split(": ")[0]
                    value=item.split(": ")[1]
                else:
                    key,value=(item.split(": "))
                key = key.strip()
                value = value.strip()
                data_dict[key] = value

            complete_dict={}
            complete_dict["PPIname"]=namePPI
            complete_dict["PPIjson"]=data_dict
            data_dict_array.append(complete_dict)
        else:
            single_line=line_array[i]

            if single_line.strip().startswith("\"PPIjson\": {"):
                data_dict = {}
                
                for item in array_temp_json:
                    if len(item.split(": "))>2:
                        key=item.split(": ")[0]
                        value=item.split(": ")[1]
                    else:
                        key,value=(item.split(": "))
                    key = key.strip()
                    value = value.strip()
                    data_dict[key] = value

                complete_dict={}
                complete_dict["PPIname"]=namePPI
                complete_dict["PPIjson"]=data_dict
                data_dict_array.append(complete_dict)

                namePPI=line_before

            elif (single_line.strip().startswith('"count"') and category!="time"):
                array_temp_json=[]
                array_temp_json.append(single_line.strip())
            elif (single_line.strip().startswith('"begin"') and category=="time"):
                array_temp_json=[]
                array_temp_json.append(single_line.strip())
            elif (single_line.strip().startswith('"end"')and category=="time"):
                array_temp_json.append(single_line.strip())
            elif single_line.strip().startswith('"metric_condition"'):
                array_temp_json.append(single_line.strip())
            elif single_line.strip().startswith('"aggregation"'):
                array_temp_json.append(single_line.strip())
            elif single_line.strip().startswith('"group_by"'):
                array_temp_json.append(single_line.strip())
            elif single_line.strip().startswith('"filter"'):
                array_temp_json.append(single_line.strip())

            line_before=single_line.strip()


    # Crear un archivo temporal para la salida
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{category}_2_prompt.json", mode='w+', dir=tempfile.gettempdir()) as temp_file:
        json.dump(data_dict_array, temp_file, indent=4)
        temp_file_path = temp_file.name


    return temp_file_path


def clean_data(file_path):

    with open(file_path, 'r') as file:
        data = json.load(file)

    for item in data:
        item['PPIname']=item['PPIname'].replace("PPIname: ","")
        if(len(item['PPIname'])>0 and (item['PPIname'][-1]==",")):
            item['PPIname']=item['PPIname'][:-1]

        if item['PPIjson']:
            for key in item['PPIjson']:
                if(len(item['PPIjson'][key])>0 and (item['PPIjson'][key])[-1]==","):
                    item['PPIjson'][key]=item['PPIjson'][key][:-1]

    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def modify_file(file_path):

    with open(file_path, 'r+', encoding='utf-8') as file:
        content = file.read()
        file.seek(0)
        file.write(content.replace("\\\"", ""))
        file.truncate()


def findPPI_fallback(dataframe, my_activity, list_variants, activities, type, description, goal, nome_file, client, custom_direction=""):
    """
    Fallback mechanism to discover PPIs using alternative approaches.
    This function uses different prompting strategies to find PPIs when the main approach needs enhancement.
    """
    if my_activity in activities:
        # Use alternative prompt approach for fallback
        prompt_path = '3_prompt_fallback/prompt_' + type + '_fallback.txt'
        
        try:
            with open(prompt_path, 'r') as file:
                prompt = file.read()
                # Add custom direction if provided
                if custom_direction.strip():
                    if type == "time":
                        prompt = prompt.replace(
                            "h) Provide metrics that complement traditional duration measurements",
                            f"h) Provide metrics that complement traditional duration measurements\n   i) {custom_direction}"
                        )
                    elif type == "occurrency":
                        prompt = prompt.replace(
                            "h) Provide metrics that complement traditional frequency measurements",
                            f"h) Provide metrics that complement traditional frequency measurements\n   i) {custom_direction}"
                        )
                response = get_completion(client, prompt.format(dataframe, activities, list_variants, description, goal, my_activity))
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{nome_file}_{type}_fallback.txt", mode='w+', dir=tempfile.gettempdir()) as temp_file:
                    temp_file.write(my_activity + " (Fallback Analysis)\n")
                    temp_file.write(response + "\n\n")
                    temp_file_path = temp_file.name
                    
        except FileNotFoundError:
            # If fallback prompts don't exist, use a generic alternative approach
            custom_requirement = f"\n            6. {custom_direction}" if custom_direction.strip() else ""
            
            generic_prompt = f"""
            Analyze the event log and discover alternative Process Performance Indicators for the activity '{my_activity}'.
            
            Event Log Data: {dataframe}
            Activities: {activities}
            Variants: {list_variants}
            Description: {description}
            Goal: {goal}
            
            Focus on discovering PPIs using these alternative approaches:
            1. Cross-activity relationships and dependencies
            2. Process bottleneck identification
            3. Resource utilization patterns
            4. Quality and compliance metrics
            5. Predictive indicators for process optimization{custom_requirement}
            
            Provide a list of innovative PPIs that complement traditional {'time-based' if type == 'time' else 'frequency/percentage-based'} metrics.
            
            Format your response as:
            {my_activity} (Alternative Analysis):
            1) PPI 1
            2) PPI 2
            ...
            """
            
            response = get_completion(client, generic_prompt)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{nome_file}_{type}_fallback.txt", mode='w+', dir=tempfile.gettempdir()) as temp_file:
                temp_file.write(my_activity + " (Fallback Analysis)\n")
                temp_file.write(response + "\n\n")
                temp_file_path = temp_file.name
    else:
        response = "The activity is not in the log."
        temp_file_path = None
        
    return response, temp_file_path


def exec_with_fallback(dataframe, acti, varianti, activities, category, description, goal, attribute_array, nome_file, client, custom_direction=""):
    """
    Execute PPI discovery with fallback mechanism.
    First runs the standard approach, then adds fallback analysis for enhanced insights.
    """
    # Run standard PPI discovery
    listaKPI, temp_file_path = findPPI(dataframe, acti, varianti, activities, category, description, goal, nome_file, client)
    _, file_path_input = translatePPI(listaKPI, activities, attribute_array, nome_file, category, client)
    extracted_data = extract_ppi_json(file_path_input, category)
    modify_file(extracted_data)
    clean_data(extracted_data)
    
    # Run fallback analysis
    fallback_response, fallback_temp_path = findPPI_fallback(dataframe, acti, varianti, activities, category, description, goal, nome_file, client, custom_direction)
    
    if fallback_temp_path:
        # Translate fallback PPIs
        _, fallback_file_path_input = translatePPI(fallback_response, activities, attribute_array, nome_file + "_fallback", category, client)
        if fallback_file_path_input:
            fallback_extracted_data = extract_ppi_json(fallback_file_path_input, category)
            modify_file(fallback_extracted_data)
            clean_data(fallback_extracted_data)
            
            # Merge results - combine both standard and fallback PPIs
            with open(extracted_data, 'r') as f:
                standard_data = json.load(f)
            
            with open(fallback_extracted_data, 'r') as f:
                fallback_data = json.load(f)
            
            # Combine the data
            combined_data = standard_data + fallback_data
            
            # Save combined results
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{nome_file}_{category}_combined.json", mode='w+', dir=tempfile.gettempdir()) as temp_file:
                json.dump(combined_data, temp_file, indent=4)
                combined_file_path = temp_file.name
            
            return combined_file_path
    
    return extracted_data


def exec(dataframe, acti, varianti, activities, category, description, goal, attribute_array, nome_file, client):
    listaKPI,temp_file_path =findPPI(dataframe,acti,varianti,activities,category,description,goal,nome_file, client)
    _, file_path_input = translatePPI(listaKPI,activities,attribute_array,nome_file,category,client)
    extracted_data = extract_ppi_json(file_path_input,category)
    modify_file(extracted_data)
    clean_data(extracted_data)
    return extracted_data
    #probando_json = "results_2_prompt/resultIncidentManagement.xes_time_2_prompt.json"
    #return probando_json

#print("\n\n")

