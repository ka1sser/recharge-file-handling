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
        files_with_path (list): List containing all the files within the sub directories
    """
    
    sub_dirs = get_sub_dir(input_path)
    
    files_with_path = []
    for sub_dir in sub_dirs:
        files_in_sub_dir = os.listdir(sub_dir)
        for file in files_in_sub_dir:
            file_path = os.path.abspath(os.path.join(sub_dir, file))
            files_with_path.append(file_path)
            
    return files_with_path

def get_base_name(files):
    """
    This function gets the basename of the file path

    Args:
        files (list): List of file paths

    Returns:
        list_of_basename (list): List of strings of basename
    """
    list_of_basename = []
    for file in files:
        list_of_basename.append(os.path.basename(file))
        
    return list_of_basename

def check_filename(files):
    
    """
    This function checks the filename that has the current date of when the script
    was executed. The date format %d%m%Y outputs DDMMYYYY (ex. 27012025)

    Args:
        files (list): This argument should be a list containing the filenames
                      to be checked.

    Returns:
        matched_files (list): Returns a list of matching file names
    """
    
    current_date = datetime.now()
    formatted_date = current_date.strftime("%d%m%Y")
    
    matched_files = []
    for file in files:
        if file.find(formatted_date) != -1:
            if file.endswith('.csv'):
                matched_files.append(file)
    
    return matched_files

def get_csv_files_to_read(input_path):
    """
    This function will get the csv files in different directories that matches the current date.

    Args:
        input_path (dir): Directory of the input path

    Returns:
        csv_files_to_read (list): Returns a list containing the file path of the csv files
    """
    
    files_in_path = combined_files_per_dir(input_path)
    filenames = get_base_name(files_in_path)
    matched_files = check_filename(filenames)

    csv_files_to_read = []
    for file in matched_files:
        for file_path in files_in_path:
            if file_path.find(file) != -1:
                csv_files_to_read.append(file_path)
                
    return csv_files_to_read
   
def read_csv(file):
    """
    This function reads and loads the csv file.

    Args:
        file (str): This input should be the file path for the

    Returns:
        csv (pandas.core.frame.DataFrame): Returns the csv via pandas dataframe
    """
    
    csv = pd.read_csv(file)
    
    return csv

def combine_matched_csv(files):
    """
    This function will combine all the csv files data in one big df

    Args:
        files (list): List of csv file path that matches the current date

    Returns:
        combined_df (pandas.core.frame.DataFrame): Returns a data frame with combined data from all the listed csv files
    """
    csv_list = []
    for file in files:
        df = read_csv(file)
        csv_list.append(df)
        
    combined_df = pd.concat(csv_list, ignore_index=True)
    
    return combined_df

def location_and_recharge_df(data):
    """
    This function isolates the data with "Location" and "RechargeAmount" as the key or header to the column.
    It creates a new data frame using the these columns.

    Args:
        data (pandas.core.frame.DataFrame): Argument should be a dataframe that contains the data

    Returns:
        location_and_recharge (pandas.core.frame.DataFrame): Returns a new data frame that only consist
                                                            of "Location" and "RechargeAmount"
    """
    
    df = pd.DataFrame(data)
    location_and_recharge = df[["Location", "RechargeAmount"]]
    
    return location_and_recharge

def stats_loc_recharge(data, loc):
    """
    This function gets the sum of "RechargeAmount" per "Location"

    Args:
        data (pandas.core.frame.DataFrame): Data frame that contains the "Location" and "RechargeAmount" data columns
        loc (str): A string containing the value from "Location" namely "X10", "X11", "X12", and "X13"

    Returns:
        loc_data_total_recharge (int): Sum of the total "RechargeAmount" from data that has the value inputted in loc
    """
    
    
    loc_data = data[data["Location"] == loc]
    loc_data_total_recharge = loc_data["RechargeAmount"].sum()
    
    return loc_data_total_recharge
    
def category_and_recharge_df(data):
    """
    This function isolates the data with "Category" and "RechargeAmount" as the key or header to the column.
    It creates a new data frame using the these columns.

    Args:
        data (pandas.core.frame.DataFrame): Argument should be a dataframe that contains the data

    Returns:
        category_and_recharge (pandas.core.frame.DataFrame): Returns a new data frame that only consist
                                                            of "Category" and "RechargeAmount"
    """

    df = pd.DataFrame(data)
    category_and_recharge = df[["Category", "RechargeAmount"]]

    return category_and_recharge

def stats_cat_recharge(data, cat):
    """
    This function gets the sum of "RechargeAmount" per "Category"

    Args:
        data (pandas.core.frame.DataFrame): Data frame that contains the "Category" and "RechargeAmount" data columns
        cat (str): A string containing the value from "Category" namely "YTH", "STD", "BSC", and "SPL"

    Returns:
        cat_data_total_recharge (int): Sum of the total "RechargeAmount" from data that has the value inputted in cat
    """
    
    cat_data = data[data["Category"] == cat]
    cat_data_total_recharge = cat_data["RechargeAmount"].sum()
    
    return cat_data_total_recharge

def payment_method_df(data):
    """
    This function isolates the data with "PaymentMethod" as the key or header to the column.
    It creates a new data frame using the this column.

    Args:
        data (pandas.core.frame.DataFrame): Argument should be a dataframe that contains the data

    Returns:
        payment_method (pandas.core.frame.DataFrame): Returns a new data frame that only consist of "PaymentMethod"
    """
    
    df = pd.DataFrame(data)
    payment_method = df[["PaymentMethod"]]

    return payment_method


def stats_payment_method(data, pm):
    """
    This function gets the count of "PaymentMethod" per value

    Args:
        data (pandas.core.frame.DataFrame): Data frame that contains the "PaymentMethod" data column
        pm (int): An int containing the value from "PaymentMethod" namely 1, 2, and 3

    Returns:
        total_pm_count (int): Count of the inputted pm
    """
    
    pm_data = data[data["PaymentMethod"] == pm]
    total_pm_count = pm_data.count()
    
    return total_pm_count

        
def main():
    
    config = import_config_file()
    input_path = import_file_path(config)
    
    csv_files_to_read = get_csv_files_to_read(input_path)
    combined_df = combine_matched_csv(csv_files_to_read)
    
    
    
if __name__ == "__main__":
    
    main()