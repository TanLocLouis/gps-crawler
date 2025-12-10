import requests
import time
import os
import argparse
import getpass
from datetime import datetime
from dotenv import load_dotenv
from utils import dict_to_csv, hash_password, store_user_credentials, delete_user_credentials

base_url = "https://gps.toanthangjsc.vn/"
data_path = os.path.join(os.path.dirname(__file__), "data")

load_dotenv()
USER_NAME = os.getenv("USER_NAME")
PASSWORD = os.getenv("PASSWORD")
TRACKER_ID = os.getenv("TRACKER_ID")
VEH_ID = os.getenv("VEH_ID")
SERVER_IP = os.getenv("SERVER_IP")



# Argument parser setup
parser = argparse.ArgumentParser(description='GPS Crawler')
parser.add_argument('--add', action='store_true', help='Add a new user')
parser.add_argument('--rm', action='store_true', help='Remove an existing user')

args = parser.parse_args()

if args.add:
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    hashed_password = hash_password(password)
    store_user_credentials(username, hashed_password)
    print("User created successfully.")
    exit()

if args.rm:
    username = input("Enter username to remove: ")
    delete_user_credentials(username)
    exit()

def login():
    # Step 1: GET to get session ID
    # Define the headers for the request
    headers = {
        "Host": "gps.toanthangjsc.vn",
        "Sec-Ch-Ua": '" Not A;Brand";v="99", "Chromium";v="96"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "Linux",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        # Send the GET request without following redirects
        response = requests.get(base_url, headers=headers, allow_redirects=False)
    except Exception as e:
        print("Failed to connect to the server.")
        return

    # Output the response details
    print("Status Code:", response.status_code)
    print("Headers:", response.headers)
    print("Cookies:", response.cookies.get_dict())
    print("Body:", response.text)
    session_cookie = response.cookies.get("ASP.NET_SessionId")
    print(f"Session ID: {session_cookie}")

    # Step 2: POST to login
    login_url = f"{base_url}/Login.aspx/CheckLogin"
    headers_post_login = {
        "Cookie": f"ASP.NET_SessionId={session_cookie}",
        "Sec-Ch-Ua": '" Not A;Brand";v="99", "Chromium";v="96"',
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Sec-Ch-Ua-Mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        "Sec-Ch-Ua-Platform": "Linux",
        "Origin": base_url,
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": f"{base_url}/Domain/gps.toanthangjsc.vn/login.html?v=2.01.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
    }
    login_payload = {
        "Username": USER_NAME,
        "Password": PASSWORD,
        "Type": 0
    }

    try:
        login_response = requests.post(login_url, headers=headers_post_login, json=login_payload)
        if login_response.status_code == 200:
                print("Login successful.")
        else:
                print("Login failed.")
    except Exception as e:
        print("Failed to connect to the server during login.")
        return

    return session_cookie

def get_info(session_cookie):
    # Step 3: POST to get vehicle information
    vehicle_info_url = f"{base_url}/Default.aspx/VehicleStatus"
    headers_post_vehicle = {
        "Cookie": f"ASP.NET_SessionId={session_cookie}",
        "Sec-Ch-Ua": '" Not A;Brand";v="99", "Chromium";v="96"',
        "Accept": "*/*",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Sec-Ch-Ua-Mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        "Sec-Ch-Ua-Platform": "Linux",
        "Origin": base_url,
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": f"{base_url}/Default1.aspx",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
    }
    vehicle_payload = {
        "TrackerID": TRACKER_ID,
        "VehID": VEH_ID,
        "Show_Output": 0,
        "OBD": 0,
        "VehicleType": "2169",
        "ServerIp": SERVER_IP 
    }

    try:
        vehicle_response = requests.post(vehicle_info_url, headers=headers_post_vehicle, json=vehicle_payload)
        if vehicle_response.status_code == 200:
            data = vehicle_response.json()
            flat_data = data.get('d', {})
            if len(flat_data.get('stime')) > 1:
                print("Vehicle information retrieved successfully.")
                print(flat_data)
                print("-" * 100)

                current_date = datetime.now()
                filename_date = current_date.strftime("%Y-%m-%d") + ".csv"
                return [flat_data, filename_date]
            else:
                print("Failed to retrieve vehicle information.")
    except:
        print("Failed to retrieve vehicle information.")
        return


def main():
    # Login to the website to get the session cookie
    # This cookie will expire after 20 mins of inactivity
    last_refresh = 0; 

    previous_location = [0, 0]
    # Continuously get vehicle information every 10 seconds
    while True:
        time.sleep(10)

        current_time = time.time()
        if current_time - last_refresh > 600:
            session_cookie = login()
            if session_cookie:
                print("Session refreshed.")
                last_refresh = current_time
                time.sleep(10)
            else:
                print("Failed to refresh session.")
                continue

        result = get_info(session_cookie)
        if result is None:
            continue

        [flat_data, filename_date] = result
        current_location = [flat_data.get('lat'), flat_data.get('lng')]
        if current_location != previous_location:
            dict_to_csv(flat_data, filename_date)
            previous_location = current_location

if __name__ == "__main__":
    main()