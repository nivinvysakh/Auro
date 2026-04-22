@echo off
echo Auro Engine : Starting Node Update ...
echo Fetching Main branch from Github ....

git pull origin Main

echo Restarting Auro 

pm2 restart Auro-Bot

echo Update Complete .