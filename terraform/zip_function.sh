#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

cd function

FUNCTION_NAME="reddit-giveaway"
OUTPUT_DIR="dist"

mkdir -p $OUTPUT_DIR

poetry export -f requirements.txt --output requirements.txt --without-hashes

# Copy python and requirements in
cp *.py $OUTPUT_DIR/
cp requirements.txt $OUTPUT_DIR/

# Create a .gcloudignore file, not sure if this is necessary but I saw it on stackoverflow so it must be legit
echo "
.gcloudignore
.git
.gitignore
__pycache__/
*.pyc
venv/
.venv/
" > $OUTPUT_DIR/.gcloudignore

# Zippity doo da
(cd $OUTPUT_DIR && zip -r ../../function_export.zip *)
echo "Package created: function_export.zip"

# Clean up
rm -rf $OUTPUT_DIR
rm requirements.txt

echo "Cleanup complet"