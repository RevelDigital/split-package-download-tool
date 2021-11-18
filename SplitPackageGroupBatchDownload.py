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

retry_interval = 15
max_retry_attempts = 5
enable_retry_limit = False
request_timeout = 30

api_key = os.environ.get('REVEL_SPLIT_PACKAGE_API_KEY')
if api_key is None:
    print(Fore.RED + "API Key environmental variable not found.")
    print("Please create a new variable using key name: 'REVEL_SPLIT_PACKAGE_API_KEY'")
    print("Close script and try again or contact support." + Fore.RESET)
    close = input("Press enter to exit script")
    sys.exit()

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

def apiRequest(url, streamType, run_download_animation):
    global enable_loading_animation
    global enable_retry_limit
    global request_timeout
    retry_count = 0
    enable_loading_animation = run_download_animation
    while enable_retry_limit == False or (enable_retry_limit == True and retry_count < max_retry_attempts):
        try:
            response = requests.get(url, stream=streamType, timeout=request_timeout)
        except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
            enable_loading_animation = False
            sys.stdout.write('\r')
            print(Fore.RED + "Connection Error")
            print("Error: " + str(e) + Fore.RESET)
            print("Retrying in " + str(retry_interval) + " seconds")
            timerAnimation(retry_interval)
            print("\nRetrying now")
            enable_loading_animation = run_download_animation
        else:
            if response.status_code == requests.codes.ok:
                return response
            else:
                enable_loading_animation = False
                sys.stdout.write('\r')
                print(Fore.RED + "Bad response code recevied")
                print("Response code: " + str(response.status_code))
                print("Response body:" + str(response.content) + Fore.RESET)
                print("Retrying in " + str(retry_interval) + " seconds")
                timerAnimation(retry_interval)
                print("\nRetrying now")
                enable_loading_animation = run_download_animation
        retry_count += 1
    return None

def removeFile(filename):
    if path.exists(filename):
        os.remove(filename)

def removeDirectory(directory):
    if path.isdir(directory):
        shutil.rmtree(directory)

def get_group_id():
    response = apiRequest("https://api.reveldigital.com/api/devices/groups?api_key=" + api_key + "&include_snap=false", False, False)
    deviceGroupsJSON = response.json()
    idx = 1
    for group in deviceGroupsJSON:
        print(str(idx) + ".) " + group["name"] + "  (" + str(group["count"]) + ")")
        idx += 1
    device_group_index = int(input("\nEnter number associated with device group: "))
    print("")
    device_group_index -= 1
    if device_group_index > -1 and device_group_index < len(deviceGroupsJSON):
        device_group_name = deviceGroupsJSON[device_group_index]["name"]
        print("Group Selected: " + device_group_name)
        if deviceGroupsJSON[device_group_index]["count"] == 0:
            print("Device group doesn't contain any devices. Please select another group\n")
            return get_group_id()
        else:
            device_group_id = deviceGroupsJSON[device_group_index]["id"]
            return device_group_id
    else:
        print("Invalid entry")
        return get_group_id()

response = apiRequest("https://api.reveldigital.com/api/status", False, False)

if path.exists("Media.tar") and path.exists("GroupId.txt"):
    print("Media package already exists. Loading device group from file. Skipping steps 1 and 2")
    with open('GroupId.txt') as text_file:
        group_id = text_file.read()
    if path.exists("Media.tar"):
        tar = tarfile.open("Media.tar", 'r')
        for entry in tar:
            if entry.name.startswith("Media"):
                tar.extract(entry)
        tar.close()
    else:    
        print(Fore.RED + "Something went wrong.")
        print("MediaPackage.tar not found")
        print("Close script and try again or contact support." + Fore.RESET)
        close = input("Press enter to exit script")
        sys.exit()
else:
    print("Missing Media.tar and/or GroupId.txt files. Select device group to pull media from")
    removeFile("MediaPackage.tar")
    removeFile("Media.tar")
    removeFile("GroupId.txt")
    removeDirectory('Media')
    group_id = get_group_id()
    with open('GroupId.txt', 'w') as outfile:
        outfile.write(group_id)
    response = apiRequest("https://api.reveldigital.com/api/devices?api_key=" + api_key + "&group_id=" + group_id + "&include_snap=false", False, False)
    groupDevicesJSON = response.json()
    media_reference_device_reg_key = groupDevicesJSON[0]["registration_key"]
    print("Downloading shared media...")
    # Getting media package from shared media device
    response = apiRequest("https://svc1.reveldigital.com/v2/package/get/" + media_reference_device_reg_key + "?usb=true&tar=true", True, True)
    with open("MediaPackage.tar", 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            f.write(chunk)
    f.close()
    response.close()
    enable_loading_animation = False
    sys.stdout.write('\r             Media download complete\n\n')

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
        print("MediaPackage.tar not found")
        print("Close script and try again or contact support." + Fore.RESET)
        close = input("Press enter to exit script")
        sys.exit()

    # verify Media folder exists and isn't empty
    if path.isdir('Media'):
        if len(os.listdir("Media")) == 0:
            removeFile("MediaPackage.tar")
            removeDirectory('Media')
            print("Media directory is empty")
            print("Check device schedule in CMS and try again")
            close = input("Press enter to exit script")
            sys.exit()
    else:
        removeFile("MediaPackage.tar")
        print(Fore.RED + "Something went wrong.")
        print("Media folder doesn't exist")
        print("Close script and try again or contact support." + Fore.RESET)
        close = input("Press enter to exit script")
        sys.exit()

    # Creating Media.tar file
    with tarfile.open('Media.tar', "a", format=tarfile.GNU_FORMAT) as archive:
        archive.add('Media')
    archive.close()
    print("             Media.tar file created\n")

    # remove unneeded files/directories
    removeFile("MediaPackage.tar")
    
#download the update package tar file for each device in group, excluding media
print("\nGetting new devices now...\n")
response = apiRequest("https://api.reveldigital.com/api/devices?api_key=" + api_key + "&group_id=" + group_id + "&include_snap=false", False, False)
devicesJSON = response.json()
response.close()
newDeviceCount = 0
enable_retry_limit = True
for device in devicesJSON:
    if (path.exists(device["registration_key"] + '.zip')) or (path.exists(device["registration_key"] + '.tar')):
        print("package with matching registration key found in directory " + device["registration_key"])
        print("Skipping download for device\n")
    else:
        print(Fore.GREEN + "Device Found: " + device["name"] + ". Downloading package now..." + Fore.RESET)
        response = apiRequest("https://svc1.reveldigital.com/v2/package/get/" + device["registration_key"] + "?usb=true&tar=true&excludeMedia=true", True, True)
        if response is None:
            print(Fore.RED + "Too many retry attempts made, skipping device" + Fore.RESET)
        else:
            newDeviceCount += 1
            with open(device["registration_key"] + ".tar", 'wb') as f:
                f.write(response.raw.read())
            response.close()
            enable_loading_animation = False
            sys.stdout.write('\rDownload complete')
        print("\n")

print("Check complete. " + str(newDeviceCount)+ " new Device(s) found")

def tarContainsMedia(tarPackage):
    tar = tarfile.open(tarPackage, 'r')
    containsMedia = False
    for entry in tar:
        if entry.name.startswith("Media"):
            if not containsMedia:
                containsMedia = True
                break
    tar.close()
    return containsMedia
        
rehydrate = input("Would you like to merge the Media content with downloaded device packages? (y/n)")
if rehydrate == "y":
    if not path.isdir('Media'):
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
            if tarContainsMedia(tar_name):
                print("tar file already contains media folder")
                print("skipping package")
            else:
                print("Merging device package: " + device["name"])
                with tarfile.open(tar_name, "a", format=tarfile.GNU_FORMAT) as archive:
                    archive.add('Media')
                archive.close()
        elif path.exists(device["registration_key"] + ".zip"):
            print("skipping zip package")
        else:
            print(Fore.RED + "Something went wrong.")
            print("Package not found for registration key: " + device["registration_key"])
            print("package skipped" + Fore.RESET)
    print("package merge complete")
removeDirectory('Media')

convert = input("Would you like to convert the tar package files to zip file for Android? (y/n)")
if convert == "y":
    for device in devicesJSON:
        registration_key = device["registration_key"]
        if path.exists(registration_key + ".tar") and not path.exists(registration_key + ".zip"):
            print("Compressing device package: " + device["name"])
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
        else:
            print("Skipping device name: " + device["name"] + ". Either zip file already exists or tar file is missing. reg key: " + registration_key)
    print("package conversion complete")
