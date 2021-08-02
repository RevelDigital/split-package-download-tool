import requests
import json
import tarfile
import os
import time
from os import path
import shutil
import itertools
import threading
import sys
from colorama import Fore, Back, Style, init
init()

api_key = ""
media_reference_device_reg_key = ""
polling_interval = 60
retry_interval = 30
original_devicesJSON = {}

def loadingAnimation():
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if enable_loading_animation:
            sys.stdout.write('\rDownloading ' + c)
            sys.stdout.flush()
            time.sleep(0.1)
        else:
            time.sleep(1)

enable_loading_animation = False
t = threading.Thread(target=loadingAnimation)
t.daemon=True
t.start()

def timerAnimation(duration):
    while duration > -1:
        sys.stdout.write('\r' + str(duration) + " seconds remaining ")
        sys.stdout.flush()
        time.sleep(1)
        duration -= 1
    print("")

not_connected = True
while not_connected:
    try:
        response = requests.get("https://api.reveldigital.com/api/status")
    except requests.exceptions.RequestException as e:
        print(Fore.RED + "Connection Error")
        print("Error: " + str(e) + Fore.RESET)
        print("Retrying in " + str(retry_interval) + " seconds")
        timerAnimation(retry_interval)
        print("")
        print("Retrying now")
    else:
        if response.status_code == requests.codes.ok:
            not_connected = False
        else:
            print(Fore.RED + "Bad response code recevied")
            print("Response code: " + str(response.status_code))
            print("Response body:" + str(response.content) + Fore.RESET)
            print("Retrying in " + str(retry_interval) + " seconds")
            timerAnimation(retry_interval)
            print("")
            print("Retrying now")

def apiRequest(url, streamType, run_download_animation):
    global response
    global enable_loading_animation
    requestIncomplete = True
    if run_download_animation:
        enable_loading_animation = True
    while requestIncomplete:
        try:
            response = requests.get(url, stream=streamType)
        except requests.exceptions.RequestException as e:
            enable_loading_animation = False
            sys.stdout.write('\r')
            print(Fore.RED + "Connection Error")
            print("Error: " + str(e) + Fore.RESET)
            print("Retrying in " + str(retry_interval) + " seconds")
            timerAnimation(retry_interval)
            print("")
            print("Retrying now")
            if run_download_animation:
                enable_loading_animation = True
        else:
            if response.status_code == requests.codes.ok:
                requestIncomplete = False
            else :
                enable_loading_animation = False
                sys.stdout.write('\r')
                print(Fore.RED + "Bad response code recevied")
                print("Response code: " + str(response.status_code))
                print("Response body:" + str(response.content) + Fore.RESET)
                print("Retrying in " + str(retry_interval) + " seconds")
                timerAnimation(retry_interval)
                print("")
                print("Retrying now")
                if run_download_animation:
                    enable_loading_animation = True

# Getting media package from shared media device 
print("Step 1 of 3: Downloading shared media...")
apiRequest("https://svc1.reveldigital.com/v2/package/get/" + media_reference_device_reg_key + "?tar=true", True, True)
with open("MediaPackage.tar", 'wb') as f:
    for chunk in response.iter_content(chunk_size=1024 * 1024):
        f.write(chunk)
f.close()
response.close()
enable_loading_animation = False
sys.stdout.write('\r             Media download complete')
print("")
print("")

#Extracting Media folder from tar package
print("Step 2 of 3: Creating Media.tar file")
if path.exists("MediaPackage.tar"):
    tar = tarfile.open("MediaPackage.tar", 'r')
    for entry in tar:
        if entry.name.startswith("Media/"):
            tar.extract(entry)
    tar.close()
else:    
    print(Fore.RED + "Something went wrong.")
    print("MediaPackage.tart not found")
    print("Close script and try again or contact support." + Fore.RESET)
    close = input("Press enter to exit script")
    sys.exit()

# Creating Media.tar file
with tarfile.open('Media.tar', "a", format=tarfile.GNU_FORMAT) as archive:
    archive.add('./Media')
archive.close()
print("             Media.tar file created")
print("")

# remove unneeded files/directories
if os.path.exists("MediaPackage.tar"):
    os.remove("MediaPackage.tar")
if os.path.isdir('Media'):
    shutil.rmtree('./Media')

# create or load data from local JSON device list
if path.exists("DeviceList.txt"):
    print("Step 3 of 3: Local device list found. Loading devices from list")
    with open('DeviceList.txt') as json_file:
        original_devicesJSON = json.load(json_file)
    print("             Device list loaded")
    print("")
    print("Checking in " + str(polling_interval) + " seconds for new devices registered since script was last closed")
else:
    print("Step 3 of 3: Local device list doesn't exist. Generating list device list now...")
    apiRequest("https://api.reveldigital.com/api/devices?api_key=" + api_key + "&include_snap=false", False, True)
    original_devicesJSON = response.json()
    response.close()
    enable_loading_animation = False
    with open('DeviceList.txt', 'w') as outfile:
        json.dump(original_devicesJSON, outfile)
    print("")
    sys.stdout.write('\r             Device list created')
    print("")
    print("")
    print("Checking for new devices in " + str(polling_interval) + " seconds")

#Monitor for new device registrations and automatically download the device specific package.tar
while True:
    timerAnimation(polling_interval)
    print("")
    print("Checking for new devices now...")
    apiRequest("https://api.reveldigital.com/api/devices?api_key=" + api_key + "&include_snap=false", False, False)
    devicesJSON = response.json()
    response.close()
    newDeviceCount = 0
    if path.exists("DeviceList.txt"):
        with open('DeviceList.txt') as json_file:
            original_devicesJSON = json.load(json_file)
        for device in devicesJSON:
            if(device["device_type"]["id"] == "Universal"):
                matchFound = False
                for originalDevice in original_devicesJSON:
                    if device["registration_key"] == originalDevice["registration_key"]:
                        matchFound = True
                if matchFound == False:
                    newDeviceCount += 1
                    print(Fore.GREEN + "New Device Found: " + device["name"] + ". Downloading package now..." + Fore.RESET)
                    apiRequest("https://svc1.reveldigital.com/v2/package/get/" + device["registration_key"] + "?tar=true&excludeMedia=true", True, True)
                    with open(device["registration_key"] + ".tar", 'wb') as f:
                        f.write(response.raw.read())
                    response.close()
                    enable_loading_animation = False
                    sys.stdout.write('\rDownload complete')
                    print("")
                    print("")
        original_devicesJSON = devicesJSON
        with open('DeviceList.txt', 'w') as outfile:
            json.dump(original_devicesJSON, outfile)
        print("Check complete. " + str(newDeviceCount)+ " new Device(s) found")
        print("Checking again in " + str(polling_interval) + " seconds")
    else:
        print(Fore.RED + "Something went wrong.")
        print("DeviceList.txt not found")
        print("Close script and try again or contact support." + Fore.RESET)
        close = input("Press enter to exit script")
        sys.exit()
