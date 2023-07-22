#!/bin/bash

# Define the folder path where the zip files are located
folder_path="/Users/federicopalai/Documents/Codes/Python/kodi_addons/"

# Change directory to the specified folder
cd "$folder_path" || exit

# Check if there is only one zip file in the folder
zip_count=$(ls -1 *.zip | wc -l)
if [ "$zip_count" -ne 1 ]; then
  echo "Error: There should be exactly one zip file in the folder."
  exit 1
fi

# Get the name of the zip file (assuming the filename format is 'test.v.1.0.0.zip')
zip_file=$(ls -1 *.zip)

# Extract the version number from the zip file name
version=$(echo "$zip_file" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)

# Split the version number into its components
IFS='.' read -r -a version_components <<< "$version"

# Check if the last number is 9
if [ "${version_components[2]}" -eq 9 ]; then
  # Increment the second-to-last number
  ((version_components[1]++))
  # Set the last number to 0
  version_components[2]=0
else
  # Increment the last number
  ((version_components[2]++))
fi

# Assemble the new version number
new_version="${version_components[0]}.${version_components[1]}.${version_components[2]}"

# Create a new zip file with the incremented version number
new_zip_file="${zip_file/$version/$new_version}"
zip -r "$new_zip_file" "./anime.saturn.addon"

# Delete the previous zip file
rm "$zip_file"

echo "New zip file created: $new_zip_file"
