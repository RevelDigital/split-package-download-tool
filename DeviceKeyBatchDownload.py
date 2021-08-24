import os
import requests
import sys
import time
from colorama import Fore, Back, Style, init
init()

retry_interval = 30
target_string = "evo"
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
                
print("gettting device data...")
response = apiRequest("https://api.reveldigital.com/api/devices/?api_key=" + api_key + "&include_snap=false")
devicesJSON = response.json()
response.close()
print("creating device.key files for the following devices:")
for device in devicesJSON:
    deviceName = device["name"]
    if target_string.lower() in deviceName.lower():
        if os.path.isdir(deviceName):
            print("")
            print(Fore.RED + "device.key already created for another device with matching name")
            print("Skipping device name: " + deviceName)
            print("Registration Key:" + device["registration_key"] + Fore.RESET)
            print("")
        else:
            os.mkdir(deviceName)
            path = os.path.join('./' + deviceName, "device.key")
            deviceKey = open(path, "w")
            deviceKey.write(device["encrypted_registration_key"])
            deviceKey.close()
            print(deviceName)
print(Fore.GREEN + "device.key creation complete" + Fore.RESET)
