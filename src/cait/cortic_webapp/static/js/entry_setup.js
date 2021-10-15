/* 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021
  
 */

var cait_system_up = false;
var stopStreaming = true;
var hostname = window.location.hostname
var clientID = "blockly_" + parseInt(Math.random() * 100);
var client = new Paho.Client(hostname, 8083, clientID);
var subscribed_to_programming_topics = false;

client.onConnectionLost = onConnectionLost;
client.onMessageArrived = onMessageArrived;

function MQTTconnect() {
  client.connect({
    onSuccess: onConnect,
    onFailure: onFailure,
    reconnect: true
  });
}

MQTTconnect();

function onFailure(message) {
  console.log("Failed Connecting, Retrying...");
  setTimeout(MQTTconnect, 500);
}

function onConnect() {
  // Once a connection has been made, make a subscription and send a message.
  console.log("Connected to cait");
  $.post("/getusername",
    {},
    function (data, status) {
      document.getElementById('loggedUser').innerHTML = localizedStrings.loggedInAs[locale] + data['username'];
      if (/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(hostname)) {
        client.subscribe("cait/output/device_info");
        subscribed_to_programming_topics = false;
      }
      else {
        client.subscribe("cait/output/" + hostname.split(".")[0] + "/displayFrame");
        console.log("Subscribed to: " + "cait/output/" + hostname.split(".")[0] + "/displayFrame");
        client.subscribe("cait/output/" + hostname.split(".")[0] + "/system_status");
        console.log("Subscribed to: " + "cait/output/" + hostname.split(".")[0] + "/system_status");
      }

    });
}

// called when the client loses its connection
function onConnectionLost(responseObject) {
  subscribed_to_programming_topics = false;
  if (responseObject.errorCode !== 0) {
    console.log("onConnectionLost:" + responseObject.errorMessage);
    client.connect({ onSuccess: onConnect });
  }
}

// called when a message arrives
function onMessageArrived(message) {
  //console.log("onMessageArrived:");
  if (message.payloadString == "CAIT UP") {
    if (!cait_system_up) {
      cait_system_up = true;
    }
  }
  else {
    if (message.topic == "cait/output/device_info") {
      var device_info = JSON.parse(message.payloadString);
      if (device_info['host_ip'] == hostname) {
        if (!subscribed_to_programming_topics) {
          client.subscribe("cait/output/" + device_info['hostname'] + "/displayFrame");
          console.log("Subscribed to: " + "cait/output/" + device_info['hostname'] + "/displayFrame");
          client.subscribe("cait/output/" + device_info['hostname'] + "/system_status");
          console.log("Subscribed to: " + "cait/output/" + device_info['hostname'] + "/system_status");
          subscribed_to_programming_topics = true;
        }
      }
    }
    else {
      if (stopStreaming) {
        document.getElementById("cameraImage").setAttribute("src", '/static/img/video_placeholder.png');
      }
      else {
        document.getElementById("cameraImage").setAttribute(
          'src', "data:image/png;base64," + message.payloadString
        );
      }
    }
  }
}

var scan_for_devices = true;

var cameras = [];
var speakers = [];
var microphones = []
var light_devices = [];
var media_players = [];
var voice_mode = ["on device"]
var cloud_accounts = [];
var nlp_models = [];
var virtual_processors = { "Vision": [], "STT": [], "TTS": [], "NLP": [] }
var control_hubs = [];
var added_hubs = [];
var spatial_face_dection = false;
var spatial_object_dection = false;

function initDevices(interpreter, scope) {
  var wrapper = function (device_type, callback) {
    $.post("/get_states",
      {
        'device_type': device_type
      },
      function (data, status) {
        callback(data['devices']);
      });
  };
  interpreter.setProperty(scope, 'get_devices',
    interpreter.createAsyncFunction(wrapper));
}

function cloudAccounts(interpreter, scope) {
  var wrapper = function (callback) {
    $.post("/get_cloud_accounts",
      {},
      function (data, status) {
        callback(data['accounts']);
      });
  };
  interpreter.setProperty(scope, 'get_cloud_accounts',
    interpreter.createAsyncFunction(wrapper));
}

var get_cloud_accounts_code = "get_cloud_accounts();";
var myInterpreter_cloud = new Interpreter(get_cloud_accounts_code, cloudAccounts);

function get_cloud_accounts() {
  var options = [];
  if (myInterpreter_cloud.run()) {
    setTimeout(get_cloud_accounts, 100);
  }
  if (myInterpreter_cloud.value != null) {
    cloud_accounts = myInterpreter_cloud.value;
    if (cloud_accounts.length >= 1) {
      if (voice_mode.length == 1) {
        voice_mode.push("online");
      }
    }
    else {
      if (voice_mode.length == 2) {
        voice_mode.pop();
      }
    }
  }
}

setInterval(function () {
  if (scan_for_devices) {
    myInterpreter_cloud = new Interpreter(get_cloud_accounts_code, cloudAccounts);
    get_cloud_accounts();
  }
}, 5000);

function NLPModels(interpreter, scope) {
  var wrapper = function (callback) {
    $.post("/get_nlp_models",
      {},
      function (data, status) {
        callback(data['models']);
      });
  };
  interpreter.setProperty(scope, 'get_nlp_models',
    interpreter.createAsyncFunction(wrapper));
}

var get_nlp_models_code = "get_nlp_models();";
var myInterpreter_nlp = new Interpreter(get_nlp_models_code, NLPModels);

function get_nlp_models() {
  var options = [];
  if (myInterpreter_nlp.run()) {
    setTimeout(get_nlp_models, 100);
  }
  if (myInterpreter_nlp.value != null) {
    nlp_models = myInterpreter_nlp.value;
  }
}

setInterval(function () {
  if (scan_for_devices) {
    myInterpreter_nlp = new Interpreter(get_nlp_models_code, NLPModels);
    get_nlp_models();
  }
}, 5000);

var get_light_device_code = "get_devices('light');";
var myInterpreter_light = new Interpreter(get_light_device_code, initDevices);

function get_light_devices() {
  var options = [];
  if (myInterpreter_light.run()) {
    setTimeout(get_light_devices, 100);
  }
  if (myInterpreter_light.value != null) {
    light_devices = myInterpreter_light.value;
  }
}

setInterval(function () {
  if (scan_for_devices) {
    myInterpreter_light = new Interpreter(get_light_device_code, initDevices);
    get_light_devices();
  }
}, 5000);

var get_media_player_code = "get_devices('media_player');";
var myInterpreter_mdeia = new Interpreter(get_media_player_code, initDevices);

function get_media_players() {
  var options = [];
  if (myInterpreter_mdeia.run()) {
    setTimeout(get_media_players, 100);
  }
  if (myInterpreter_mdeia.value != null) {
    media_players = myInterpreter_mdeia.value;
  }
}

setInterval(function () {
  if (scan_for_devices) {
    myInterpreter_mdeia = new Interpreter(get_media_player_code, initDevices);
    get_media_players();
  }
}, 5000);

function Cameras(interpreter, scope) {
  var wrapper = function (callback) {
    $.get("/getvideodev",
      function (data, status) {
        callback(data);
      });
  };
  interpreter.setProperty(scope, 'get_cameras',
    interpreter.createAsyncFunction(wrapper));
}

var get_cameras_code = "get_cameras();";
var myInterpreter_cameras = new Interpreter(get_cameras_code, Cameras);

function get_cameras() {
  var options = [];
  if (myInterpreter_cameras.run()) {
    setTimeout(get_cameras, 100);
  }
  if (myInterpreter_cameras.value != null) {
    cameras = [];
    for (var i = 0; i < myInterpreter_cameras.value.length; i++) {
      cameras.push(myInterpreter_cameras.value[i]);
    }
  }
}

setInterval(function () {
  if (scan_for_devices) {
    myInterpreter_cameras = new Interpreter(get_cameras_code, Cameras);
    get_cameras();
  }
}, 5000);

function Speakers(interpreter, scope) {
  var wrapper = function (callback) {
    $.get("/getaudiodev",
      function (data, status) {
        callback(data);
      });
  };
  interpreter.setProperty(scope, 'get_speakers',
    interpreter.createAsyncFunction(wrapper));
}

var get_speakers_code = "get_speakers();";
var myInterpreter_speakers = new Interpreter(get_speakers_code, Speakers);

function get_speakers() {
  var options = [];
  if (myInterpreter_speakers.run()) {
    setTimeout(get_speakers, 100);
  }
  if (myInterpreter_speakers.value != null) {
    speakers = [];
    for (var i = 0; i < myInterpreter_speakers.value.length; i++) {
      if (myInterpreter_speakers.value[i]['type'] == "Output") {
        speakers.push(myInterpreter_speakers.value[i]);
      }
    }
  }
}

setInterval(function () {
  if (scan_for_devices) {
    myInterpreter_speakers = new Interpreter(get_speakers_code, Speakers);
    get_speakers();
  }
}, 5000);

function Microphones(interpreter, scope) {
  var wrapper = function (callback) {
    $.get("/getaudiodev",
      function (data, status) {
        callback(data);
      });
  };
  interpreter.setProperty(scope, 'get_microphones',
    interpreter.createAsyncFunction(wrapper));
}

var get_microphones_code = "get_microphones();";
var myInterpreter_microphones = new Interpreter(get_microphones_code, Microphones);

function get_microphones() {
  var options = [];
  if (myInterpreter_microphones.run()) {
    setTimeout(get_microphones, 100);
  }
  if (myInterpreter_microphones.value != null) {
    microphones = [];
    for (var i = 0; i < myInterpreter_microphones.value.length; i++) {
      if (myInterpreter_microphones.value[i]['type'] == "Input") {
        microphones.push(myInterpreter_microphones.value[i]);
      }
    }
  }
}

setInterval(function () {
  if (scan_for_devices) {
    myInterpreter_microphones = new Interpreter(get_microphones_code, Microphones);
    get_microphones();
  }
}, 5000);

function ControlHubs(interpreter, scope) {
  var wrapper = function (callback) {
    $.post("/get_control_devices",
      {},
      function (data, status) {
        callback(data['control_devices']);
      });
  };
  interpreter.setProperty(scope, 'get_control_devices',
    interpreter.createAsyncFunction(wrapper));
}

var get_control_devices_code = "get_control_devices();";
var myInterpreter_control_devices = new Interpreter(get_control_devices_code, ControlHubs);

function get_control_devices() {
  var options = [];
  if (myInterpreter_control_devices.run()) {
    setTimeout(get_control_devices, 100);
  }
  if (myInterpreter_control_devices.value != null) {
    control_hubs = [];
    for (var i = 0; i < myInterpreter_control_devices.value.length; i++) {
      if (myInterpreter_control_devices.value[i]['device'] == "EV3") {
        control_hubs.push(myInterpreter_control_devices.value[i]['device'] + ": " + myInterpreter_control_devices.value[i]['ip_addr']);
      } else {
        control_hubs.push(myInterpreter_control_devices.value[i]['device'] + ": " + myInterpreter_control_devices.value[i]['mac_addr']);
      }
    }
  }
}

setInterval(function () {
  if (scan_for_devices) {
    myInterpreter_control_devices = new Interpreter(get_control_devices_code, ControlHubs);
    get_control_devices();
  }
}, 3000);


function update_added_hub_list() {
  var allBlocks = workspace.getAllBlocks();
  for (blk in allBlocks) {
    if (allBlocks[blk].type == "add_control_hub" && allBlocks[blk].isEnabled()) {
      var hub_name = allBlocks[blk].inputList[0].fieldRow[1].value_;
      var index = added_hubs.indexOf(hub_name);
      if (index == -1) {
        added_hubs.push(hub_name);
      }
    }
  }
}

setInterval(update_added_hub_list, 1000);

setTimeout(() => { load_workspace(true); }, 200);