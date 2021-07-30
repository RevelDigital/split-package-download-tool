import requests
import json
import tarfile
import os
import time
from os import path
import shutil

newDevicePollingInterval = 30
dummy_device_reg_key = ""
api_key = ""

query = {'api_key':api_key, 'include_snap':False}
original_devicesJSON = {}

print("Step 1: Downloading media package for dummy device...")
package = requests.get("https://svc1.reveldigital.com/v2/package/get/" + dummy_device_reg_key + "?tar=true", stream=True)
with open("MediaPackage.tar", 'wb') as f:
    f.write(package.raw.read())

print("        Media package download complete")
print("")
print("Step 2: Creating Media.tar file")
with tarfile.open("MediaPackage.tar") as tar:
    subdir_and_files = [
        tarinfo for tarinfo in tar.getmembers()
            if tarinfo.name.startswith("Media/")
    ]
    tar.extractall(members=subdir_and_files)
    tar.close()
    
# creates media tar archive for runtime media rehydration
media_path = './Media'
media_tar_handle = tarfile.open('Media.tar', "a", format=tarfile.GNU_FORMAT)
for root, dirs, files in os.walk(media_path):
    for file in files:
        media_tar_handle.add(os.path.join(root, file))
media_tar_handle.close()
print("        Media.tar file created")
print("")

# remove files unneeded files/directories
if os.path.exists("MediaPackage.tar"):
  os.remove("MediaPackage.tar")
if os.path.isdir('Media'):
    shutil.rmtree('./Media')

# create or load data from local JSON device list
if path.exists("DeviceList.txt"):
    print("Step 3: Local device list found. Loading devices from list")
    with open('DeviceList.txt') as json_file:
        original_devicesJSON = json.load(json_file)
    print("        Device list loaded")
    print("")
    print("Step 4: Checking in " + str(newDevicePollingInterval) + " seconds for new devices registered since script was last closed")
    print("")
else:
    print("Step 3: Local device list doesn't exist. Generating list device list now...")
    print("Device list created")
    print("")
    original_devices = requests.get("https://api.reveldigital.com/api/devices", params=query)
    original_devicesJSON = original_devices.json()
    with open('DeviceList.txt', 'w') as outfile:
        json.dump(original_devicesJSON, outfile)
    print("Step 4: Checking for new devices in " + str(newDevicePollingInterval) + " seconds")
    print("")

#Monitor for new device registrations and automatically download the device specific package.tar
#get snapshot of all  devices for comparison
while True:
    time.sleep(newDevicePollingInterval)
    print("Checking for new devices now...")
    print("")
    devices = requests.get("https://api.reveldigital.com/api/devices", params=query)
    devicesJSON = devices.json()
    newDeviceCount = 0
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
                print("New Device Found: " + device["name"] + ". Downloading package now...")
                key = device["registration_key"]
                package = requests.get("https://svc1.reveldigital.com/v2/package/get/" + key + "?tar=true&excludeMedia=true", stream=True)
                with open(key + ".tar", 'wb') as f:
                    f.write(package.raw.read())
                print("Download complete")
                print("")
    original_devicesJSON = devicesJSON
    with open('DeviceList.txt', 'w') as outfile:
        json.dump(original_devicesJSON, outfile)
    print("Check complete. " + str(newDeviceCount)+ " new Device(s) found")
    print("")
    print("Checking again in " + str(newDevicePollingInterval) + " seconds")
    print("")
