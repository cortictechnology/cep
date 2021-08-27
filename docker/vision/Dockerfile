FROM python:3.8-slim
RUN apt-get -y update && apt-get -y upgrade
RUN apt-get -y update && apt-get -y install \
    curl \
    wget \
    sudo \
    gnupg
    
RUN echo "deb-src http://archive.raspbian.org/raspbian/ buster main contrib non-free rpi" >> /etc/apt/sources.list; \
    echo "deb http://archive.raspberrypi.org/debian/ buster main ui" >> /etc/apt/sources.list.d/raspi.list; \
    echo "deb-src http://archive.raspberrypi.org/debian/ buster main ui" >> /etc/apt/sources.list.d/raspi.list; \
    wget -qO - http://archive.raspberrypi.org/debian/raspberrypi.gpg.key | apt-key add -; \
    wget http://archive.raspbian.org/raspbian.public.key -O - | apt-key add -; \
    apt-get -y update && apt-get -y upgrade

WORKDIR /root

RUN mkdir -p .config/pip; \
    echo "[global]" >> .config/pip/pip.conf; \
    echo "index-url=https://pypi.org/simple" >> .config/pip/pip.conf; \
    echo "extra-index-url=https://www.piwheels.org/simple" >> .config/pip/pip.conf; 

RUN apt-get -y update && apt-get -y install \
    libatlas3-base \
    build-essential \
    cmake \
    pkg-config \
    libatlas-base-dev \
    gfortran \
    libjpeg-dev \
    libtiff5-dev \
    libpng-dev \
    libilmbase-dev \
    libopenexr-dev \
    libgstreamer1.0-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libfontconfig1-dev \
    libcairo2-dev \
    libgdk-pixbuf2.0-dev \
    libpango1.0-dev \
    libgtk2.0-dev \
    libgtk-3-dev \
    libqtgui4 \
    libqtwebkit4 \
    libqt4-test \
    ffmpeg \
    python3-pyqt5 \
    libhdf5-dev \
    libhdf5-serial-dev \
    libhdf5-103 \
    libatomic-ops-dev \
    lsb-release \
    git \
    gcc \
    libtinfo-dev \
    zlib1g-dev \
    libedit-dev \
    libxml2-dev \
    llvm \
    kmod \
    libraspberrypi0 \
    libraspberrypi-dev \
    libraspberrypi-bin \
    libusb-1.0-0-dev

RUN pip3 install picamera paho-mqtt cython scipy numpy ws4py Pillow

RUN pip3 install --extra-index-url https://artifacts.luxonis.com/artifactory/luxonis-python-snapshot-local/ depthai

WORKDIR  /root 
RUN apt-get -y update && apt-get -y install \
    zip \
    unzip 

RUN wget -O opencv.zip https://github.com/opencv/opencv/archive/4.1.2.zip; \
    unzip opencv.zip; \
    rm opencv*.zip; \
    mv opencv-4.1.2 opencv

WORKDIR /root/opencv
RUN mkdir build
WORKDIR /root/opencv/build

RUN cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D ENABLE_NEON=ON \
    -D ENABLE_VFPV3=ON \
    -D BUILD_TESTS=OFF \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D CMAKE_SHARED_LINKER_FLAGS=-latomic \
    -D BUILD_EXAMPLES=OFF ..; \
    make -j4; \
    make install; \
    ldconfig

WORKDIR /root
RUN git clone --recursive https://github.com/apache/incubator-tvm tvm; \
    cd tvm; \
    mkdir build; \
    cp cmake/config.cmake build; \
    cd build; \
    cmake ..; \
    make runtime -j4; \
    echo 'export PYTHONPATH=$PYTHONPATH:/root/tvm/python' >> /root/.bashrc

RUN pip3 install scikit-image

WORKDIR /root
RUN apt-get clean; \
    apt-get -y autoremove; \
    rm -rf opencv; \
    rm -rf opencv_contrib
