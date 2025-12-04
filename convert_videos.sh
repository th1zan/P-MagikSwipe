#!/bin/bash

# Script pour convertir toutes les vidéos MP4 existantes en WebM
# Utilise ffmpeg pour la conversion

echo "Conversion des vidéos MP4 vers WebM..."

find storage/univers/ -name "*_silent.mp4" -type f -exec bash -c '
mp4_file="$1"
webm_file="${mp4_file%.mp4}.webm"
echo "Conversion de $mp4_file vers $webm_file"
ffmpeg -i "$mp4_file" -c:v libvpx-vp9 -an "$webm_file"
if [ $? -eq 0 ]; then
    rm "$mp4_file"
    echo "Suppression de $mp4_file"
else
    echo "Erreur lors de la conversion de $mp4_file"
fi
' _ {} \;

echo "Conversion terminée."