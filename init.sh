#!/usr/bin/bash

apt-get update -y # && apt-get upgrade -y
apt-get install git python3-venv python3 cron curl -y

cd $HOME
mkdir -p code

cd $HOME/code/
git clone https://github.com/meanother/cookie.git

cd $HOME/code/cookie
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r req.txt


crontab <<EOF
@reboot sleep 60 && $HOME/code/cookie/run.py
40 23 * * 6 $HOME/code/cookie/run.py
EOF
