#!/bin/bash

data_file="youtube_channels_data.json"

echo "Fetching YouTube channel data..."

python3 get_youtube_channel.py $data_file

echo "Data saved to $data_file"

# Download audio files
echo "Downloading audio files..."
python3 download_audio.py $data_file

# to be filled :
	# process files
	# finetune the model


echo "Process completed."