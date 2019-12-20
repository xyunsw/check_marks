#!/bin/bash

export PATH=~/bin:"/usr/local/bin:$PATH"

my_script="`readlink -f "$0"`"
my_dir="`dirname "$my_script"`"
mkdir -p "$my_dir/marks"
cd "$my_dir/marks" 
if [ $? -ne 0 ]; then 
    echo "failed to cd to $my_dir/marks"
    exit 1
fi

date
echo "Checking give marks..."
# execute the python script here
# e.g.  ../check_give_marks.py seng2011 3222 2511
echo -e "----------------------------------------------------------------------------\n"
