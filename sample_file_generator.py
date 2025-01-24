import os
import random
import string
from datetime import datetime, timedelta

def generate_msidn():
    num = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    code = 971
    random_numbers = random.choices(num, k=9)
    msidn = str(code)

    for num in random_numbers:
        msidn = msidn + str(num)
    
    return msidn

def generate_event_date_time():
    now = datetime.now().strftime("%d%m%Y%H%M")
    return now

def generate_service_class():
    first_digit_choices = [0, 1, 2, 3, 4, 5]
    second_digit_choices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    third_digit_choices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    
    first_digit = random.choice(first_digit_choices)
    second_digit = random.choice(second_digit_choices)
    third_digit = random.choice(third_digit_choices)
    
    service_class = f"{first_digit}{second_digit}{third_digit}"
    
    return service_class

def generate_recharge_amt():
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
    num = [1, 2, 3]
    payment_method = "0" + str(random.choice(num))
    
    return payment_method
    
def generate_subscriber_category():
    categories = ["YTH", "STD", "BSC", "SPL"]
    subscriber_category = random.choice(categories)
    
    return subscriber_category

def generate_location():
    locations = ["X10", "X11", "X12", "X13"]
    location = random.choice(locations)
    
    return location        
            
def generate_content_for_file(file_path, msidn, event_date_time, service_class,
                              recharge_amt, payment_method, subscriber_category, location):
    
    with open(file_path, "a") as file:
        content = f"{msidn},{event_date_time},{service_class},{recharge_amt},{payment_method},{subscriber_category},{location}\n"
        
        file.write(content)

def create_sample_recharge_file(base_path, num_of_lines):
    
    os.makedirs(base_path, exist_ok=True)
    
    file_name = f"EvenFile_Recharge_000.csv"
    file_path = os.path.join(base_path, file_name)

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
    
    base_path = "sample"
    num_of_lines = 5
    
    create_sample_recharge_file(base_path, num_of_lines)
    
    
if __name__ == "__main__":
    main()