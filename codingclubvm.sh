cp -r /home/azureuser/azagent/_work/r1/a/_abhishek0220_Ava/* /home/azureuser/Ava/
cd /home/azureuser/Ava/
sudo pm2 delete ava
sudo pm2 -f start ava.py --no-autorestart
sudo pm2 startup systemd
sudo pm2 save
