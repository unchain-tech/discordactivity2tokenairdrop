#!/usr/bin/sh

# get env variables
source ./config.txt

serverID=936573458748432405 #UNCHAIN server ID
userID=$DISCORDUSER # user token https://github.com/Tyrrrz/DiscordChatExporter/blob/master/.docs/Token-and-IDs.md#how-to-get-a-user-token

START="2024-01-01"
END="2024-03-24"

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
sh crawl_discordServer.sh

#activate python venv
source ./venv/bin/activate

#count CHAI distribution and save to csv
python3 ./chai_counter.py

#deactivate python venv
deactivate
