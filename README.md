# device-registration-monitoring-tool
Saves Media.tar file of dummy device. Then continuously monitors account for new devices. When a new device is registered the tar package is downloaded, excluding the media content.

## Installation

Built for [Python](https://www.python.org/downloads/) version 3.9.6 or higher.
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requests and colorama.

```bash
pip install requests
pip install colorama
```

Note: Place the Python script file 'DeviceRegistrationMonitoringTool.py' within an empty folder before running it. All files will be added to that directory. 

## Useage
Before running the script, open it in some text editor and include the API key for your Revel Digital account. Insert API key within the set of double quotes following the api_key variable near the top of the script. You can find your [API key](https://as1.reveldigital.com/account/api) by clicking the user icon in the top right corner of the CMS portal. Navigate to 'Account Information' > 'Developer API', and choose GENERATE NEW API KEY

Similarly, the registration key of the dummy device must be included as well. Use dummy_device_reg_key to store the key as listed below

```
api_key = ""
dummy_device_reg_key = ""
```

Save the changes and then run the script. This script includes animations. For best performance run the script using command prompt.

Once the script is running it won't require any user input. Before closing the script make sure a download isn't in progress. Before copying copying a package to a USB drive, make sure that it's fully downloaded.

The script also generates a DeviceList.txt file which allows the script to detect new devices if they get registered when the script isn't running. For this functionality to work correctly, the file should not me removed or deleted. This functionality will only be available starting with the second time the script is ran.

The script also downloads one device update package including media. When the download is complete, the script will provide the option of merging the one media download file with the all packages that were downloaded.