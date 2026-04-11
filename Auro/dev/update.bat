@echo off
echo Auro Engine : Starting Node Update ...
echo Fetching Main branch from Github ....

git pull origin main

echo Restarting Auro 

pm2 restart Auro --interpreter "C:\Users\SERVER\AppData\Local\Programs\Python\Python314\python.exe"

echo Update Complete .