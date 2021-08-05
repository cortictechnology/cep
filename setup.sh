sudo apt update
sudo apt -y full-upgrade

curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh
sudo groupadd docker
sudo gpasswd -a $USER docker
sudo touch /etc/docker/daemon.json
sudo bash -c 'echo "{\"experimental\": true}" > /etc/docker/daemon.json'
sudo mkdir ~/cait_workspace
sudo cp ../samples/block_samples/* ~/cait_workspace
sudo systemctl restart docker
sudo docker pull homeassistant/home-assistant:stable
sudo docker pull cortictech/speech:0.52
sudo docker pull cortictech/nlp:0.52
sudo docker pull cortictech/vision:0.52
sudo docker pull cortictech/control:0.52
sudo docker pull cortictech/broker:0.51
sudo sh -c "echo 'dtparam=spi=on' >> /boot/config.txt"
sudo apt-get install v4l-utils -y
sudo apt-get install portaudio19-dev mplayer graphviz libbluetooth-dev bluez-tools -y
sudo pip3 install docker-compose flask Flask-HTTPAuth flask-login flask_cors paho-mqtt gunicorn pyaudio lolviz cython pybluez
sudo apt-get install npm nodejs -y
sudo touch /opt/accounts
sudo npm install -g configurable-http-proxy
sudo pip3 install notebook
sudo pip3 install jupyterhub
sudo rm get-docker.sh

git clone https://github.com/respeaker/seeed-voicecard.git
cd seeed-voicecard
sudo ./install.sh

echo 'export CURT_PATH=$PWD/src/curt/' >> ~/.bashrc 
echo 'export CAIT_PATH=$PWD/src/cait/' >> ~/.bashrc 
echo 'export CAIT_WEB_PATH=$PWD/src/cait/cortic_webapp/' >> ~/.bashrc 
echo 'export PYTHONPATH=$PYTHONPATH:$CURT_PATH:$CAIT_PATH' >> ~/.bashrc 

sudo reboot now