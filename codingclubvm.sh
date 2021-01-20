pwd
sudo pm2 delete ava
cp -r /home/azureuser/azagent/_work/r1/a/_abhishek0220_Ava/* /home/azureuser/Ava/
cd /home/azureuser/Ava/
source venv/bin/activate
pip install -r requirements.txt
deactivate
sudo pm2 -f start ava.py --no-autorestart --interpreter /home/azureuser/Ava/venv/bin/python
sudo pm2 startup systemd
sudo pm2 save
