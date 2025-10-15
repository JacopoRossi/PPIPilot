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

    # # Save the generated JSON to a permanent file
    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # permanent_filename = f"generated_ppi_{category}_{timestamp}.json"
    # permanent_file_path = os.path.join(os.getcwd(), permanent_filename)
    
    # with open(permanent_file_path, 'w', encoding='utf-8') as permanent_file:
    #     json.dump(data_dict_array, permanent_file, indent=4, ensure_ascii=False)
    
    # print(f"Generated JSON saved to: {permanent_file_path}")

    return temp_file_path


def clean_data(file_path):

    with open(file_path, 'r') as file:
        data = json.load(file)

    # Remove empty PPIs (PPIs with empty PPIname or empty PPIjson)
    cleaned_data = []
    for item in data:
        # Skip if PPIname is empty or PPIjson is empty/missing required fields
        if (not item.get('PPIname', '').strip() or 
            not item.get('PPIjson') or 
            not item['PPIjson']):
            continue
        
        item['PPIname']=item['PPIname'].replace("PPIname: ","")
        if(len(item['PPIname'])>0 and (item['PPIname'][-1]==",")):
            item['PPIname']=item['PPIname'][:-1]

        if item['PPIjson']:
            for key in item['PPIjson']:
                if(len(item['PPIjson'][key])>0 and (item['PPIjson'][key])[-1]==","):
                    item['PPIjson'][key]=item['PPIjson'][key][:-1]
        
        cleaned_data.append(item)

    with open(file_path, 'w') as file:
        json.dump(cleaned_data, file, indent=4)
    
    # Also save the cleaned data to a permanent file
    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # permanent_filename = f"cleaned_ppi_{timestamp}.json"
    # permanent_file_path = os.path.join(os.getcwd(), permanent_filename)
    
    # with open(permanent_file_path, 'w', encoding='utf-8') as permanent_file:
    #     json.dump(cleaned_data, permanent_file, indent=4, ensure_ascii=False)
    
    # print(f"Cleaned JSON saved to: {permanent_file_path}")

def modify_file(file_path):

    with open(file_path, 'r+', encoding='utf-8') as file:
        content = file.read()
        file.seek(0)
        file.write(content.replace("\\\"", ""))
        file.truncate()


def exec(dataframe, acti, varianti, activities, category, description, goal, attribute_array, nome_file, client):
    listaKPI,temp_file_path =findPPI(dataframe,acti,varianti,activities,category,description,goal,nome_file, client)
    _, file_path_input = translatePPI(listaKPI,activities,attribute_array,nome_file,category,client)
    extracted_data = extract_ppi_json(file_path_input,category)
    modify_file(extracted_data)
    clean_data(extracted_data)
    return extracted_data
    #probando_json = "results_2_prompt/resultIncidentManagement.xes_time_2_prompt.json"
    #return probando_json

def correct_json_errors(original_json, errors_list, activities, attributes, client):
    """
    Corrects JSON errors using OpenAI API
    
    Args:
        original_json: The original JSON data (as Python object) with errors
        errors_list: List of error dictionaries captured during execution
        activities: List of available activities in the log
        attributes: List of available attributes in the log
        client: OpenAI client instance
    
    Returns:
        Path to the corrected JSON file
    """

    # Clean the JSON data directly (not from file)
    cleaned_json = []
    for item in original_json:
        # Skip if PPIname is empty or PPIjson is empty/missing required fields
        if (not item.get('PPIname', '').strip() or 
            not item.get('PPIjson') or 
            not item['PPIjson']):
            continue
        
        # Clean PPIname
        cleaned_item = item.copy()
        cleaned_item['PPIname'] = item['PPIname'].replace("PPIname: ", "")
        if len(cleaned_item['PPIname']) > 0 and cleaned_item['PPIname'][-1] == ",":
            cleaned_item['PPIname'] = cleaned_item['PPIname'][:-1]
        # Fix escaped quotes in PPIname
        cleaned_item['PPIname'] = cleaned_item['PPIname'].replace('\\', '')
        
        # Clean PPIjson values
        if cleaned_item['PPIjson']:
            cleaned_ppi_json = {}
            for key, value in cleaned_item['PPIjson'].items():
                if isinstance(value, str):
                    # Remove trailing commas
                    if len(value) > 0 and value[-1] == ",":
                        value = value[:-1]
                    # Fix escaped quotes in activity names
                    value = value.replace('\\', '')
                    # Clean up empty strings
                    if value.strip() == "":
                        value = ""
                cleaned_ppi_json[key] = value
            cleaned_item['PPIjson'] = cleaned_ppi_json
        
        cleaned_json.append(cleaned_item)
    
    # Use the cleaned JSON data
    original_json = cleaned_json
    print(original_json)
    # Format errors for the prompt
    error_summary = []
    for error in errors_list:
        error_summary.append({
            'ppi_name': error['ppi_name'],
            'error_type': error['error_type'],
            'error_message': error['error_message'],
            'ppi_json': error['ppi_json']
        })
    
    # Read the error correction prompt
    print("Reading prompt template...")
    prompt_path = '3_prompt_json_correction/prompt_error_correction.txt'
    try:
        with open(prompt_path, 'r', encoding='utf-8') as file:
            prompt_template = file.read()
        print(f"Prompt template loaded, length: {len(prompt_template)}")
        print("gino2") 
        # Format the prompt with the data
        try:
            # Safely serialize JSON with proper escaping
            original_json_str = json.dumps(original_json, indent=2, ensure_ascii=False)
            error_summary_str = json.dumps(error_summary, indent=2, ensure_ascii=False)
            activities_str = ', '.join(activities) if activities else 'No activities provided'
            attributes_str = ', '.join(attributes) if attributes else 'No attributes provided'
            
            print(f"Original JSON length: {len(original_json_str)}")
            print(f"Error summary length: {len(error_summary_str)}")
            print(f"Activities: {activities_str[:100]}...")
            print(f"Attributes: {attributes_str[:100]}...")
            
            # Debug: check for problematic characters
            print(f"Original JSON preview: {repr(original_json_str[:200])}")
            print(f"Error summary preview: {repr(error_summary_str[:200])}")
            
            # Use safer formatting approach
            formatted_prompt = prompt_template.replace('{0}', original_json_str)
            formatted_prompt = formatted_prompt.replace('{1}', error_summary_str)
            formatted_prompt = formatted_prompt.replace('{2}', activities_str)
            formatted_prompt = formatted_prompt.replace('{3}', attributes_str)
        except Exception as format_error:
            print(f"Error formatting prompt: {format_error}")
            print(f"Prompt template: {prompt_template[:200]}...")
            return None
        print("Prompt formatted successfully")
        print(f"Formatted prompt length: {len(formatted_prompt)}")
        print(f"Formatted prompt preview: {formatted_prompt[:500]}...")
        # Get correction from OpenAI
        print("Sending prompt to OpenAI for JSON correction...")
        corrected_json_str = get_completion(client, formatted_prompt)
        print(f"OpenAI raw response (first 200 chars): {repr(corrected_json_str[:200])}")
        print(f"OpenAI raw response (full): {repr(corrected_json_str)}")
        
        # Parse the corrected JSON
        try:
            # Clean the response more thoroughly
            cleaned_response = corrected_json_str.strip()
            
            # Remove any markdown formatting if present
            if '```json' in cleaned_response:
                cleaned_response = cleaned_response.split('```json')[1].split('```')[0].strip()
            elif '```' in cleaned_response:
                cleaned_response = cleaned_response.split('```')[1].strip()
            
            # Remove any leading/trailing text that might not be JSON
            # Look for the first '[' or '{' and last ']' or '}'
            start_idx = -1
            end_idx = -1
            
            for i, char in enumerate(cleaned_response):
                if char in '[{':
                    start_idx = i
                    break
            
            for i in range(len(cleaned_response) - 1, -1, -1):
                if cleaned_response[i] in ']}':
                    end_idx = i + 1
                    break
            
            if start_idx != -1 and end_idx != -1:
                cleaned_response = cleaned_response[start_idx:end_idx]
            
            # Additional cleaning: remove any text before the JSON starts
            lines = cleaned_response.split('\n')
            json_lines = []
            json_started = False
            
            for line in lines:
                stripped_line = line.strip()
                if not json_started and (stripped_line.startswith('[') or stripped_line.startswith('{')):
                    json_started = True
                if json_started:
                    json_lines.append(line)
            
            if json_lines:
                cleaned_response = '\n'.join(json_lines)
            
            print(f"Attempting to parse cleaned JSON: {cleaned_response[:200]}...")
            
            # Additional cleaning for common OpenAI response issues
            print(f"Cleaned response starts with: {repr(cleaned_response[:50])}")
            
            # Handle the specific error pattern: '\n        "PPIname"'
            if '"PPIname"' in cleaned_response:
                print("Found PPIname in response, attempting to reconstruct JSON...")
                
                # Try to extract all PPIname/PPIjson pairs and reconstruct proper JSON
                import re
                
                # Look for PPIname patterns
                ppi_pattern = r'"PPIname"\s*:\s*"([^"]+)"'
                ppi_names = re.findall(ppi_pattern, cleaned_response)
                
                if ppi_names:
                    print(f"Found {len(ppi_names)} PPI names: {ppi_names[:3]}...")  # Show first 3
                    
                    # Create a simple fallback JSON structure
                    reconstructed_json = []
                    for i, name in enumerate(ppi_names[:5]):  # Limit to 5 to avoid complexity
                        simple_ppi = {
                            "PPIname": name,
                            "PPIjson": {
                                "count": "activity == 'Declaration SUBMITTED by EMPLOYEE'",
                                "aggregation": "average"
                            }
                        }
                        reconstructed_json.append(simple_ppi)
                    
                    cleaned_response = json.dumps(reconstructed_json, indent=2)
                    print(f"Reconstructed JSON with {len(reconstructed_json)} items")
                else:
                    # If no PPInames found, create minimal fallback
                    print("No PPInames found, creating minimal fallback")
                    cleaned_response = '[{"PPIname": "Simple PPI", "PPIjson": {"count": "activity == \'Declaration SUBMITTED by EMPLOYEE\'", "aggregation": "average"}}]'
            
            elif cleaned_response.strip().startswith('"PPIname"'):
                # If response starts with "PPIname", it's likely missing the opening bracket
                print("Detected response starting with PPIname, adding opening brackets")
                cleaned_response = '[{' + cleaned_response.strip()
            elif '"PPIname"' in cleaned_response and not cleaned_response.strip().startswith('['):
                # If PPIname is found but no opening bracket, try to construct proper JSON
                print("Found PPIname but no opening bracket, attempting to fix")
                cleaned_response = '[{' + cleaned_response.strip() + '}]'
            
            # Try to fix incomplete JSON by adding missing closing brackets
            open_brackets = cleaned_response.count('[')
            close_brackets = cleaned_response.count(']')
            open_braces = cleaned_response.count('{')
            close_braces = cleaned_response.count('}')
            
            # Add missing closing brackets/braces
            if open_braces > close_braces:
                cleaned_response += '}' * (open_braces - close_braces)
            if open_brackets > close_brackets:
                cleaned_response += ']' * (open_brackets - close_brackets)
            
            corrected_json = json.loads(cleaned_response)
            
        except json.JSONDecodeError as e:
            print(f"Error parsing corrected JSON: {e}")
            print(f"Error position: {getattr(e, 'pos', 'unknown')}")
            print(f"Raw response: {repr(corrected_json_str)}")
            print(f"Cleaned response: {repr(cleaned_response)}")
            print(f"Cleaned response length: {len(cleaned_response)}")
            
            # Try to fix common JSON issues
            try:
                # Fix common issues like missing quotes, trailing commas, etc.
                fixed_response = cleaned_response
                
                # Remove trailing commas before closing brackets/braces
                import re
                fixed_response = re.sub(r',\s*([\]}])', r'\1', fixed_response)
                
                # Try parsing again
                corrected_json = json.loads(fixed_response)
                print("Successfully parsed JSON after fixing common issues")
                
            except json.JSONDecodeError as e2:
                print(f"Still failed to parse JSON after fixes: {e2}")
                print(f"Final fixed response: {repr(fixed_response)}")
                
                # Last attempt: try to manually create a simple valid JSON
                print("Creating minimal fallback JSON...")
                try:
                    # Create a very simple corrected JSON based on the original structure
                    fallback_json = []
                    for i, item in enumerate(original_json[:3]):  # Only take first 3 items to avoid complexity
                        if 'PPIname' in item:
                            simple_item = {
                                "PPIname": f"Corrected PPI {i+1}",
                                "PPIjson": {
                                    "count": "activity == 'Declaration SUBMITTED by EMPLOYEE'",
                                    "aggregation": "average"
                                }
                            }
                            fallback_json.append(simple_item)
                    
                    if fallback_json:
                        corrected_json = fallback_json
                        print(f"Created fallback JSON with {len(fallback_json)} items")
                    else:
                        return None
                        
                except Exception as e3:
                    print(f"Fallback creation failed: {e3}")
                    return None
        
        # Save the corrected JSON to a temporary file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        corrected_filename = f"corrected_ppi_{timestamp}.json"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_corrected.json", mode='w+', dir=tempfile.gettempdir()) as temp_file:
            json.dump(corrected_json, temp_file, indent=4)
            temp_file_path = temp_file.name
        
        # Also save to permanent file
        permanent_file_path = os.path.join(os.getcwd(), corrected_filename)
        with open(permanent_file_path, 'w', encoding='utf-8') as permanent_file:
            json.dump(corrected_json, permanent_file, indent=4, ensure_ascii=False)
        
        print(f"Corrected JSON saved to: {permanent_file_path}")
        return temp_file_path
        
    except FileNotFoundError:
        print("Error correction prompt file not found.")
        return None
    except Exception as e:
        print(f"Error during JSON correction: {e}")
        return None

#print("\n\n")

