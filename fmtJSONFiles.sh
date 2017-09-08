#!/bin/bash
# This script recursively finds all ".json" files under current directory and pretty formats them.

while IFS= read -r -d $'\0' file; do
	echo $file
	python -m json.tool $file > $file"_formatted"
done < <(find . -iname "*.json" -print0)
