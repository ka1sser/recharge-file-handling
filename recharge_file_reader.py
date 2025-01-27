"""
This script will read through all the directories included in the input path.

It shall:
1. Create a log that has an output on when the file was picked up by the script with it's filename and log if any error persist during the pickup of the file.
2. It should create multiple report files for a complete day and contain below details:
    a. Report 1: Location wise total recharge amount for a complete day
    b. Report 2: Category-wise total recharge amount for a complete day
    b. Report 3: Total cash, card, and payment.
"""
import os
import tomli
import pandas as pd
from datetime import datetime
import glob

def import_config_file():
    
    """
    This function will import and initialize the specified config file to the script.
    This file will give the inputs for the script

    Returns:
        config (dict): .toml config file for the inputs
    """
    
    with open("recharge_file_config.toml", "rb") as file:
        config = tomli.load(file)
        
    return config

def import_file_path(config):
    
    """
    This function will import the file path given in the config file.

    Args:
        config (dict): .toml file for the inputs

    Returns:
        input_path (dir): Returns the input path from the config file
    """
    
    input_path = config["directories"]["input_path"]
    
    return input_path

def get_sub_dir(input_path):
    
    """
    This function will get all the subdirectories in the input path.

    Args:
        input_path (dir): Input path from the config file that contains the subdirectories.

    Returns:
        list_sub_dir (list): List of existing subdirectories
    """
    
    get_sub_dir = os.listdir(input_path)
    
    list_sub_dir = []
    for sub_dir in get_sub_dir:
        sub_dir = os.path.join(input_path, sub_dir)
        list_sub_dir.append(sub_dir)

    return list_sub_dir

def combined_files_per_dir(input_path):
    
    """
    This function will check the files in each directory and compile it in one list.

    Returns:
        files (list): List containing all the files within the sub directories
    """
    
    sub_dirs = get_sub_dir(input_path)
    
    files = []
    for sub_dir in sub_dirs:
        files_in_sub_dir = os.listdir(sub_dir)
        files = files + files_in_sub_dir

    return files

def check_filename(files):
    
    """
    This function checks the filename that has the current date of when the script
    was executed. The date format %d%m%Y outputs DDMMYYYY (ex. 27012025)

    Args:
        files (list): This argument should be a list containing the filenames
                      to be checked.

    Returns:
        matched_files (list): Returns a list of matching file names. To be os.path.joined() to
        the original path for it to be accessed properly.
    """
    
    current_date = datetime.now()
    formatted_date = current_date.strftime("%d%m%Y")
    
    matched_files = []
    for file in files:
        if file.find(formatted_date) != -1:
            matched_files.append(file)
    
    return matched_files
    
def read_csv(file):
    
    csv = pd.read_csv(file)
    
    return csv

def main():
    
    config = import_config_file()
    input_path = import_file_path(config)
    files = (combined_files_per_dir(input_path))
    
    matched_files = check_filename(files)
    #file = "C:/Users/eserkai/OneDrive - Ericsson/Documents/Programming/Python/Training/recharge-file-handling/sample_data/subdir_1/EventFile_Recharge_006_27012025_0926.csv"
        
    #csv = read_csv(file)
    #print(csv.head(3))
    #print(csv["Category"].head(5))
    
if __name__ == "__main__":
    
    main()