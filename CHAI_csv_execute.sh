#!/usr/bin/sh

# get env variables
source ./config.txt

# user token https://github.com/Tyrrrz/DiscordChatExporter/blob/master/.docs/Token-and-IDs.md#how-to-get-a-user-token
userID=$DISCORDUSER
serverID=$DISCORDSERVER

#after~before
	# from $(date -j -v-30d +'%Y-%m-%d')
    Af="$START 0:00"
    # until $(date -j -v-1d +'%Y-%m-%d')
    Bf="$END 23:59"

#create directory to store discord data
folderName=$END
mkdir -p discord_log/$folderName

#export variable names
export userID serverID Af Bf folderName

#execute discord crawling script
bash ./crawl_discordServer.sh

#activate python venv
source ./venv/bin/activate

#count CHAI distribution and save to csv
python3 ./chai_counter.py

#deactivate python venv
deactivate
