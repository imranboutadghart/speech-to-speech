#!/bin/bash

data_file="youtube_channels_data.json"

echo "Fetching YouTube channel data..."

python3 get_youtube_channel.py $data_file

echo "Data saved to $data_file"

# to be filled :
	# download files
	# process files
	# finetune the model


echo "Process completed."