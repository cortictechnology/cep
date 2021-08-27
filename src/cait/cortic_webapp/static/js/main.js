/* 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2021
  
 */
var hostname = window.location.hostname;

(function ($) {
    "use strict";
    /*==================================================================
    [ Validate ]*/
    var input = $('.validate-input .input100');

    $('.login100-form-btn').on('click', function () {
        var check = true;
        for (var i = 0; i < input.length; i++) {
            if (validate(input[i]) == false) {
                showValidate(input[i]);
                check = false;
            }
        }
        return check;
    });


    $('.validate-form .input100').each(function () {
        $(this).focus(function () {
            hideValidate(this);
        });
    });

    function validate(input) {
        if ($(input).attr('type') == 'email' || $(input).attr('name') == 'email') {
            if ($(input).val().trim().match(/^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{1,5}|[0-9]{1,3})(\]?)$/) == null) {
                return false;
            }
        }
        else {
            if ($(input).val().trim() == '') {
                return false;
            }
        }
    }

    function showValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).addClass('alert-validate');
    }

    function hideValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).removeClass('alert-validate');
    }

})(jQuery);

var cait_system_up = false
var clientID = "cait_login_client_" + parseInt(Math.random() * 100);
var client = new Paho.Client(hostname, 8083, clientID);
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
    client.subscribe("cait/output/" + hostname.split(".")[0] + "/system_status");
}

// called when the client loses its connection
function onConnectionLost(resObj) {
    console.log("Lost connection to " + resObj.uri + "\nError code: " + resObj.errorCode + "\nError text: " + resObj.errorMessage);
    if (resObj.reconnect) {
        console.log("Automatic reconnect is currently active.");
    } else {
        alert("Lost connection to host.");
    }
}

// called when a message arrives
function onMessageArrived(message) {
    console.log(message.payloadString);
    if (message.payloadString == "CAIT UP") {
        if (!cait_system_up) {
            cait_system_up = true;
            login();
        }
    }
}

function login() {
    var username_ = document.getElementById("username").value;
    var password_ = document.getElementById("pass").value;

    if (username_.length > 0 && password_.length > 0) {
        $.post("/login", { username: username_, password: password_ })
            .done(function (data) {
                if (data['result'] == "") {
                    alert(localizedStrings.usernameNotExist[locale]);
                }
                else if (data['result'] == "Wrong password.\n") {
                    alert(localizedStrings.wrongPass[locale]);
                }
                else {
                    if (!cait_system_up) {
                        loader.style.display = "flex";
                        loader.style.zIndex = 1;
                    } else {
                        url = window.location.protocol + "//" + window.location.hostname + "/programming";
                        window.location.href = url;
                    }
                }
            });
    }
}
