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

def check_files_per_dir(input_path):
    
    """
    This function will check the files in each directory and compile it in one list.

    Returns:
        files (list): List containing all the files within the sub directories
    """
    
    sub_dirs = get_sub_dir(input_path)
    
    files = []
    for sub_dir in sub_dirs:
        files_in_dir = os.listdir(sub_dir)
        files = files + files_in_dir

    return files
    
def import_csv(csv_file):
    
    dataset_raw = pd.read_csv(csv_file)
    
    return dataset_raw

def main():
    
    config = import_config_file()
    input_path = import_file_path(config)
    print(type(config))
    print()
    print(check_files_per_dir(input_path))
    
if __name__ == "__main__":
    
    main()