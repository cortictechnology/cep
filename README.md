# Cortic Edge Computing Platform (CEP) 

CEP is a rapid prototyping platform for users who want to use A.I. in their projects. CEP runs on the popular Raspberry Pi 4B single-board computer and has build-in support for the [Luxonis OAK-D camera](https://shop.luxonis.com/products/1098obcenclosure).  It consists of a frontend called CAIT (Cortic A.I. Toolkit) and a backend called CURT (Cortic Universal Runtime). 

CAIT is based on Google's Blockly project. We extended it to provide a variety of custom A.I. and automation blocks. They allow users to create their own A.I. and robotics projects in a visual programming environment. All of these blocks are backed by a simple Python API that interfaces with the CURT backend. You may choose to program directly using this API for added flexibility and power. Advanced users can study the implementation of this Python API to understand how it interfaces with the CURT backend.

CURT is middleware that enables users to create distributed A.I. applications with minimal effort and minimal computational overhead. It offers a simple command-based programming interface to perform distributed computing tasks. CURT has five built-in modules:
1. Computer vision (all vision-related tasks including the DepthAI Gen2 pipeline)
2. Voice (speech recognition and speech generation)
3. NLP (users can build their own chatbots using the natural language processing tools in here)
4. Robotic control (motor and sensor controls, including the PID component)
5. Smart home (programmatically interfaces with HomeAssistant to send commands to smart home devices)

Each module provides a set of workers that can perform different tasks. We have provided various examples of how to use CURT's command-based programming interface. Users can also extend or implement new workers for these modules. We have provided an example of implementing an American Sign Language (ASL) recognition worker for the computer vision module.

## Hardware

Below is a list of hardware components that are required for each module. 

* All modules: 
  * Any of Raspberry Pi 4B 2GB/4Gb/8GB models
  * Micro SD card (32GB recommended)
* Computer vision module:
  * OAK-D camera
* Voice module:
  * ReSpeaker 4-Mic Array for Raspberry Pi
  * Mini speaker with 3.5mm audio jack
* Robotic control module:
  * LEGO Mindstorms Robot Inventor
  * LEGO Spike Prime
* Smart home module:
  * Smart home devices such as Philips Hue, smart speakers, etc


## Install

Before you start, make sure there is at least 32GB of free space on your SD card.  

```
$ git clone https://github.com/cortictechnology/cep
$ cd cep
$ bash setup.sh
```
The Raspberry Pi 4 will reboot at the end of the setup script.

## Usage

### CAIT 

1. Make sure your Raspberry Pi 4 is connected to the local WiFi.
2. On any computer that is connected to the same local WiFi, go to ```http://<raspberry_pi_hostname>.local/setup``` on your browser and follow the instruction to complete the setup process. 
3. After the setup is finished, you can access CAIT at ```http://<raspberry_pi_hostname>.local```. The default username and password for the login page is:
```
username: pi
password: cortic
```

### CURT

Please refer to the examples provided in the ``examples`` folder.

## How to contribute

We welcome contributions from all our users.  You can contribute by requesting features or reporting bugs under "Issues".  You can also submit proposed code updates through pull requests to our "dev" branch.


## Notes

This is a work in progress. We will update this project constantly to provide more documentation, examples and improvements.
