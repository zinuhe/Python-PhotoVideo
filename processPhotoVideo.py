# Python3 processPhotoVideo.py
# To process photo and video files under same folder
# By example files from iPhone

# TODO
# -Si no hay fotos o videos, no crear ese folder
# -Linea 71 eso se puede cambiar en processPhotoVideoSony hay mejores ejemplos
# -estoy revisando lo de las fechas sacadas de EXIF, se puede organizar mejor como en processPhotoVideoSony

import os, shutil, glob
import exifread #pip install exifread
import os.path, time, calendar

from subprocess import check_output, check_call
# from datetime import datetime

PHOTO_TYPES = ('*.jpg', '*.JPG', '*.JPE', '*.jpe', '*.JPEG', '*.jpeg', '*.png', '*.PNG')
VIDEO_TYPES = ('*.mov', '*.MOV', '*.mp4', '*.MP4')

# Creates a new folder and return a boolean
def createFolder(pathNewFolder):
    isCreatedOrExists = False
    if os.path.isdir(pathNewFolder) == False:
        try:
            os.mkdir(pathNewFolder)
        except OSError:
            print(f"Creation of the directory {pathNewFolder} failed")
        else:
            # print(f"Successfully created the folder: {pathNewFolder}")
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
    
    # print(f"Files Names: {filesNames}")
    filesNames.sort()
    # print(f"Files Names sort: {filesNames}")
    return filesNames


# Iterates throught files and moves them
def processMediaFiles(mediaFiles, mediaPath):
    index = 1

    # for file in mediaFiles:
    for i, file in enumerate(mediaFiles, start=1):
        #print(f"file: {file}")

        # Open media file for reading (binary mode)
        f = open(currentPath + file, 'rb')

        # Return Exif tags
        tags = exifread.process_file(f, details=False, stop_tag='EXIF DateTimeDigitized')

        if bool(tags):
            dateFromExif = tags['EXIF DateTimeDigitized']
            # print(f"dateFromExif: {dateFromExif}")

            # It needs to be converted to datetime - 2021-07-15 09:42:07
            dateTimeFromExif = datetime.strptime(str(dateFromExif), '%Y:%m:%d %H:%M:%S')
            # print(f"dateTimeFromExif: {dateTimeFromExif}")
            # print(f"{dateTimeFromExif.year}-{dateTimeFromExif.month}-{dateTimeFromExif.day}"")

            # validDateTimeDigitized = str(dateFromExif)[0:10].replace(':', '-')  ___TO_DELETE

            # get year
            # strYear = str(dateFromExif)[0:4]  ___TO_DELETE
            strYear = dateTimeFromExif.year

            # Creates subfolder with the year if it doesn't already exists
            createFolder(mediaPath + "/" + strYear)
            check_call(['Setfile', '-d', "01/01/" + strYear + " 01:00", mediaPath + "/" + strYear])

            # get month
            # strNumberMonth = str(dateFromExif)[5:7] ___TO_DELETE
            strNumberMonth = dateTimeFromExif.month
            strNameMonth = calendar.month_abbr[int(strNumberMonth)]

            # get day
            # strDay = str(dateFromExif)[8:10]  ___TO_DELETE
            strDay = dateTimeFromExif.day

            if i == 1 :
                # Keep date to restart index
                keepDate = strYear + strNumberMonth + strDay
            elif keepDate == (strYear + strNumberMonth + strDay):
                index += 1
            else:
                index = 1
                keepDate = strYear + strNumberMonth + strDay

            validDateTimeDigitized = "event_" + strNameMonth + "-" + strDay

            print(f"validDateTimeDigitized: {validDateTimeDigitized}")

            if validDateTimeDigitized != '':
                if createFolder(mediaPath + "/" + strYear + "/" + validDateTimeDigitized):
                    # Set the propper date to the new folder just created
                    tmpCreationDate =  strNumberMonth + "/" + strDay + "/" + strYear + " 01:00" #"12/20/2020 16:13"
                    check_call(['Setfile', '-d', tmpCreationDate, mediaPath + "/" + strYear + "/" + validDateTimeDigitized])

                    # Rename files to format 2021-01-31_event_001.ext
                    # newFileName = time.strftime('%Y-%m-%d_event_', time.localtime(os.path.getmtime(currentPath + folder))) + f'{i:03}'
                    newFileName = strYear + "-" + strNumberMonth + "-" + strDay + "_event_" + f'{index:03}' #To add secuency
                    os.rename(file, newFileName)
                    print(f"newFileName: {newFileName}")

                    # Move the file to the new folder
                    # shutil.move(file, mediaPath + "/" + strYear + "/" + validDateTimeDigitized) #WORKING
                    shutil.move(newFileName, mediaPath + "/" + strYear + "/" + validDateTimeDigitized)

                    # print(f"file: {file}")
            else:
                print(f"DATE {validDateTimeDigitized} NOT VALID")
        else:
            print(f"Not EXIF Info for {currentPath} / {file}")

            try:
                # Create folder with creation/modification date from the file
                # modificationTime = time.strftime('%Y-%m-%d', time.localtime(os.path.getmtime(currentPath + file)))
                # creationTime = time.strftime('%Y-%m-%d', time.localtime(os.path.getctime(currentPath + file)))

                # get year
                strYear = time.strftime('%Y', time.localtime(os.path.getmtime(currentPath + file)))

                # Creates subfolder with the year if it does't already exists
                createFolder(mediaPath + "/" + strYear)
                check_call(['Setfile', '-d', "01/01/" + strYear + " 01:00", mediaPath + "/" + strYear])

                # get month
                strNumberMonth = time.strftime('%m', time.localtime(os.path.getmtime(currentPath + file)))
                strNameMonth = calendar.month_abbr[int(strNumberMonth)]

                # get day
                strDay = time.strftime('%d', time.localtime(os.path.getmtime(currentPath + file)))

                validDateTimeDigitized = "event_" + strNameMonth + "-" + strDay

                if validDateTimeDigitized != '':
                    if createFolder(mediaPath + "/" + strYear + "/" + validDateTimeDigitized):
                        # Set the proper date to the new folder just created
                        tmpCreationDate =  strNumberMonth + "/" + strDay + "/" + strYear + " 01:00" #"12/20/2020 16:13"
                        check_call(['Setfile', '-d', tmpCreationDate, mediaPath + "/" + strYear + "/" + validDateTimeDigitized])

                        # Move the file to the new folder
                        shutil.move(file, mediaPath + "/" + strYear + "/" + validDateTimeDigitized)
                else:
                    print(f"DATE {validDateTimeDigitized} NOT VALID")

                # print(f"Created: {creationTime}")
                # time.ctime(modification_time)
            except OSError:
                print(f"Path {currentPath} does not exists or is inaccessible")
                sys.exit()

            # Move to (Photo/Video) root folder
            # shutil.move(file, mediaPath) #Igual mueve el archivo al folder del tipo de media
    return


# detect the current working directory
currentPath = os.getcwd() + "/"

# prefix the name of the directory to be created
photoPath = currentPath + "photo"
videoPath = currentPath + "video"

# define the access rights
# access_rights = 0o755

createFolder(photoPath)
createFolder(videoPath)

photoFiles = getNameFiles(PHOTO_TYPES) #returns an array with photo files
videoFiles = getNameFiles(VIDEO_TYPES) #returns an array with video files


# Process photo files
processMediaFiles(photoFiles, photoPath)

# Process video files
processMediaFiles(videoFiles, videoPath)

