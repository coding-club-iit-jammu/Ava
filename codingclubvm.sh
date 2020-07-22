sudo pm2 delete ava
cp -r /home/azureuser/azagent/_work/r1/a/_abhishek0220_Ava/* /home/azureuser/Ava/
cd /home/azureuser/Ava/
pip3 install -r reqirements.txt
sudo pm2 -f start ava.py --no-autorestart --interpreter python3
sudo pm2 startup systemd
sudo pm2 save
