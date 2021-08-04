# split-package-download-tool
The script continuously monitors a Revel Digital account for new devices. When a new device is registered, the respective tar package is downloaded, excluding the media content.

## Installation

Built for [Python](https://www.python.org/downloads/) version 3.9.6 or higher.
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requests and colorama.

```bash
pip install requests
pip install colorama
```

Note: Place the Python script file 'DeviceRegistrationMonitoringTool.py' within an empty folder before running it. All files will be added to that directory. 

## Usage
A designated device should be registered in Revel that the script can reference to download the correct media files. Before running the script confirm that the correct content has been scheduled to your designated media reference device. If new content is scheduled to the media reference device, you will need to restart the script in order for the new content to be downloaded. Before running the script, open it in some text editor and include the API key for your Revel Digital account. Insert API key within the set of double quotes following the api_key variable near the top of the script. You can find your [API key](https://as1.reveldigital.com/account/api) by clicking the user icon in the top right corner of the CMS portal. Navigate to 'Account Information' > 'Developer API', and choose GENERATE NEW API KEY

The registration key of the designated media reference device must be included as well. Use media_reference_device_reg_key to store the key as listed below

```
api_key = ""
media_reference_device_reg_key = ""
```

Save the changes and then run the script. This script includes animations. For best performance run the script using command prompt.

Once the script is running it shouldn't require any user input. The script will download a Media.tar file containing the media scheduled to the designated media reference device. The script will only check for new devices with the Universal device type. Before closing the script, make sure a download isn't in progress. Before copying a package to a USB drive, confirm that it isn't still downloading.

The script also generates a DeviceList.txt file which allows the script to detect new devices that are registered when the script is not running. For this functionality to work correctly, the file should not be removed or deleted. This functionality will only be available starting on the second time the script runs.
