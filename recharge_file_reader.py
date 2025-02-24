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
import psycopg2.sql

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
    It creates a new data frame that has "Location" and "Total_RechargeAmount" as the values per location
    was summed.

    Args:
        data (pandas.core.frame.DataFrame): Argument should be a dataframe that contains the data

    Returns:
        location_and_total_recharge (pandas.core.frame.DataFrame): Returns a new data frame that consist
                                                            of "Location" and "Total_RechargeAmount"
    """
    
    df = pd.DataFrame(data)
    location_and_recharge = df[["Location", "RechargeAmount"]]
    location_and_total_recharge = location_and_recharge.groupby("Location", as_index=False).sum()
    location_and_total_recharge.rename(columns={"RechargeAmount": "Total_RechargeAmount"}, inplace=True)
    
    return location_and_total_recharge

def category_and_recharge_df(data):
    """
    This function isolates the data with "Category" and "RechargeAmount" as the key or header to the column.
    It creates a new data frame that has "Category" and "Total_RechargeAmount" as the values per category
    was summed.

    Args:
        data (pandas.core.frame.DataFrame): Argument should be a dataframe that contains the data

    Returns:
        category_and_total_recharge (pandas.core.frame.DataFrame): Returns a new data frame that consist
                                                            of "Category" and "Total_RechargeAmount"
    """

    df = pd.DataFrame(data)
    category_and_recharge = df[["Category", "RechargeAmount"]]
    category_and_total_recharge = category_and_recharge.groupby("Category", as_index=False).sum()
    category_and_total_recharge.rename(columns={"RechargeAmount": "Total_RechargeAmount"}, inplace=True)
    
    return category_and_total_recharge

def payment_method_df(data):
    """
    This function isolates the data with "PaymentMethod" as the key or header to the column.
    It creates a new data frame using the this column and the count for each payment method.

    Args:
        data (pandas.core.frame.DataFrame): Argument should be a dataframe that contains the data

    Returns:
        payment_method (pandas.core.frame.DataFrame): Returns a new data frame that consists of "PaymentMethod" and "Total_Count"
    """
    
    df = pd.DataFrame(data)
    payment_method_total = df.groupby("PaymentMethod", as_index=False).size()
    payment_method_total.rename(columns={"size": "Total_Count"}, inplace=True)
    
    """
    payment_method_total = df["PaymentMethod"].value_counts().reset_index()
    payment_method_total.columns = ["PaymentMethod", "Total_Count"]
    
    payment_mapping = {
        1: "Cash",
        2: "Credit Card",
        3: "Paytm"
    }
    
    payment_method_total["PaymentMethod"] = payment_method_total["PaymentMethod"].replace(payment_mapping)"""
    
    return payment_method_total


def save_to_csv(filename_prefix, csv_path, dataframe):
    """
    This function will create a csv file for the location_and_total_recharge dataframe

    Args:
        csv_path (dir): Directory for the csv_file path
        dataframe (pandas.core.frame.DataFrame): Dataframe consisting of "Location" and "Total_RechargeAmount"
    """
    current_date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    file_name = f"{filename_prefix}_{current_date}.csv"
    
    file_path = os.path.abspath(os.path.join(csv_path, file_name))
    dataframe.to_csv(file_path, index=False)

def create_location_final_data(combined_df, csv_path):
    """
    This function will run different functions to create the summarized data and save it to csv.

    Args:
        combined_df (dataframe): Combined data from all directories
        csv_path (dir): File path for the csv file
    """
    
    script_log.info("Analyzing 'Location' and 'RechargeAmount' data...")
    
    location_and_total_recharge_data = location_and_recharge_df(combined_df)
    filename_prefix = "total_recharge_per_location"
    save_to_csv(filename_prefix,csv_path, location_and_total_recharge_data)
    
    script_log.info("Done with the analysis. Refer to the csv file for details.\n")

def create_category_final_data(combined_df, csv_path):
    """
    This function will run different functions to create the summarized data and save it to csv.

    Args:
        combined_df (dataframe): Combined data from all directories
        csv_path (dir): File path for the csv file
    """
    
    script_log.info("Analyzing 'Category' and 'RechargeAmount' data...")
    
    category_and_total_recharge_data = category_and_recharge_df(combined_df)
    filename_prefix = "total_recharge_per_category"
    save_to_csv(filename_prefix,csv_path, category_and_total_recharge_data)
    
    script_log.info("Done with the analysis. Refer to the csv file for details.\n")
    
def create_paymentmethod_final_data(combined_df, csv_path):
    """
    This function will run different functions to create the summarized data and save it to csv.

    Args:
        combined_df (dataframe): Combined data from all directories
        csv_path (dir): File path for the csv file
    """
    
    script_log.info("Analyzing 'PaymentMethod' data...")
    
    payment_method_count = payment_method_df(combined_df)
    filename_prefix = "count_per_payment_method"
    save_to_csv(filename_prefix,csv_path, payment_method_count)
    
    script_log.info("Done with the analysis. Refer to the csv file for details.\n")

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
        script_log.info("Cursor created.\n")
        return cursor
    
    except Exception as e:
        script_log.error(f"An error has occured: {e}")

def create_recharge_file_stats_db(db_name, cursor, connection):
    """
    This function will create a database to handle the recharge file stats by executing the commands in the default database
    then close the connection and the cursor to make way to create a new connection and cursor.
    
    Args:
        cursor (psycopg2.extensions.cursor): Cursor to execute in the database
        connection (psycopg2.extensions.connection): Connection to the database
    """
    script_log.info(f"Creating database '{db_name}'")
    cursor.connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    
    try:
        cursor.execute("SELECT 1 FROM pg_database WHERE datname= %s;", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:    
            try:
                query = psycopg2.sql.SQL("CREATE DATABASE {}").format(psycopg2.sql.Identifier(db_name))
                cursor.execute(query)
                script_log.info(f"Database '{db_name}' has been created.\n")
            
            except Exception as e:
                script_log.error(f"An error has occured while creating new database '{db_name}': {e}\n")
    
        else:
            script_log.warning(f"Database '{db_name}' already exists. Skipping database creation.\n")
            
    except Exception as e:
        script_log.error(f"An error occured connected to the creation of '{db_name}': {e}")
    
    finally:
        cursor.close()
        connection.close()
 
def connect_to_new_db(db_name, config):   
    """
    This function will create a new connection to the newly created database for recharge file stats.

    Args:
        db_name (str): Name of the database to connect to
        config (dict): .toml file containing parameters

    Returns:
        new_connection (psycopg2.extensions.connection): Connection established with the new database
    """
    db_host = config["database"]["db_host"]
    db_user = config["database"]["db_user"]
    db_password = config["database"]["db_password"]
    
    try:
        new_connection = psycopg2.connect(
            dbname = db_name,
            user = db_user,
            password = db_password,
            host = db_host
        )

        script_log.info(f"Creating connection for user:{db_user} to database:{db_name}")
        script_log.info(f"Connection status: {new_connection.status}\n")

        return new_connection
    
    except Exception as e:
        script_log.error(f"An error occured: {e}\n")

def cursor_for_new_db(connection):
    """
    This function will create a new cursor for this database connection to execute commands.

    Args:
        connection (psycopg2.extensions.connection): Connection to the database

    Returns:
        cursor (psycopg2.extensions.cursor): Returns a cursor instance to be used to execute commands
    """
    
    try:
        cursor = connection.cursor()
        script_log.info("Creating cursor for command execution...\n")
        
        return cursor
    
    except Exception as e:
        script_log.error(f"An error has occured: {e}")
        
def create_table_locations_stats(cursor):
    """
    This function will create a table for the location-rechargeamount data

    Args:
        cursor (psycopg2.extensions.cursor): Instance of the cursor to execute data
    """
    
    try:
        
        script_log.info("Creating table...")
        table_name = "total_recharge_amount_per_location"
        query = f"CREATE TABLE IF NOT EXISTS {table_name} (id SERIAL PRIMARY KEY, Location VARCHAR(255), Total_RechargeAmount INT);"
        script_log.info(f"Executing query to create table '{table_name}' if not exists.")
        
        cursor.execute(query)
        
        script_log.info("Table created or already exists.")
        
    except Exception as e:
        script_log.error(f"An error occured: {e}\n")

def insert_location_data(csv_file, connection):
    """
    This function inserts the location data to the table.

    Args:
        csv_file (file): CSV file outputted by the script
        connection (psycopg2.extensions.connection): Connection to the database
    """
    try:
        cursor = connection.cursor()
        
        df = pd.read_csv(csv_file)
        table = "total_recharge_amount_per_location"
        for index, row in df.iterrows():
            query = f"INSERT INTO {table} (Location, Total_RechargeAmount) VALUES (%s, %s);"
            cursor.execute(query, (row["Location"], row["Total_RechargeAmount"]))
        
        connection.commit()
        script_log.info(f"Successfully inserted data from {csv_file} into '{table}' table\n")
    
    except Exception as e:
        script_log.error(f"Error inserting data into database: {e}\n")
    
    finally:
        cursor.close()

def create_table_category_stats(cursor):
    """
    This function will create a table for the category-rechargeamount data

    Args:
        cursor (psycopg2.extensions.cursor): Instance of the cursor to execute data
    """
    
    try:
        
        script_log.info("Creating table...")
        table_name = "total_recharge_amount_per_category"
        query = f"CREATE TABLE IF NOT EXISTS {table_name} (id SERIAL PRIMARY KEY, Category VARCHAR(255), Total_RechargeAmount INT);"
        script_log.info(f"Executing query to create table '{table_name}' if not exists.")
        
        cursor.execute(query)
        
        script_log.info("Table created or already exists.")
        
    except Exception as e:
        script_log.error(f"An error occured: {e}\n")

def insert_category_data(csv_file, connection):
    """
    This function inserts the location data to the table.

    Args:
        csv_file (file): CSV file outputted by the script
        connection (psycopg2.extensions.connection): Connection to the database
    """
    try:
        cursor = connection.cursor()
        
        df = pd.read_csv(csv_file)
        table = "total_recharge_amount_per_category"
        
        for index, row in df.iterrows():
            query = f"INSERT INTO {table} (Category, Total_RechargeAmount) VALUES (%s, %s);"
            cursor.execute(query, (row["Category"], row["Total_RechargeAmount"]))
        
        connection.commit()
        script_log.info(f"Successfully inserted data from {csv_file} into '{table}' table\n")
    
    except Exception as e:
        script_log.error(f"Error inserting data into database: {e}\n")
    
    finally:
        connection.commit()
        cursor.close()

def create_table_payment_method_stats(cursor):
    """
    This function will create a table for the paymentmethod ddata

    Args:
        cursor (psycopg2.extensions.cursor): Instance of the cursor to execute data
    """
    
    try:
        
        script_log.info("Creating table...")
        table_name = "payment_method_count"
        query = f"CREATE TABLE IF NOT EXISTS {table_name} (id SERIAL PRIMARY KEY, PaymentMethod VARCHAR(255), Total_Count INT);"
        script_log.info(f"Executing query to create table '{table_name}' if not exists.")
        
        cursor.execute(query)
        
        script_log.info("Table created or already exists.")
        
    except Exception as e:
        script_log.error(f"An error occured: {e}\n")

def insert_payment_method_data(csv_file, connection):
    """
    This function inserts the paymentmethod data to the table.

    Args:
        csv_file (file): CSV file outputted by the script
        connection (psycopg2.extensions.connection): Connection to the database
    """
    try:
        cursor = connection.cursor()
        
        df = pd.read_csv(csv_file)
        table = "payment_method_count"
        
        for index, row in df.iterrows():
            query = f"INSERT INTO {table} (PaymentMethod, Total_Count) VALUES (%s, %s);"
            cursor.execute(query, (str(row["PaymentMethod"]), int(row["Total_Count"])))
        
        connection.commit()
        script_log.info(f"Successfully inserted data from {csv_file} into '{table}' table\n")
    
    except Exception as e:
        script_log.error(f"Error inserting data into database: {e}\n")
    
    finally:
        connection.commit()
        cursor.close()

def execute_location_data_functions(new_cursor, csv_path, new_connection):
    """
    This function executes functions to handle the insertion of data from the summarized location data

    Args:
        new_cursor (psycopg2.extensions.cursor): Cursor created to execute a command
        csv_path (dir): Directory to get the csv file
        new_connection (psycopg2.extensions.connection): Connection to the database
    """
    
    create_table_locations_stats(new_cursor)
    latest_csv_file = max(
        [os.path.join(csv_path, f) for f in os.listdir(csv_path) if f.startswith("total_recharge_per_location")],
        key=os.path.getctime
        )
    insert_location_data(latest_csv_file, new_connection)

def execute_category_data_functions(new_cursor, csv_path, new_connection):
    """
    This function executes functions to handle the insertion of data from the summarized category data

    Args:
        new_cursor (psycopg2.extensions.cursor): Cursor created to execute a command
        csv_path (dir): Directory to get the csv file
        new_connection (psycopg2.extensions.connection): Connection to the database
    """
    
    create_table_category_stats(new_cursor)
    latest_csv_file = max(
        [os.path.join(csv_path, f) for f in os.listdir(csv_path) if f.startswith("total_recharge_per_category")],
        key=os.path.getctime
        )
    insert_category_data(latest_csv_file, new_connection)

def execute_paymentmethod_data_functions(new_cursor, csv_path, new_connection):
    """
    This function executes functions to handle the insertion of data from the summarized payment data

    Args:
        new_cursor (psycopg2.extensions.cursor): Cursor created to execute a command
        csv_path (dir): Directory to get the csv file
        new_connection (psycopg2.extensions.connection): Connection to the database
    """
    
    create_table_payment_method_stats(new_cursor)
    latest_csv_file = max(
        [os.path.join(csv_path, f) for f in os.listdir(csv_path) if f.startswith("count_per_payment_method")],
        key=os.path.getctime
        )
    insert_payment_method_data(latest_csv_file, new_connection)

def main():
    
    config = import_config_file()
    input_path = import_input_path(config)
    log_path = import_log_path(config)
    
    csv_files_to_read = get_csv_files_to_read(input_path)
    combined_df = combine_matched_csv(csv_files_to_read)
    send_to_database_operation = config["operation"]["send_to_database"]
    csv_path = config["directories"]["csv_path"]
    
    try:
        create_location_final_data(combined_df, csv_path)
    except Exception as e:
        script_log.error(f"An error occured while analyzing 'Location' and 'RechargeAmount' data: {e}\n")
    
    try:    
        create_category_final_data(combined_df, csv_path)
    except Exception as e:
        script_log.error(f"An error occured while analyzing 'Category' and 'RechargeAmount' data: {e}\n")
    
    try:
        create_paymentmethod_final_data(combined_df, csv_path)
    except Exception as e:
        script_log.error(f"An error occured while analyzing 'Payment' data: {e}\n")
    
    new_cursor = None
    new_connection = None
    
    if send_to_database_operation == "YES":
        
        script_log.info(f"Operation send_to_database: {send_to_database_operation}")
        script_log.info("Executing transfer...")
        
        try:
             
            db_connection = connect_to_db(config)
            db_cursor = open_cursor_db(db_connection)
            
            db_name = "recharge_file_stats_db" 
            create_recharge_file_stats_db(db_name, db_cursor, db_connection)
            
            try:
                new_connection = connect_to_new_db(db_name, config)
                new_cursor = cursor_for_new_db(new_connection)
                
                execute_location_data_functions(new_cursor, csv_path, new_connection)
                execute_category_data_functions(new_cursor, csv_path, new_connection)
                execute_paymentmethod_data_functions(new_cursor, csv_path, new_connection)
                
                new_connection.commit()
            
            except Exception as e:
                script_log.error(f"An error occured while creating a new connection or new cursor: {e}\n")
            
        except Exception as e:
            script_log.error(f"An error has occured: {e}")
            
        finally:
            script_log.info("Closing connection...")
            
            if new_cursor is not None:
                new_cursor.close()
            if new_connection is not None:
                new_connection.close()
                
            script_log.info("Connection closed.\n")
            
    else:
        script_log.info(f"Operation send_to_database: {send_to_database_operation}")
        script_log.info("Skipping copying of files to postgres database...\n")
    
if __name__ == "__main__":
    config = import_config_file()
    log_path = import_log_path(config)
    current_date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    script_log = initialize_logger(log_path, f"recharge_file_reader - {current_date}.log", "script_handler")
    
    script_log.info("##############################################################################")
    script_log.info("Script is called...")
    script_log.info("##############################################################################\n")
    
    main()
    
    script_log.info("##############################################################################")
    script_log.info("Script executed...")
    script_log.info("##############################################################################\n")