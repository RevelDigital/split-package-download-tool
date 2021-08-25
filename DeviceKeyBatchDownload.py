import os
import requests
import sys
import time
from colorama import Fore, Back, Style, init
init()

retry_interval = 30
api_key = os.environ.get('REVEL_SPLIT_PACKAGE_API_KEY')

if api_key is None:
    print(Fore.RED + "API Key environmental variable not found.")
    print("Please create a new variable using key name: 'REVEL_SPLIT_PACKAGE_API_KEY'")
    print("Close script and try again or contact support." + Fore.RESET)
    close = input("Press enter to exit script")
    sys.exit()

def timerAnimation(duration):
    while duration > -1:
        sys.stdout.write('\r' + str(duration) + " seconds remaining ")
        sys.stdout.flush()
        time.sleep(1)
        duration -= 1
    print("")

def apiRequest(url):
    requestIncomplete = True
    while requestIncomplete:
        try:
            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            sys.stdout.write('\r')
            print(Fore.RED + "Connection Error")
            print("Error: " + str(e) + Fore.RESET)
            print("Retrying in " + str(retry_interval) + " seconds")
            timerAnimation(retry_interval)
            print("\nRetrying now")
        else:
            if response.status_code == requests.codes.ok:
                requestIncomplete = False
                return response
            else:
                sys.stdout.write('\r')
                print(Fore.RED + "Bad response code recevied")
                print("Response code: " + str(response.status_code))
                print("Response body:" + str(response.content) + Fore.RESET)
                print("Retrying in " + str(retry_interval) + " seconds")
                timerAnimation(retry_interval)
                print("\nRetrying now")

print("Please provide keyword(s) to filter devices by.")
print("If the keyword(s) are found within a device name, the respective device.key file will be created.")
print("If more than one word is provided the entire text string will be matched exactly as it appears.")
target_string = input("Please enter text...")
target_string = target_string.strip()
print("Keyword text: " + target_string)
print("gettting device data...")
response = apiRequest("https://api.reveldigital.com/api/devices/?api_key=" + api_key + "&include_snap=false")
devicesJSON = response.json()
response.close()
matchFound =False
for device in devicesJSON:
    deviceName = device["name"].strip()
    if target_string.lower() in deviceName.lower():
        if not matchFound:
            print("creating device.key files for the following devices:")
            matchFound = True
        if os.path.isdir(deviceName):
            print("")
            print(Fore.YELLOW + "device folder already created for another device with matching name")
            print("Skipping device name: " + deviceName)
            print("Registration Key:" + device["registration_key"] + Fore.RESET)
            print("")
        else:
            try:
                os.mkdir(deviceName)
            except OSError as e:
                print("")
                print(Fore.RED + "directory could not be created for device name: " + deviceName)
                print("Registration Key:" + device["registration_key"])
                print("If the device name includes an invalid character or character sequence, the OS won't allow a folder to be created with that device name.")
                print("error: " + str(e) + Fore.RESET)
                print("")
            if os.path.isdir(deviceName):
                path = os.path.join('./' + deviceName, "device.key")
                deviceKey = open(path, "w")
                deviceKey.write(device["encrypted_registration_key"])
                deviceKey.close()
                print(deviceName)

if matchFound:
    print(Fore.GREEN + "device.key creation complete" + Fore.RESET)    
else:
    print(Fore.RED + "No device name in the account contains text that matches the provided keyword(s): " + target_string + Fore.RESET)
