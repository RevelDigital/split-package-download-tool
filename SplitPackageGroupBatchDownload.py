import itertools
import json
import os
from os import path
import shutil
import sys
import tarfile
import threading
import time
import zipfile
from colorama import Fore, Back, Style, init
import requests
init()

api_key = os.environ.get('REVEL_SPLIT_PACKAGE_API_KEY')
if api_key is None:
    print(Fore.RED + "API Key environmental variable not found.")
    print("Please create a new variable using key name: 'REVEL_SPLIT_PACKAGE_API_KEY'")
    print("Close script and try again or contact support." + Fore.RESET)
    close = input("Press enter to exit script")
    sys.exit()
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
            else:
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

#get group selection from user
def get_group_id():
    apiRequest("https://api.reveldigital.com/api/devices/groups?api_key=" + api_key, False, False)
    deviceGroupsJSON = response.json()
    idx = 1
    for group in deviceGroupsJSON:
        print(str(idx) + ".) " + group["name"])
        idx += 1
    device_group_index = int(input("Enter number associated with device droup: "))
    device_group_index -= 1
    if device_group_index > -1 and device_group_index < len(deviceGroupsJSON):
        device_group_name = deviceGroupsJSON[device_group_index]["name"]
        print("Group Selected: " + device_group_name)
        if deviceGroupsJSON[device_group_index]["count"] == 0:
            print("Device group doesn't contain any devices. Please select another group")
            return get_group_id()
        else:
            device_group_id = deviceGroupsJSON[device_group_index]["id"]
            return device_group_id
    else:
        print("Invalid entry")
        return get_group_id()

if path.exists("Media.tar") and path.exists("GroupId.txt"):
    print("Media package already exists. Loading device group from file. Skipping steps 1 and 2")
    with open('GroupId.txt') as text_file:
        group_id = text_file.read()
else:
    print("Missing Media.tar and/or GroupId.txt files. Select device group to pull media from")
    if path.exists("MediaPackage.tar"):
        os.remove("MediaPackage.tar")
    if path.exists("Media.tar"):
        os.remove("Media.tar")
    if path.exists("GroupId.txt"):
        os.remove("GroupId.txt")
    if path.isdir('Media'):
        shutil.rmtree('./Media')
    group_id = get_group_id()
    with open('GroupId.txt', 'w') as outfile:
        outfile.write(group_id)
    apiRequest("https://api.reveldigital.com/api/devices?api_key=" + api_key + "&group_id=" + group_id + "&include_snap=false", False, False)
    groupDevicesJSON = response.json()
    media_reference_device_reg_key = groupDevicesJSON[0]["registration_key"]
    print("Downloading shared media...")
    # Getting media package from shared media device
    apiRequest("https://svc1.reveldigital.com/v2/package/get/" + media_reference_device_reg_key + "?usb=true&tar=true", True, True)
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
            if entry.name.startswith("Media"):
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
    if path.exists("MediaPackage.tar"):
        os.remove("MediaPackage.tar")
    if path.isdir('Media'):
        shutil.rmtree('./Media')

#automatically download the device specific package.tar for each device in account
print("")
print("Getting new devices now...")
apiRequest("https://api.reveldigital.com/api/devices?api_key=" + api_key + "&group_id=" + group_id + "&include_snap=false", False, False)
devicesJSON = response.json()
response.close()
newDeviceCount = 0
for device in devicesJSON:
    newDeviceCount += 1
    print(Fore.GREEN + "Device Found: " + device["name"] + ". Downloading package now..." + Fore.RESET)
    apiRequest("https://svc1.reveldigital.com/v2/package/get/" + device["registration_key"] + "?usb=true&tar=true&excludeMedia=true", True, True)
    with open(device["registration_key"] + ".tar", 'wb') as f:
        f.write(response.raw.read())
    response.close()
    enable_loading_animation = False
    sys.stdout.write('\rDownload complete')
    print("")
    print("")
print("Check complete. " + str(newDeviceCount)+ " new Device(s) found")

rehydrate = input("Would you like to merge the Media content with downloaded device packages? (y/n)")
if rehydrate == "y":
    if path.exists("Media.tar"):
        tar = tarfile.open("Media.tar", 'r')
        tar.extractall()
        tar.close()
    else:    
        print(Fore.RED + "Something went wrong.")
        print("Media.tar not found")
        print("Close script and try again or contact support." + Fore.RESET)
        close = input("Press enter to exit script")
        sys.exit()
    for device in devicesJSON:
        tar_name = device["registration_key"] + ".tar"
        if path.exists(tar_name):
            print("Merging device package: " + device["name"])
            with tarfile.open(tar_name, "a", format=tarfile.GNU_FORMAT) as archive:
                archive.add('./Media')
            archive.close()
        else:
            print(Fore.RED + "Something went wrong.")
            print(tar_name + " not found")
            print("package skipped" + Fore.RESET)
    print("package merge complete")
    if path.isdir('Media'):
        shutil.rmtree('./Media')

convert = input("Would you like to convert the tar package files to zip file for Android? (y/n)")
if convert == "y":
    for device in devicesJSON:
        print("Compressing device package: " + device["name"])
        registration_key = device["registration_key"]
        tar = tarfile.open(registration_key + ".tar", 'r')
        zipPackage = zipfile.ZipFile(registration_key + ".zip", 'a', zipfile.ZIP_DEFLATED)
        for entry in tar:
            entryName = entry.name
            file = tar.extractfile(entry)
            if file is not None:
                entryFile = file.read()
                zipPackage.writestr(entryName, entryFile)
        tar.close()
        zipPackage.close()
        
        if path.exists(registration_key + ".tar"):
            os.remove(registration_key+ ".tar")
    print("package conversion complete")
