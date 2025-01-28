"""

This script will read through all the directories included in the input path.

It shall:
1. Create a log that has an output on when the file was picked up by the script with it's filename and log if any error persist during the pickup of the file.
2. It should create multiple report files for a complete day and contain below details:
    a. Report 1: Location wise total recharge amount for a complete day
    b. Report 2: Category-wise total recharge amount for a complete day
    b. Report 3: Total cash, card, and payment.
    
"""

import logging.handlers
import os
import tomli
import pandas as pd
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import psycopg2

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

def import_input_path(config):
    
    """
    This function will import the input path given in the config file.

    Args:
        config (dict): .toml file for the inputs

    Returns:
        input_path (dir): Returns the input path from the config file
    """
    
    input_path = config["directories"]["input_path"]
    
    return input_path

def import_log_path(config):
    
    """
    This function will import the log path given in the config file.

    Args:
        config (dict): .toml file for the inputs

    Returns:
        log_path (dir): Returns the log path from the config file
    """
    
    log_path = config["directories"]["log_path"]
    
    return log_path

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
    
    try:
        matched_files = []
        for file in files:
            if file.find(formatted_date) != -1:
                if file.endswith('.csv'):
                    matched_files.append(file)
        
        return matched_files
    
    except Exception as e:
        script_log.error("An error occured: {e}")

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
    
    try:
        csv_list = []
        for file in files:
            df = read_csv(file)
            csv_list.append(df)
            
        combined_df = pd.concat(csv_list, ignore_index=True)
        
        return combined_df
    
    except Exception as e:
        script_log.error(f"An error has occured: {e}\n")

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
    total_pm_count = len(pm_data)
    
    return total_pm_count

def initialize_logger(log_path, log_filename, logger_type):
    """
    Initializes a logger with a custom naming format for rotated files.
    
    Args:
        log_path (dir): Directory path for logs.
        log_filename (str): Base filename for the logs.
        logger_type (str): Logger type for distinguishing logs.

    Returns:
        logging.Logger: Configured logger instance.
    """

    os.makedirs(log_path, exist_ok=True)
    log_file = os.path.join(log_path, log_filename)
    
    logger = logging.getLogger(logger_type)
    logger.setLevel(logging.INFO)

    handler = TimedRotatingFileHandler(log_file, when="s", interval=5, backupCount=7)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s : %(message)s")
    handler.setFormatter(formatter)
    #handler.suffix = "%d-%m-%Y_%H-%M-%S.log"
    logger.addHandler(handler)

    return logger



def get_location_recharge_data(log_path, combined_df):
    """
    This function will output the data collected from the combined data frame via log

    Args:
        log_path (dir): Directory where the log will be outputted
        combined_df (pandas.core.frame.DataFrame): Data frame containing the combined data of "Location" and "RechargeAmount"
    """
    
    current_date = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    log_file_name = f"loc_and_total_recharge_amt - {current_date}.log"
    loc_logger = initialize_logger(log_path, log_file_name, "location_handler")
    
    location_and_recharge = location_and_recharge_df(combined_df)
    
    x10_data = stats_loc_recharge(location_and_recharge, "X10")
    x11_data = stats_loc_recharge(location_and_recharge, "X11")
    x12_data = stats_loc_recharge(location_and_recharge, "X12")
    x13_data = stats_loc_recharge(location_and_recharge, "X13")
    
    loc_logger.info(f"Analyzing Location and RechargeAmount data as of {current_date}...\n")
    loc_logger.info("Here is the data for total RechargeAmount per Location:")
    loc_logger.info(f"Location\t Total_RechargeAmount")
    loc_logger.info(f"X10:\t\t {x10_data}")
    loc_logger.info(f"X11:\t\t {x11_data}")
    loc_logger.info(f"X12:\t\t {x12_data}")
    loc_logger.info(f"X13:\t\t {x13_data}")
    
def get_category_recharge_data(log_path, combined_df):
    """
    This function will output the data collected from the combined data frame via log

    Args:
        log_path (dir): Directory where the log will be outputted
        combined_df (pandas.core.frame.DataFrame): Data frame containing the combined data of "Category" and "RechargeAmount"
    """
    
    current_date = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    log_file_name = f"cat_and_total_recharge_amt - {current_date}.log"
    cat_logger = initialize_logger(log_path, log_file_name, "category_handler")
    
    cat_and_recharge = category_and_recharge_df(combined_df)
    
    
    yth_data = stats_cat_recharge(cat_and_recharge, "YTH")
    std_data = stats_cat_recharge(cat_and_recharge, "STD")
    bsc_data = stats_cat_recharge(cat_and_recharge, "BSC")
    spl_data = stats_cat_recharge(cat_and_recharge, "SPL")
    
    cat_logger.info(f"Analyzing Category and RechargeAmount data as of {current_date}...\n")
    cat_logger.info("Here is the data for total RechargeAmount per Category:")
    cat_logger.info(f"Category\t Total_RechargeAmount")
    cat_logger.info(f"YTH:\t\t {yth_data}")
    cat_logger.info(f"STD:\t\t {std_data}")
    cat_logger.info(f"BSC:\t\t {bsc_data}")
    cat_logger.info(f"SPL:\t\t {spl_data}")
    
def get_payment_method_data(log_path, combined_df):
    """
    This function will output the data collected from the data frame via log

    Args:
        log_path (dir): Directory where the log will be outputted
        combined_df (pandas.core.frame.DataFrame): Data frame containing the data of "PaymentMethod"
    """
    
    current_date = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    log_file_name = f"payment_method_count - {current_date}.log"
    pm_logger = initialize_logger(log_path, log_file_name, "payment_handler")
    
    payment = payment_method_df(combined_df)
    
    
    cash_data = stats_payment_method(payment, 1)
    cc_data = stats_payment_method(payment, 2)
    paytm_data = stats_payment_method(payment, 3)

    pm_logger.info(f"Analyzing Location and RechargeAmount data as of {current_date}...\n")
    pm_logger.info("Here is the data for total RechargeAmount per Location:")
    pm_logger.info(f"PaymentMethod\t\t Total_Count")
    pm_logger.info(f"Cash:\t\t\t\t {cash_data}")
    pm_logger.info(f"Credit Card:\t\t {cc_data}")
    pm_logger.info(f"Paytm:\t\t\t\t {paytm_data}")

def connect_to_db(config):
    """
    This function will create a connection for the postgres db

    Args:
        config (dict): Config file (.toml) for the script

    Returns:
        connection (psycopg2.extensions.connection): Connection instance for accessing the postgres db
    """
    
    db_host = config["database"]["db_host"]
    db_name = config["database"]["db_name"]
    db_user = config["database"]["db_user"]
    db_password = config["database"]["db_password"]
    
    try:
        connection = psycopg2.connect(
            dbname = db_name,
            user = db_user,
            password = db_password,
            host = db_host
        )

        script_log.info(f"Creating connection for user:{db_user} to database:{db_name}")
        script_log.info(f"Connection status: {connection.status}\n")

        return connection
    
    except Exception as e:
        script_log.error(f"An error occured: {e}")

def open_cursor_db(connection):
    """
    This function will create a cursor instance to be able to execute commands

    Args:
        connection (psycopg2.extensions.connection): Connection instance for accessing the postgres db

    Returns:
        cursor (psycopg2.extensions.cursor): Cursor instance for executing commands 
    """
    
    try:
        cursor = connection.cursor()
        script_log.info("Creating cursor for command execution...")
        return cursor
    
    except Exception as e:
        script_log.error(f"An error has occured: {e}")

def create_table(cursor):
    """
    This function executes a PostgreSQL query to create a table

    Args:
        cursor (extensions): Cursor instance for executing commands
    """
    
    try:
        
        script_log.info("Creating table...")
        
        query = "CREATE TABLE IF NOT EXISTS logs (id SERIAL PRIMARY KEY, file_name VARCHAR(255), log_content TEXT);"
        script_log.info(f"Executing query to create table 'logs' if not exists.")
        cursor.execute(query)
        
        script_log.info("Table created or already exists.\n")
        
    except Exception as e:
        script_log.error(f"An error occured: {e}\n")

def insert_entire_logs(cursor, log_folder):
    try:
        for file_name in os.listdir(log_folder):
            file_path = os.path.abspath(os.path.join(log_folder, file_name))
            if os.path.isfile(file_path) and file_name.endswith(".log"):
                with open(file_path, 'r') as file:
                    content = file.read()
                    cursor.execute("INSERT INTO logs (file_name, log_content) VALUES (%s, %s);", (file_name, content))
            script_log.info(f"Inserted log file: {file_name} as a single row.")
    
    except Exception as e:
        script_log.error(f"Failed to insert log file: {e}\n")
        
def main():
    
    config = import_config_file()
    input_path = import_input_path(config)
    log_path = import_log_path(config)
    
    csv_files_to_read = get_csv_files_to_read(input_path)
    combined_df = combine_matched_csv(csv_files_to_read)
    send_to_database_operation = config["operation"]["send_to_database"]
    
    try:
        script_log.info("Analyzing 'Location' and 'RechargeAmount' data...")
        get_location_recharge_data(log_path, combined_df)
        script_log.info("Done with the analysis. Refer to the logs for details.\n")
    except Exception as e:
        script_log.error(f"An error occured while analyzing 'Location' and 'RechargeAmount' data: {e}\n")
    
    try:    
        script_log.info("Analyzing 'Category' and 'RechargeAmount' data...")
        get_category_recharge_data(log_path, combined_df)
        script_log.info("Done with the analysis. Refer to the logs for details.\n")
    except Exception as e:
        script_log.error(f"An error occured while analyzing 'Category' and 'RechargeAmount' data: {e}\n")
    
    try:
        script_log.info("Analyzing 'PaymentMethod' data...")
        get_payment_method_data(log_path, combined_df)
        script_log.info("Done with the analysis. Refer to the logs for details.\n")
    except Exception as e:
        script_log.error(f"An error occured while analyzing 'Payment' data: {e}\n")
    
    if send_to_database_operation == "YES":
        script_log.info(f"Operation send_to_database: {send_to_database_operation}")
        script_log.info("Executing transfer...")
        try:    
            db_connection = connect_to_db(config)
            db_cursor = open_cursor_db(db_connection)
            create_table(db_cursor)
            insert_entire_logs(db_cursor, log_path)
            db_connection.commit()
            
        except Exception as e:
            script_log.warning(f"An error has occured: {e}")
        finally:
            script_log.info("Closing connection...")
            db_cursor.close()
            db_connection.close()
            script_log.info("Connection closed.")
    
    script_log.info(f"Operation send_to_database: {send_to_database_operation}")
    script_log.info("Skipping copying of files to postgres database...")
    
if __name__ == "__main__":
    config = import_config_file()
    log_path = import_log_path(config)
    current_date = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    script_log = initialize_logger(log_path, f"recharge_file_reader - {current_date}.log", "script_handler")
    
    script_log.info("##############################################################################")
    script_log.info("Script is called...")
    script_log.info("##############################################################################\n")
    
    main()
    
    script_log.info("##############################################################################")
    script_log.info("Script executed...")
    script_log.info("##############################################################################\n")