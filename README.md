# split-package-download-tool
This project consists of four scripts. SplitPackageDownloadByGroup.py and SplitPackageDownloadByRegKey.py both continuously monitor a Revel Digital account for new devices. When a new device is registered, the respective tar package is downloaded, excluding the media content. Each script has a unique way of selecting the media reference device. SplitPackageGroupBatchDownload.py downloads all device packages in a specific device group. DeviceKeyBatchDownload.py can be used to create device.key files

## Installation

Built for [Python](https://www.python.org/downloads/) version 3.9.6 or higher.
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requests and colorama.

```bash
pip install requests
pip install colorama
```

Note: Place the Python file within an empty folder before running it. All files will be added to that directory. 

## Usage
A designated device should be registered in Revel that the script can reference to download the correct media files. Before running the script confirm that the correct content has been scheduled to your designated media reference device. If new content is scheduled to the media reference device, you will need to restart the script in order for the new content to be downloaded.

Before running the script, a Revel account API key must be provided. You can find your [API key](https://as1.reveldigital.com/account/api) by clicking the user icon in the top right corner of the CMS portal. Navigate to 'Account Information' > 'Developer API', and choose GENERATE NEW API KEY. The API Key can be added as an environmental variable using the following key name.
```
REVEL_SPLIT_PACKAGE_API_KEY
```
The **SplitPackageDownloadByGroup** and **SplitPackageGroupBatchDownload** scripts provides a list of all device groups from the account. Once a group is selected, the first device in that group becomes the media reference device. The group selection is saved and referenced the next time the script is run. To select a new device group, close the script, remove the Media.tar and/or GroupId.txt from your directory, and start the script again.

However, when running the **SplitPackageDownloadByRegKey** script, the registration key of the designated media reference device must be provided. The registration key can be added as an environmental variable using the following key name. 

```
REVEL_SPLIT_PACKAGE_REG_KEY
```

Save the changes and then run the script. This script includes animations. For best performance run the script using command prompt.

Once the script is running it shouldn't require any user input. The script will check if the media package has already been created, and if it hasn't, it will create a Media.tar file containing the media scheduled to the designated media reference device. Before closing the script, make sure a download isn't in progress. Before copying a package to a USB drive, confirm that it isn't still downloading.

The script also generates a DeviceList.txt file which allows the script to detect new devices that are registered when the script is not running. For this functionality to work correctly, the file should not be removed or deleted. This functionality will only be available starting on the second time the script runs.

The **SplitPackageGroupBatchDownload** script provides an option of merging the Media package with all downloaded device packages, and can optionally convert the tar packages to zip file for updating Android devices.

The **DeviceKeyBatchDownload.py** script will save the encrypted registration key to a device.key file for each device where the device name contains a target string (case-insensitive). The target string can be provided when prompted in the console. A folder is created in the current directory to store each device.key file and named using the respective device name. The device.key download will be skipped if a folder with a matching device name already exists in the directory, or if the device name contains illegal characters that can't be used as a folder name.