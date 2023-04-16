# Origin Combine-Genres now
### A python script loops through a directory looking for flac files, looks at whether there is data in the flac's genre, style and mood vorbis tags and if there is, it adds them to the associated origin file.

Origin files will have genre related tags pulls from the source site of the music.  While the genre tags at the source are often correct they can be wrong or incomplete and in very rare instances missing altogether.  Before writing the genre tags from the origin files to the flac vorbis comments, this script checks to see if the flac files have either genre, mood or style tags already.  If they are present it grabs them and reformats them to match the exact tagging format of the site generating the origin files. It uses the full alias matching of that site to ensure tags are combined in non-duplicative ways. The script then combines them with the tags in the origin file. It removes redundent and non-relevant tags leaving the origin file with a clean set of combined genre tags written to the Tag: field of the origin file.  

It does not alter the flac files in any way allowing for the files to be seeded. This script is meant to be used with another script that writes the tags to the flac files vorbis comments overwriting what is there. 

This project has a dependency on the gazelle-origin project created by x1ppy. gazelle-origin scrapes gazelle based sites and stores the related music metadata in a yaml file in the music albums folder. For this script to work you need to use a fork that has additional metadata including the cover art. The fork that has the most additional metadata right now is: https://github.com/spinfast319/gazelle-origin

This has only been tested to work with flac files and would need to be modified to work with mp3 or other types of music files. The script can handle albums with artwork folders or multiple disc folders in them. It can also handle specials characters. It has been tested and works in both Ubuntu Linux and Windows 10.

## Install and set up
1) Clone this script where you want to run it.

2) Install [mutagen](https://pypi.org/project/mutagen/) with pip. (_note: on some systems it might be pip3_) 

to install it:

```
pip install mutagen
```

3) Install [ruamel yaml](https://pypi.org/project/ruamel.yaml/) with pip. (_note: on some systems it might be pip3_) 

to install it:

```
pip install ruamel.yaml
```

4) Edit the script where it says _Set your directories here_ to set up or specify two directories you will be using. Write them as absolute paths for:

    A. The directory where the albums you want to examine for missing tags are stored  
    B. The directory to store the log files the script creates  

5) Edit the script where it says _Set whether you are using nested folders_ to specify whether you are using nested folders or have all albums in one directory 

    A. If you have all your ablums in one music directory, ie. Music/Album then set this value to 1 (the default)  
    B. If you have all your albums nest in a Music/Artist/Album style of pattern set this value to 2

6) Use your terminal to navigate to the directory the script is in and run the script from the command line.  When it finishes it will output how many albums have combined tags and if you scroll up the output will show you the final tags in an easy to read way.

```
Origin-Combine-Genres.py
```

_note: on linux and mac you will likely need to type "python3 Origin-Combine-Genres.py"_  
_note 2: you can run the script from anywhere if you provide the full path to it_

The script will also create logs listing any album that is missing genre tags in both the origin files and flac files.  


