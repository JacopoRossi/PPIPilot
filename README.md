## Requirements

The code has been tested using **Python 3.8.12**.

## Set Up before using the code

It is possible to use the already defined conda environment.

After having installed **Conda** or **Miniconda**, download the Github project, open the terminal or an Anaconda Prompt, change directory to go to the location where the file "env.yml" is located and do the following steps:

1. Create the environment from the env.yml file:

```
conda env create -f env.yml
```

The first line of the yml file sets the new environment's name, in this case "ppi_env"

2. Activate the new environment:

```
conda activate ppi_env
```

3. Verify that the new environment was installed correctly:

```
conda env list
```

or

```
conda info --envs.
```

## Folder description

- **1_prompt_description_goal** contains the files with the prompt to discover PPIs related to time, frequency and percentage. In this prompt it is required a description of the event log and a goal to make a more specific action.
- **2_prompt** contains the files with the prompt to translate PPIs from natural language to a JSON format.

## To use the code

1. Open terminal or Anaconda Prompt.
2. Activate "ppi_env".
3. Run: ``streamlit run interface_2.py`` in terminal or prompt;
4. Follow the program instructions

## Link

At this link https://drive.google.com/drive/folders/14mjxtRH7dEKFVSoSQx0eGaPAlQiYJw37?usp=sharing, you can find the DomesticDeclarations.xes, the IT_incident_management.xes and the Manuscript_review_management.xes with a relative example of description and goal
