#!/bin/bash

# Start timer
start=$(date +%s.%N)

# activate virtual environment
source ./.venv/bin/activate

# change directory to the folder with the files
cd "$1"

# iterate over all .bin files in the folder and its subdirectories
find . -type f -name "*.bin" | while read file; do
  # run the Python script with the .bin file as the argument
  echo "Processing file: $file"
  ./.venv/bin/python ./bin_to_csv.py "$file"
done

cd "$1"
# iterate over all .tdms files in the folder and its subdirectories
find . -type f -name "*.tdms" | while read file; do
  # run the Python script with the .tdms file as the argument
  echo "Processing file: $file"
  ./.venv/bin/python ./tdms_to_csv.py "$file"
done

# deactivate virtual environment
deactivate

# End timer
end=$(date +%s.%N)
runtime=$(echo "$end - $start" | bc)

# Print the runtime
echo "Runtime: $runtime seconds"