# Python3 ~/MyDocuments/Dev/python/python-photoVideo/processPhotoVideo.py
# Python3 processPhotoVideo.py

# From the NAS - TO BE FIXED
# /Volumes/video/2023/CLIP
# Python3 DEV/Python/SourceCode/PhotoVideo/processPhotoVideo.py

# To process photo and video files under the same folder
# By example files from iPhone
# What does it do:
# - Reads the entire content of a folder
# - Creates /photo and /video folders
# - Inside each one creates a folder by year
# - Moves the files to the respective folder

# TODO
# It is not working with '.MP4' files from DJI
# An option for put all the files under the same folder, don't make
#    year/photo/even_ folders only one folder
# Create event's folders with the proper creation time

import os, shutil, glob, sys
import exifread # pip3 install exifread
import os.path, time, calendar
from subprocess import check_output, check_call
from datetime import datetime

# Photo and Video files extensions allowed
PHOTO_TYPES = ('*.dng', '*.DNG', '*.jpe', '*.JPE', '*.jpeg', '*.JPEG', '*.jpg', '*.JPG', '*.png', '*.PNG')
VIDEO_TYPES = ('*.mov', '*.MOV', '*.mp4', '*.MP4')
EVENT_NAME = "event_"

# To manage object file
class file:
    def __init__(self, name, year, monthNumber, monthName, day, fullDate, exifCreation):
        self.name = name
        self.year = year
        self.monthNumber = monthNumber
        self.monthName = monthName
        self.day = day
        self.fullDate = fullDate
        self.exifCreation = exifCreation

# Creates a new folder and return a boolean
def createFolder(pathNewFolder):
    isCreatedOrExists = False
    if os.path.isdir(pathNewFolder) == False:
        try:
            os.mkdir(pathNewFolder)
        except OSError:
            print(f"Creation of the directory {pathNewFolder} failed")
        else:
            isCreatedOrExists = True
    else:
        # print(f"Folder '{pathNewFolder}' already exists")
        isCreatedOrExists = True

    return isCreatedOrExists


# Gets file extensions and return an array of matching files
def getNameFiles(p_extensionFiles):
    filesNames = []
    for ext in p_extensionFiles:
        filesNames.extend(glob.glob(ext))

    return filesNames

# Gets the year from a given date
def getYear(inputDate):
    return str(inputDate.year)

# Gets the month from a given date
def getMonthNumber(inputDate):
    return inputDate.strftime('%m')

# Gets the month's name from a given date
def getMonthName(inputDate):
    return calendar.month_abbr[int(getMonthNumber(inputDate))]

# Gets the day from a given date
def getDay(inputDate):
    return inputDate.strftime('%d')

def getFullDate(inputDate):
    return getYear(inputDate) + getMonthNumber(inputDate) + getDay(inputDate)

# WORKING HERE - something failing here
# Return a list of 'file' objects sorted by creation/modification date
def getFileInfo(listFilesNames):
    files = []

    for fileName in listFilesNames:
        # Open media file for reading (binary mode)
        f = open(currentPath + fileName, 'rb')

        # Return Exif tags
        try:
            tags = exifread.process_file(f, details=False, stop_tag='EXIF DateTimeDigitized')
        except:
            print(f"File '{currentPath}{fileName}' fails getting EXIF DateTimeDigitized")
            sys.exit()
        finally:
            f.close()

        try:
            # print(f"tags: {tags}")
            print(f"bool(tags['EXIF DateTimeDigitized']): {bool(tags['EXIF DateTimeDigitized'])}")
            if bool(tags) and bool(tags['EXIF DateTimeDigitized']):
                # print(f"tags['EXIF DateTimeOriginal']: {tags['EXIF DateTimeOriginal']}")
                # validar que este tag exista
                dateFromExif = tags['EXIF DateTimeDigitized']
                print(f"dateFromExif:{dateFromExif}")
                # It needs to be converted to datetime - 2022-09-28 19:40:07
                dateFrom = datetime.strptime(str(dateFromExif), '%Y:%m:%d %H:%M:%S')
            else: # Not EXIF Info - get creation/modification date from the file
                # creationDate = time.strftime('%Y-%m-%d', time.localtime(os.path.getctime(currentPath + fileName)))
                modificationDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(currentPath + fileName)))
                dateFrom = datetime.strptime(str(modificationDate), '%Y-%m-%d %H:%M:%S')
        except:
            print(f"File '{currentPath}{fileName}' tag info has an issue.")
            sys.exit()
        finally:
            f.close()

        # appending instances to list files
        # ***AGREGAR SOLO LOS QUE NO FALLAN?
        files.append(file(fileName, getYear(dateFrom), getMonthNumber(dateFrom), getMonthName(dateFrom), getDay(dateFrom), getFullDate(dateFrom), dateFrom))
        f.close()

    sortedFiles = sorted(files, key=lambda file:file.exifCreation) # sort by exifCreation
    # for f in sortedFiles:
    #     print(f"{f.name}, {f.year}, {f.monthNumber}, {f.monthName}, {f.day}, {f.fullDate},  {f.exifCreation}")

    return sortedFiles

# Iterates throught files and moves them
def processMediaFiles(mediaFiles, mediaPath):
    index = 1

    for i, file in enumerate(mediaFiles, start=1):
        # Creates subfolder with the year if it doesn't already exists
        createFolder(mediaPath + "/" + file.year)
        check_call(['Setfile', '-d', "01/01/" + file.year + " 01:00", mediaPath + "/" + file.year])

        if i == 1:
            # Keep date to restart index
            keepDate = file.fullDate
        elif keepDate == file.fullDate:
            index += 1
        else:
            index = 1
            keepDate = file.fullDate

        newDate = EVENT_NAME + file.monthName + "-" + file.day

        if newDate != '':
            if createFolder("/".join((mediaPath, file.year, newDate))):
                # Set the proper date to the new folder just created
                tmpCreationDate =  file.monthNumber + "/" + file.day + "/" + file.year + " 01:00" #"12/20/2020 16:13"
                check_call(['Setfile', '-d', tmpCreationDate, mediaPath + "/" + file.year + "/" + newDate])

                fileExtension = os.path.splitext(file.name)[1]

                newFileName = "-".join((file.year, file.monthNumber, file.day))
                newFileName = "".join((newFileName, "_", EVENT_NAME, f'{index:03}', fileExtension)) # {index:03} To add secuency

                os.rename(file.name, newFileName)

                # Move the file (using new name) to the new folder
                shutil.move(newFileName, "/".join((mediaPath, file.year, newDate)))
        else:
            print(f"DATE {newDate} NOT VALID")

    return

# Gets the current working directory
currentPath = os.getcwd() + "/"

# Prefix the name of the directory to be created
photoPath = currentPath + "photo"
videoPath = currentPath + "video"

# define the access rights
# access_rights = 0o755

photoFiles = getNameFiles(PHOTO_TYPES) # returns an array with valid photo files
videoFiles = getNameFiles(VIDEO_TYPES) # returns an array with valid video files

if len(photoFiles) > 0:
    createFolder(photoPath)
    # print(f"{photoFiles}")
    orderedPhotoFiles = getFileInfo(photoFiles) # Fallo aqui cuando lo corri en Desktop/Mover-NAS/Iphone copy
    # Process photo files
    processMediaFiles(orderedPhotoFiles, photoPath)

if len(videoFiles) > 0:
    createFolder(videoPath)
    orderedVideoFiles = getFileInfo(videoFiles)
    # Process video files
    processMediaFiles(orderedVideoFiles, videoPath)
