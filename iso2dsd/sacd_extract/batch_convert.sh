#!/bin/bash

for file in *; do
    if [ -f "$file" ]; then
        if [[ "$file" == *.dsf ]]; then
            dsf2flac "$file"
        fi
    fi
done