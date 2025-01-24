import os
import random
import string
from datetime import datetime, timedelta

def generate_msidn():
    """
    This function will generate a random msidn
    
    Returns:
        msidn (str): This will be used as a data entry for the .csv file.
    """
    
    num = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    code = 971
    random_numbers = random.choices(num, k=9)
    msidn = str(code)

    for num in random_numbers:
        msidn = msidn + str(num)
    
    return msidn

def generate_event_date_time():
    """
    This function will generate a random date from current date to 30 days ago.
    
    Returns:
        now (str): This will be used as a data entry for the .csv file. Date follows
        the format: DaysMonthYearHourMinute (DDMMYYYYHHMM)
    """
    
    end = datetime.now()
    start = end - timedelta(days=30)
    
    random_date = start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))
    now = random_date.strftime("%d%m%Y%H%M")
    
    return now

def generate_service_class():
    """
    This function generate a three digit number which serves as the service class.

    Returns:
        service_class (str): This will be used as a data entry for the .csv file.
    """
    
    first_digit_choices = [0, 1, 2, 3, 4, 5]
    second_digit_choices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    third_digit_choices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    
    first_digit = random.choice(first_digit_choices)
    second_digit = random.choice(second_digit_choices)
    third_digit = random.choice(third_digit_choices)
    
    service_class = f"{first_digit}{second_digit}{third_digit}"
    
    return service_class

def generate_recharge_amt():
    """
    This function will generate a combination of numbers depending on the
    output of num_of_digits which decides how many digits the number
    will have.

    Returns:
        recharge_amt (str): This will be used as a data entry for the .csv file.
    """
    
    digits = [2, 3, 4, 5]
    num = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    first_digit = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    
    recharge_amt = ""
    x = 1
    
    num_of_digits = random.choice(digits)
    while x <= num_of_digits:
        if x == 1:
            recharge_amt = recharge_amt + str(random.choice(first_digit))
        else:
            recharge_amt = recharge_amt + str(random.choice(num))
        x+=1
    
    return recharge_amt

def generate_payment_method():
    """
    This function will generate a random code with a prefix of '0'

    Returns:
        payment_method (str): This will be used as a data entry for the .csv file.
    """
    
    num = [1, 2, 3]
    payment_method = "0" + str(random.choice(num))
    
    return payment_method
    
def generate_subscriber_category():
    """
    This function will generate a random category based on the
    categories list.

    Returns:
        subscriber_category (str): This will be used as a data entry for the .csv file.
    """
    
    categories = ["YTH", "STD", "BSC", "SPL"]
    subscriber_category = random.choice(categories)
    
    return subscriber_category

def generate_location():
    """
    This function will generate a random location based on the
    locations list.

    Returns:
        location (str): This will be used as a data entry for the .csv file.
    """
    
    locations = ["X10", "X11", "X12", "X13"]
    location = random.choice(locations)
    
    return location        
            
def generate_content_for_file(file_path, msidn, event_date_time, service_class,
                              recharge_amt, payment_method, subscriber_category, location):
    """
    This function will generate the content of the file to be created per line.

    Args:
        file_path (dir): File where the content will be generated.
        msidn (str): Randomly generated msidn data
        event_date_time (str): Randomly generated date and time data
        service_class (str): Randomly generated service class data
        recharge_amt (str): Randomly generated recharge amount data
        payment_method (str): Randomly generated payment method data
        subscriber_category (str): Randomly generated subscriber category data
        location (str): Randomly generated location data
    """
    
    with open(file_path, "a") as file:
        content = f"{msidn},10,{event_date_time},{service_class},{recharge_amt},{payment_method},{subscriber_category},{location}\n"
        
        file.write(content)

def get_next_unique_num_from_files(base_path):
    """
    This function will output the next unique number for the filename
    by checking the previous number in the base_path.

    Args:
        base_path (dir): Directory where the file(s) is/are located.

    Returns:
        next_num (str): The number to be used for the file creation.
    """
    
    existing_files = os.listdir(base_path)
    unique_nums = []
    
    for file in existing_files:
        if file.startswith("EventFile_Recharge_") and file.endswith(".csv"):
            # Extract the unique number (assumes format EvenFile_Recharge_XXX_date.csv)
            parts = file.split("_")
            if len(parts) >= 3 and parts[2].isdigit():
                unique_nums.append(int(parts[2]))
    

    # Find the next unique number
    next_num = max(unique_nums, default=0) + 1
    next_num = f"{next_num:03}"
    return next_num

def generate_file_name(base_path):
    """
    This function generates the filename based on the unique number output
    of the get_next_unique_num_from_files() function.

    Args:
        base_path (dir): Directory where the file(s) is/are located.

    Returns:
        file_name (str): String to use for the new unique filename
    """
    
    unique_num = get_next_unique_num_from_files(base_path)
    date = datetime.now().strftime("%d%m%Y_%H%M")
    
    file_name = f"EventFile_Recharge_{unique_num}_{date}.csv"
    print(file_name)
    return file_name

def create_sample_recharge_file(base_path, num_of_lines):
    """
    This function will generate the file with contents generated randomly by different
    functions and compiled by running the generate_content_for_file() function.

    Args:
        base_path (dir): Directory where the file will be generated
        num_of_lines (int): Number of lines of content to be generated
    """
    os.makedirs(base_path, exist_ok=True)
    
    file_name = generate_file_name(base_path)
    file_path = os.path.join(base_path, file_name)
    print(file_path)    
    with open(file_path, "w") as f:
        f.write("MSIDN,EventType,EventDateAndTime,ServiceClass,RechargeAmount,PaymentMethod,Category,Location\n")
    
    x=0
    while x < num_of_lines:
        msidn = generate_msidn()
        event_date_time = generate_event_date_time()
        service_class = generate_service_class()
        recharge_amt = generate_recharge_amt()
        payment_method = generate_payment_method()
        subscriber_category = generate_subscriber_category()
        location = generate_location()
        
        generate_content_for_file(file_path, msidn, event_date_time, service_class,
                              recharge_amt, payment_method, subscriber_category, location)
        x += 1

def main():
    
    base_path = "sample_data"
    num_of_lines = 5
    
    create_sample_recharge_file(base_path, num_of_lines)
    
if __name__ == "__main__":
    main()