# Python3 ~/MyDocuments/Dev/python/python-photoVideo/processPhotoVideoSony.py
# Python3 processPhotoVideoSony.py

# To process folders and files (photos) from Sony camera and drone?
# it will set the folder and file names according to date from EXIF info
# ASSUMING dates on folders and files are correct

# TODO
# Create folder year and then move the other folders in there

import os, shutil, glob, sys
from random import randrange
import exifread #pip3 install exifread
import os.path, time, calendar
from subprocess import check_output, check_call
from datetime import datetime

# Photo files extensions allowed
PHOTO_TYPES = ['.DNG', '.JPE', '.JPEG', '.JPG', '.PNG']
EVENT_NAME = "_event_"

# Current working directory
currentPath = os.getcwd() + "/"

# Only Folders
folders = next(os.walk(currentPath))[1]  # for the current dir use ('.')
folders.sort()
# print(folders)

for folder in folders:
    # Get files inside folder and sort them out
    files = os.listdir(currentPath + "/" + folder)
    files.sort()

    # Get number of files and set secuence
    _secuence = "03"
    if len(files) > 999: _secuence = "04"

    # Stores smallest date from files inside folder
    # to rename the folder with that date
    smallestDatetime = datetime(2100, 12, 31)

    # for i, file in enumerate(files, start=1):
    i = 1
    for file in files:
        # get file extension
        fileExtension = os.path.splitext(file)[1]
        # print(f"fileExtension: {fileExtension}")

        # Filter only PHOTO_TYPES files
        if fileExtension.upper() in PHOTO_TYPES:
            # Open image file for reading (binary mode)
            f = open(currentPath + folder + "/" + file, 'rb')

            # Return Exif tags
            tags = exifread.process_file(f, details=False, stop_tag='EXIF DateTimeDigitized')

            if bool(tags):
                # YYYY:MM:DD H:M:S
                dateFromExif = tags['EXIF DateTimeDigitized']
                # print(f"dateFromExif: {dateFromExif}")

                # It needs to be converted to datetime - 2021-07-15 09:42:07
                dateTimeFromExif = datetime.strptime(str(dateFromExif), '%Y:%m:%d %H:%M:%S')
                # print(f"dateTimeFromExif: {dateTimeFromExif}")
                # print(f"{dateTimeFromExif.year}-{dateTimeFromExif.month}-{dateTimeFromExif.day}"")

                # smallestDatetime, store and compare
                # print(f"Type dateFromExif: {type(dateFromExif)}")
                # print(f"Type dateTimeFromExif: {type(dateTimeFromExif)}")
                if dateTimeFromExif < smallestDatetime:
                    smallestDatetime = dateTimeFromExif

                # YYYY-MM-DD_event_001.ext
                ## newFileName = time.strftime('%Y-%m-%d_event_', time.localtime(os.path.getmtime(currentPath + folder))) + f'{i:03}'
                newFileName = dateTimeFromExif.strftime('%Y-%m-%d') + EVENT_NAME + f"{i:{_secuence}}"
                # print(f"newFileName: {newFileName}")

                newFileName = newFileName + fileExtension
                # print(f"newFileName: {newFileName}")

                if file != newFileName:
                    # Renaming files
                    try:
                        os.rename(folder + "/" + file, folder + "/" + newFileName)
                        # print(f"Renaming file: {folder}/{file} --> {folder}/{newFileName}")
                    except:
                        print(f"Renaming file operation failed: {folder}/{file} --> {folder}/{newFileName}")
                        sys.exit()
                i += 1
            else:
                print(f"No EXIF data for: '{folder}/{file}' file was not renamed")
        else:
            print(f"Not a photo file '{folder}/{file}'")

    # print(f"smallestDatetime: {smallestDatetime}")

    newFolderName = smallestDatetime.strftime("event_%b-%d") #get month name from datetime object
    # print(f"newFolderName: {newFolderName}")

    if newFolderName != '': # TODO 1 - Shouldn't fail just continue with the next one
        if newFolderName != folder:
            try:
                # Rename folder
                # print(f"Renaming folder: {folder} --> {newFolderName}")
                os.rename(folder, newFolderName)
            except:
                print(f"Renaming folder operation failed: {folder} --> {newFolderName}")
                # Could fail because there is already a folder with this name
                # Add a random number to the name to avoid it
                newFolderName = newFolderName + "--" + str(randrange(100)) # get a random Integer from 0 to 99 inclusive
                print(f"Trying: {newFolderName}")
                os.rename(folder, newFolderName)
                # sys.exit()
    else:
        print(f"ERROR - Getting new folder name for {folder} fails - probably date is not valid")
