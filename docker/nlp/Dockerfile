FROM python:3.7-slim

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get -y update && apt-get -y upgrade
RUN apt-get -y update && apt-get -y install \
    build-essential \
    wget \
    openssh-client \
    graphviz-dev \
    pkg-config \
    git-core \
    openssl \
    libssl-dev \
    libffi6 \
    libffi-dev \
    libpng-dev \
    libatlas3-base \
    libgfortran5 \
    libfreetype6 \
    libgomp1 \
    libatomic1 \
    python3-venv \
    python3-dev \
    libeigen3-dev \
    cmake

WORKDIR /root
RUN mkdir -p .config/pip; \
    echo "[global]" >> .config/pip/pip.conf; \
    echo "index-url=https://pypi.org/simple" >> .config/pip/pip.conf; \
    echo "extra-index-url=https://www.piwheels.org/simple" >> .config/pip/pip.conf

ENV VIRTUAL_ENV=/root/rasa_env
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py; \
    python get-pip.py

WORKDIR /root
RUN wget https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py; \
    python get-poetry.py --version 1.0.8

RUN pip install keras_applications==1.0.8 --no-deps; \
    pip install keras_preprocessing==1.1.0 --no-deps; \
    pip install cython; \
    pip install h5py==2.10.0 pybind11 six mock "jsonschema>=3.2,<3.3" pycparser protobuf==3.12.2 scikit-build wheel==0.34.2

WORKDIR /root
RUN wget https://github.com/Qengineering/TensorFlow-Raspberry-Pi/raw/master/tensorflow-2.1.0-cp37-cp37m-linux_armv7l.whl; \
    wget https://github.com/koenvervloesem/tensorflow-addons-on-arm/releases/download/v0.7.1/tensorflow_addons-0.7.1-cp37-cp37m-linux_armv7l.whl; \
    pip install tensorflow-2.1.0-cp37-cp37m-linux_armv7l.whl; \
    pip install tensorflow_addons-0.7.1-cp37-cp37m-linux_armv7l.whl; \
    rm tensorflow-2.1.0-cp37-cp37m-linux_armv7l.whl; \
    rm tensorflow_addons-0.7.1-cp37-cp37m-linux_armv7l.whl

WORKDIR /root
RUN git clone https://github.com/RasaHQ/rasa.git; \
    cd rasa; \
    git checkout tags/1.10.18; \
	sed -i 's/tensorflow = "~2.1"/tensorflow = "2.1.0"/g' pyproject.toml; \
    sed -i 's/version = "2.1.1"/version = "2.1.0"/g' poetry.lock

WORKDIR /root
RUN apt install cmake -y; \
    git clone --recursive https://github.com/googleapis/python-crc32c; \
    cd python-crc32c; \
    mkdir google_crc32c/build; \
    cd google_crc32c/build; \
    cmake -DCRC32C_BUILD_TESTS=no -DCRC32C_BUILD_BENCHMARKS=no -DBUILD_SHARED_LIBS=yes ..; \
    make all install; \
    cd ../..;\
    python setup.py install; \
    pip install crc32c

WORKDIR /root/rasa
RUN sed -i 's/version = "0.1.0"/version = "1.0.0"/g' poetry.lock; \
    /bin/bash -c "source /root/.poetry/env && make install"; \
    pip install jieba paho-matt

WORKDIR /root
RUN apt-get clean; \
    apt-get -y autoremove; \
    rm -rf python-crc32c; \
    rm get-pip.py; \
    rm get-poetry.py
