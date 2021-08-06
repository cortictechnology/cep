FROM python:3.7-slim-buster
RUN apt-get update && apt-get -y upgrade
RUN apt-get -y update && apt-get -y install \
    curl \
    wget \
    sudo \
    build-essential \
    pkg-config \
    libatlas3-base \
    libatlas-base-dev \
    gfortran \
    lsb-release \
    unzip \
    ffmpeg \
    sox \
    git \
    libsox-fmt-all  \
    libtool \
    libasound2-dev

RUN pip install ws4py cython numpy scipy paho-mqtt

RUN apt-get update && apt-get -y install \
    python3-dev \
    python3-numpy \
    libsdl-dev \
    libsdl-image1.2-dev \
    libsdl-mixer1.2-dev \
    libsdl-ttf2.0-dev \
    libsmpeg-dev \
    libportmidi-dev \
    libavformat-dev \
    libswscale-dev \
    libjpeg-dev \
    libfreetype6-dev \
    portaudio19-dev \
    mplayer \
    python3-setuptools; \
    pip3 install pygame==1.9.6; \
    pip3 install PyAudio; \
    pip3 install webrtcvad~=2.0.10; \
    pip3 install halo~=0.0.18

RUN wget https://github.com/mozilla/DeepSpeech/releases/download/v0.9.1/deepspeech-0.9.1-cp37-cp37m-linux_armv7l.whl; \
    pip install deepspeech-0.9.1-cp37-cp37m-linux_armv7l.whl; \
    mkdir /opt/deepspeech-models; \
    wget https://github.com/mozilla/DeepSpeech/releases/download/v0.9.1/deepspeech-0.9.1-models.tflite; \
    wget https://github.com/mozilla/DeepSpeech/releases/download/v0.9.1/deepspeech-0.9.1-models-zh-CN.tflite; \
    wget https://github.com/mozilla/DeepSpeech/releases/download/v0.9.1/deepspeech-0.9.1-models.scorer; \
    wget https://github.com/mozilla/DeepSpeech/releases/download/v0.9.1/deepspeech-0.9.1-models-zh-CN.scorer; \
    mv deepspeech-0.9.1-models.tflite deepspeech-0.9.1-models-zh-CN.tflite deepspeech-0.9.1-models.scorer deepspeech-0.9.1-models-zh-CN.scorer /opt/deepspeech-models; \
    rm deepspeech-0.9.1-cp37-cp37m-linux_armv7l.whl

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list; \
    apt-get -y install apt-transport-https ca-certificates gnupg; \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -; \
    apt-get update && apt-get -y install google-cloud-sdk; \
    pip install google-cloud-speech

WORKDIR /root
RUN apt-get -y install gcc make pkg-config automake libtool libasound2-dev; \
    git clone https://github.com/MycroftAI/mimic1.git; \
    cd mimic1; \
    ./dependencies.sh --prefix="/usr/local"; \
    ./autogen.sh; \
    ./configure --prefix="/usr/local"; \
    make; \
    cp mimic /usr/local/bin

RUN apt-get clean; \
    apt-get -y autoremove

WORKDIR /root
RUN rm -rf .cache; \
    rm -rf mimic1
