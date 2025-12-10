
import csv
import os
import hashlib
import configparser

import os
import configparser
import hashlib
import csv

base_url = "https://gps.toanthangjsc.vn/"
data_path = os.path.join(os.path.dirname(__file__), "data")

# Function to hash the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to store user credentials
def store_user_credentials(username, hashed_password):
    if not os.path.exists('users'):
        os.kedirs('users')
    user_file = os.path.join('users', f'{username}.conf')
    config = configparser.ConfigParser()
    config['User'] = {'username': username, 'password': hashed_password}
    with open(user_file, 'w') as configfile:
        config.write(configfile)

# Function to delete user credentials
def delete_user_credentials(username):
    user_file = os.path.join('users', f'{username}.conf')
    if os.path.exists(user_file):
        os.remove(user_file)
        print(f"User {username} deleted successfully.")
    else:
        print(f"User {username} does not exist.")

def dict_to_csv(data, output_file):
    """
    Convert a nested dictionary into a CSV file.
    
    Args:
        data (dict): The input dictionary to be converted.
        output_file (str): Path to the output CSV file.
    """
    
    # Open the CSV file for writing
    # Create folder if it does not exist
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    file_path = data_path + "/" + output_file
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write the headers (keys) only if the file is empty
        if file.tell() == 0:
            writer.writerow(data.keys())
        
        # Write the values (values) to the CSV
        writer.writerow(data.values())

# Function to hash the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to verify user credentials
def verify_user_credentials(username, password):
    user_file = os.path.join('users', f'{username}.conf')
    if not os.path.exists(user_file):
        return False
    config = configparser.ConfigParser()
    config.read(user_file, encoding='utf-8')
    stored_password = config.get('User', 'password')
    return stored_password == hash_password(password)

# Function to add a new user
def add_user(username, password):
    user_file = os.path.join('users', f'{username}.conf')
    if os.path.exists(user_file):
        print(f"User {username} already exists.")
        return False
    config = configparser.ConfigParser()
    config['User'] = {
        'username': username,
        'password': hash_password(password)
    }
    with open(user_file, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    print(f"User {username} created successfully.")
    return True

# Function to delete a user
def delete_user(username):
    user_file = os.path.join('users', f'{username}.conf')
    if not os.path.exists(user_file):
        print(f"User {username} does not exist.")
        return False
    os.remove(user_file)
    print(f"User {username} deleted successfully.")
    return True

