#!/bin/bash

display_usage() {
  echo "This script must be run as the jump user."
  echo -e "\nUsage:\nrestart-gunicorn.sh [production | staging] \n"
}

## DEBUG
# echo "------"
# echo "Dollar One"
# echo $1
# echo "Dollar Sharp"
# echo $#
# echo "------"

# check that excatly 1 argument was supplied
if [ $# -ne 1 ]; then
  display_usage
  exit 1
fi

# check whether user had supplied -h or --help . If yes display usage
if [[ ( $1 == "--help") ||  $1 == "-h" ]]; then
  display_usage
  exit 0
fi

# display usage if the script is not run as jump user
if [[ $USER != "jump" ]]; then
  display_usage
  exit 1
fi

# check argument is production or staging
if [[ $1 != "staging" && $1 != "production" ]]; then
    display_usage
    exit 1
fi

echo "Stopping gunicorn $1"
pkill -f jump-$1.sock
echo "Starting gunicorn $1"
nice -20 /scr/jump/anaconda3/envs/jump-$1/bin/gunicorn --bind unix:/scr/jump/run/jump-$1.sock --daemon jump.wsgi --workers=32 --threads=8
