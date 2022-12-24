# Combine Genres
# author: hypermodified
# This python script loops through a directory, looks at whether there is data in the genre vorbis tag and if there is opens  amd adds ot tp the associated origin file
# This script add the genre to the Tags field in the orgin file.
# This has only been tested to work with flac files.
# It can handle albums with artwork folders or multiple disc folders in them. It can also handle specials characters.
# It has been tested and works in both Ubuntu Linux and Windows 10.

# Before running this script install the dependencies
# pip install mutagen

# Import dependencies
import os  # Imports functionality that let's you interact with your operating system
import yaml  # Imports yaml
import shutil  # Imports functionality that lets you copy files and directory
import datetime  # Imports functionality that lets you make timestamps
import mutagen  # Imports functionality to get metadata from music files

#  Set your directories here
album_directory = "M:\Python Test Environment\Albums1"  # Which directory do you want to start with?
log_directory = "M:\Python Test Environment\Logs"  # Which directory do you want the log in?

# Set whether you are using nested folders or have all albums in one directory here
# If you have all your ablums in one music directory Music/Album_name then set this value to 1
# If you have all your albums nest in a Music/Artist/Album style of pattern set this value to 2
# The default is 1
album_depth = 1

# Establishes the counters for completed albums and missing origin files
count = 0
total_count = 0
error_message = 0
good_missing = 0
bad_missing = 0
parse_error = 0
origin_old = 0
missing_origin_genre = 0

# identifies album directory level
path_segments = album_directory.split(os.sep)
segments = len(path_segments)
album_location_check = segments + album_depth


# A function to log events
def log_outcomes(directory, log_name, message, log_list):
    global log_directory

    script_name = "Origin Write Tags Script"
    today = datetime.datetime.now()
    log_name = f"{log_name}.txt"
    album_name = directory.split(os.sep)
    album_name = album_name[-1]
    log_path = os.path.join(log_directory, log_name)
    with open(log_path, "a", encoding="utf-8") as log_name:
        log_name.write(f"--{today:%b, %d %Y} at {today:%H:%M:%S} from the {script_name}.\n")
        log_name.write(f"The album folder {album_name} {message}.\n")
        if log_list != None:
            log_name.write("\n".join(map(str, log_list)))
            log_name.write("\n")
        log_name.write(f"Album location: {directory}\n")
        log_name.write(" \n")
        log_name.close()


# A function that determines if there is an error
def error_exists(error_type):
    global error_message

    if error_type >= 1:
        error_message += 1  # variable will increment if statement is true
        return "Warning"
    else:
        return "Info"


# A function that writes a summary of what the script did at the end of the process
def summary_text():
    global count
    global total_count
    global error_message
    global parse_error
    global bad_missing
    global good_missing
    global origin_old
    global missing_origin_genre

    print("")
    #print(f"This script wrote tags to {count} tracks from {total_count} albums.")
    print("This script looks for potential missing files or errors. The following messages outline whether any were found.")

    error_status = error_exists(parse_error)
    print(f"--{error_status}: There were {parse_error} albums skipped due to not being able to open the yaml. Redownload the yaml file.")
    error_status = error_exists(origin_old)
    print(f"--{error_status}: There were {origin_old} origin files that do not have the needed metadata and need to be updated.")
    error_status = error_exists(bad_missing)
    print(f"--{error_status}: There were {bad_missing} folders missing an origin files that should have had them.")
    error_status = error_exists(missing_origin_genre)
    print(f"--{error_status}: There were {missing_origin_genre} folders missing genre tags in their origin files.")
    error_status = error_exists(good_missing)
    print(f"--Info: Some folders didn't have origin files and probably shouldn't have origin files. {good_missing} of these folders were identified.")

    if error_message >= 1:
        print("Check the logs to see which folders had errors and what they were and which tracks had metadata written to them.")
    else:
        print("There were no errors.")


# A function to check whether the directory is a an album or a sub-directory and returns an origin file location and album name
def level_check(directory):
    global total_count
    global album_location_check
    global album_directory

    print(f"--Directory: {directory}")
    print(f"--The albums are stored {album_location_check} folders deep.")

    path_segments = directory.split(os.sep)
    directory_location = len(path_segments)

    print(f"--This folder is {directory_location} folders deep.")

    # Checks to see if a folder is an album or subdirectory by looking at how many segments are in a path and returns origin location and album name
    if album_location_check == directory_location and album_depth == 1:
        print("--This is an album.")
        origin_location = os.path.join(directory, "origin.yaml")
        album_name = path_segments[-1]
        total_count += 1  # variable will increment every loop iteration
        return origin_location, album_name
    elif album_location_check == directory_location and album_depth == 2:
        print("--This is an album.")
        origin_location = os.path.join(directory, "origin.yaml")
        album_name = os.path.join(path_segments[-2], path_segments[-1])
        total_count += 1  # variable will increment every loop iteration
        return origin_location, album_name
    elif album_location_check < directory_location and album_depth == 1:
        print("--This is a sub-directory")
        origin_location = os.path.join(album_directory, path_segments[-2], "origin.yaml")
        album_name = os.path.join(path_segments[-2], path_segments[-1])
        return origin_location, album_name
    elif album_location_check < directory_location and album_depth == 2:
        print("--This is a sub-directory")
        origin_location = os.path.join(album_directory, path_segments[-3], path_segments[-2], "origin.yaml")
        album_name = os.path.join(path_segments[-3], path_segments[-2], path_segments[-1])
        return origin_location, album_name
    elif album_location_check > directory_location and album_depth == 2:
        print("--This is an artist folder.")
        origin_location = None
        album_name = None
        return origin_location, album_name


# Rethink this so it checks all files and if any end in flac go forth
# A function to check whether a directory has flac and should be checked further
def flac_check(directory):

    # Loop through the directory and see if any file is a flac
    for fname in os.listdir(directory):
        if fname.endswith(".flac"):
            print("--There are flac in this directory.")
            return True

    print("--There are no flac in this directory.")
    return False


# A function to check if the origin file is there and to determine whether it is supposed to be there.
def check_file(directory):
    global good_missing
    global bad_missing
    global album_location_check

    # check to see if there is an origin file
    file_exists = os.path.exists("origin.yaml")
    # if origin file exists, load it, copy, and rename
    if file_exists == True:
        return True
    else:
        # split the directory to make sure that it distinguishes between folders that should and shouldn't have origin files
        current_path_segments = directory.split(os.sep)
        current_segments = len(current_path_segments)
        # create different log files depending on whether the origin file is missing somewhere it shouldn't be
        if album_location_check != current_segments:
            # log the missing origin file folders that are likely supposed to be missing
            print("--An origin file is missing from a folder that should not have one.")
            print("--Logged missing origin file.")
            log_name = "good-missing-origin"
            log_message = "origin file is missing from a folder that should not have one.\nSince it shouldn't be there it is probably fine but you can double check"
            log_list = None
            log_outcomes(directory, log_name, log_message, log_list)
            good_missing += 1  # variable will increment every loop iteration
            return False
        else:
            # log the missing origin file folders that are not likely supposed to be missing
            print("--An origin file is missing from a folder that should have one.")
            print("--Logged missing origin file.")
            log_name = "bad-missing-origin"
            log_message = "origin file is missing from a folder that should have one"
            log_list = None
            log_outcomes(directory, log_name, log_message, log_list)
            bad_missing += 1  # variable will increment every loop iteration
            return False


#  A function that gets the directory and then opens the origin file and extracts the needed variables
def get_metadata(directory, origin_location, album_name):
    global count
    global parse_error
    global origin_old
    global bad_missing
    global missing_origin_genre

    print(f"--Getting metadata for {album_name}")
    print(f"--From: {origin_location}")

    # check to see if there is an origin file is supposed to be in this specific directory
    file_exists = check_file(directory)
    # check to see the origin file location variable exists
    location_exists = os.path.exists(origin_location)

    if location_exists == True:
        print("--The origin file location is valid.")
        # open the yaml
        try:
            with open(origin_location, encoding="utf-8") as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
        except:
            print("--There was an issue parsing the yaml file and the cover could not be downloaded.")
            print("--Logged missing cover due to parse error. Redownload origin file.")
            log_name = "parse-error"
            log_message = "had an error parsing the yaml and the cover art could not be downloaded. Redownload the origin file"
            log_list = None
            log_outcomes(directory, log_name, log_message, log_list)
            parse_error += 1  # variable will increment every loop iteration
            return
        # check to see if the origin file has the corect metadata
        if "Cover" in data.keys():
            print("--You are using the correct version of gazelle-origin.")

            # turn the data into variable 
            origin_genre = data["Tags"]
            if origin_genre != None:
                # remove spaces in comma delimited string
                origin_genre = origin_genre.replace(" ", "")
                # turn string into list
                origin_genre = origin_genre.split(',')
                f.close()
                return origin_genre
            else:
                # log the missing genre tag information in origin file
                print("--There are no genre tags in the origin file.")
                print("--Logged missing genre tag in origin file.")
                log_name = "missing_origin_genre"
                log_message = "genre tag missing in origin file"
                log_list = None
                log_outcomes(directory, log_name, log_message, log_list)
                missing_origin_genre += 1  # variable will increment every loop iteration
        else:
            print("--You need to update your origin files with more metadata.")
            print("--Switch to the gazelle-origin fork here: https://github.com/spinfast319/gazelle-origin")
            print("--Then run: https://github.com/spinfast319/Update-Gazelle-Origin-Files")
            print("--Then try this script again.")
            print("--Logged out of date origin file.")
            log_name = "out-of-date-origin"
            log_message = "origin file out of date"
            log_list = None
            log_outcomes(directory, log_name, log_message, log_list)
            origin_old += 1  # variable will increment every loop iteration
    else:
        # log the missing origin file folders that are not likely supposed to be missing
        print("--An origin file is missing from a folder that should have one.")
        print("--Logged missing origin file.")
        log_name = "bad-missing-origin"
        log_message = "origin file is missing from a folder that should have one"
        log_list = None
        log_outcomes(directory, log_name, log_message, log_list)
        bad_missing += 1  # variable will increment every loop iteration


def check_genre(directory, album_name):
    global count

    print("--Checking for genre tag.")

    # Open track in directory and see if genre tag is populated
    for fname in os.listdir(directory):
        if fname.endswith(".flac"):
            tag_metadata = mutagen.File(fname)
            if "GENRE" not in tag_metadata:
                print (f"--The album {album_name} does not have a genre tag.")
                break
            else:    
                print(f"--Track Name: {fname}")
                #  check genre tag
                if tag_metadata["GENRE"] != None:
                    genre = tag_metadata["GENRE"]
                    print(genre)
                    cleaned_genre = clean_genre(genre)
                    
                    # this is for the output and nothing else.
                    print(cleaned_genre)
                    genre_list = ', '.join(cleaned_genre)
                    print (f" The genre tag is {genre_list}.")
                    return cleaned_genre
                else:
                    print ("No tag.")
                    break
                count += 1  # variable will increment every loop iteration
    
'''
    # log the album the name change
    log_name = "files_retagged"
    log_message = f"had {tracks_retagged} files retagged"
    log_list = retag_list
    log_outcomes(directory, log_name, log_message, log_list)'''
    
def clean_genre(genre):    
    #make genre lowercase
    genre_lower = [tag.lower() for tag in genre]
    #replace / with ,
    genre_noslash = [tag.replace("/", ",") for tag in genre_lower]
    #replace ; with ,
    genre_nosemi = [tag.replace(";", ",") for tag in genre_noslash]
    #turn list into string
    genre_string = ', '.join(genre_nosemi)
    #turn string into list seperating tags by comma
    genre_list = genre_string.split(',')
    #strip tags
    genre_strip = [tag.strip() for tag in genre_list]
    #remove null characters
    #replace - with .
    genre_nodash = [tag.replace("-", ".") for tag in genre_strip]
    #replace space with .
    #replace & with and
    #fix drum and bass
    #fix melodic house & techno
    return genre_nodash

def compare_write(genre_vorbis, genre_origin, album_name):
    global count
    print("LOOK HERE")
    print(genre_vorbis)
    print(genre_origin)
    
    for i in genre_vorbis:
        if i in genre_origin:
            print("Genre already in origin")
        else:
            print(f"--Adding {i} to the gengre tags in origin file")
            genre_origin.append(i)
            
    print(genre_origin)       
            


# The main function that controls the flow of the script
def main():

    try:
        # intro text
        print("")
        print("Join me, and together...")
        print("")

        # Get all the subdirectories of album_directory recursively and store them in a list:
        directories = [os.path.abspath(x[0]) for x in os.walk(album_directory)]
        directories.remove(os.path.abspath(album_directory))  # If you don't want your main directory included

        #  Run a loop that goes into each directory identified in the list and runs the genre merging process
        for i in directories:
            os.chdir(i)  # Change working Directory
            print("")
            print("Merging genres starting.")
            # establish directory level
            origin_location, album_name = level_check(i)
            # check for flac
            is_flac = flac_check(i)
            # check if vorbis tag for genre is populated
            # open orgin file
            # check if genre tag is already listed
            # write genre to tag key value pair
            if is_flac == True:
                genre_vorbis = check_genre(i, album_name)
                #if genre_vorbis != None:
                    #genre_origin = get_metadata(i, origin_location, album_name)
                    #if genre_origin != None:
                     #   compare_write(genre_vorbis, genre_origin, album_name)
                #else: 
                 #   print("No genre tag.")
                #write_tags(i, origin_metadata, album_name)
            else:
                print("No flac files.")

    finally:
        # Summary text
        print("")
        print("...we can rule the galaxy as father and son.")
        # run summary text function to provide error messages
        summary_text()
        print("")


if __name__ == "__main__":
    main()
