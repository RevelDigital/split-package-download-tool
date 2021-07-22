# USB-package-media-merge-script
 Saves TAR package w/o media for all devices in a group. Can optionally rehydrate TAR files with missing media

## Installation

Built for [Python](https://www.python.org/downloads/) version 3.9.6 or higher.
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requests.

```bash
pip install requests
```

Note: Place the Python script file 'USBUpdatePackageMediaMergeTool.py' within an empty folder before running it. All packages downloads will be saved to that directory. 

## Useage

When the script is ran, you will be prompted for your Revel Digital API Key. You can find your [API key](https://as1.reveldigital.com/account/api) by clicking the user icon in the top right corner of the CMS portal. Navigate to 'Account Information' > 'Developer API', and choose GENERATE NEW API KEY

```
Revel Digital Account API Key:
```

When asked to select a device group, enter the name of any device group exactly as it is listed. The script will will start downloading USB update packages for all devices in the selected device group. Downloaded packages will not contain any media files.

```
Devices
Devices Sub Group 1
Old Devices
New Devices
Enter Device Group Name: Devices
```

The script also downloads one device update package including media. When the download is complete, the script will provide the option of merging the one media download file with the all packages that were downloaded.

```
Would you like to merge the Media content with downloaded device packages? (y/n)
```

Once complete, the folder should include a .tar file for each device in the selected device group. Each filename is the registration key of it's respective device. You will also find a Media folder, a Media.tar file, MediaPackage.tar file, and the original Python script.

All .tar files with registration key filenames can be transferred to your USB drive

The Media Folder and MediaPackage.tar files can be deleted. If you opted to merge media content with all packages on the last step, then you can delete the Media.tar file too.

If the media content was not merged, then your deployment configuration probably requires the Media.tar file to be included on the USB drive.

To generate content for another device group, delete all files except for the python script and run it again.

