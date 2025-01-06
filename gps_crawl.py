import requests
import time
import csv
from datetime import datetime

USER_NAME = ""
PASSWORD = ""
TRACKER_ID = ""
VEH_ID = ""
SERVER_IP = ""

def dict_to_csv(data, output_file):
    """
    Convert a nested dictionary into a CSV file.
    
    Args:
        data (dict): The input dictionary to be converted.
        output_file (str): Path to the output CSV file.
    """
    # Flatten the dictionary for the 'd' key
    flat_data = data.get('d', {})
    
    # Open the CSV file for writing
    with open(output_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write the headers (keys) only if the file is empty
        if file.tell() == 0:
            writer.writerow(flat_data.keys())
        
        # Write the values (values) to the CSV
        writer.writerow(flat_data.values())

def get_info():
    # Step 1: GET to get session ID
    # Define the target URL
    base_url = "https://gps.toanthangjsc.vn/"

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

    # Send the GET request without following redirects
    response = requests.get(base_url, headers=headers, allow_redirects=False)

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

    login_response = requests.post(login_url, headers=headers_post_login, json=login_payload)
    if login_response.status_code == 200:
        print("Login successful.")
    else:
        print("Login failed.")
        exit()

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

    vehicle_response = requests.post(vehicle_info_url, headers=headers_post_vehicle, json=vehicle_payload)
    if vehicle_response.status_code == 200:
        print("Vehicle information retrieved successfully.")
        data = vehicle_response.json()
        print(data)

        current_date = datetime.now()
        filename_date = current_date.strftime("%Y-%m-%d") + ".csv"
        data = dict_to_csv(data, filename_date)
    else:
        print("Failed to retrieve vehicle information.")


def main():
    while True:
        get_info()
        time.sleep(10)

if __name__ == "__main__":
    main()