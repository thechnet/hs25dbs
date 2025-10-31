#!/bin/bash

clear
cd ist
for file in *
do
  grep -E "^(?:[^;]*;){5}Zug;(?:[^;]*;){7}(Basel|Zürich|Luzern)" "$file" > "../ist-filtered/$file"
  echo Finished $file
done
cd ..
