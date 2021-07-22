import requests
import json
import tarfile
import os

#get API Key for respective account
api_key = input("Revel Digital Account API Key: ")

query = {'api_key':api_key}
#get group name from user
def get_group_name():
    deviceGroups = requests.get("https://api.reveldigital.com/api/devices/groups", params=query)
    deviceGroupsJSON = deviceGroups.json()

    #list Device groups in accout
    for group in deviceGroupsJSON:
        print(group["name"])
    
    group_name_input = input("Enter Device Group Name: ")
    matchCount = 0
    for group in deviceGroupsJSON:
        if group["name"] == group_name_input:
            matchCount += 1
            
    if matchCount == 0:
        print("Name Not Found")
        get_group_name()
    elif matchCount > 1:
        check = input("More than one group name match found. Rename respective device group in Revel, then press enter to try again")
        get_group_name()

    return group_name_input

group_name = get_group_name()
 
query = {'api_key':api_key, 'group_name':group_name, 'include_snap':False}
devices = requests.get("https://api.reveldigital.com/api/devices", params=query)

devicesJSON = devices.json()

#Download the full package for the first device in the group
key = devicesJSON[0]["registration_key"]
package = requests.get("https://svc1.reveldigital.com/v2/package/get/" + key + "?tar=true", stream=True)
with open("MediaPackage.tar", 'wb') as f:
    f.write(package.raw.read())

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

# Iterate all devices in that group and save their respective TAR packages excluding media
for device in devicesJSON:
    print("Downloading device package: " + device["name"])
    key = device["registration_key"]
    package = requests.get("https://svc1.reveldigital.com/v2/package/get/" + key + "?tar=true&excludeMedia=true", stream=True)
    with open(key + ".tar", 'wb') as f:
        f.write(package.raw.read())

rehydrate = input("Would you like to merge the Media content with downloaded device packages? (y/n)")
if rehydrate == "y":
    path = './Media'
    for device in devicesJSON:
        print("Merging device package: " + device["name"])
        key = device["registration_key"]
        tar_name = key + ".tar"
        tar_handle = tarfile.open(tar_name, "a", format=tarfile.GNU_FORMAT)
        for root, dirs, files in os.walk(path):
            for file in files:
                tar_handle.add(os.path.join(root, file))
        tar_handle.close()
