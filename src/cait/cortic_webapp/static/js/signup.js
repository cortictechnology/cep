/* 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, March 2020
  
 */

const button = document.querySelector('.btn-register')
const form   = document.querySelector('.form')

button.addEventListener('click', function() {
    var username_ = document.getElementById("username").value;
    var password_ = document.getElementById("pass").value;

    if (username_.length > 0 && password_.length > 0){
        $.post("/signup", { username: username_, password: password_ })
        .done(function( data ) {
            if(data['result'] != 0) {
                alert(localizedStrings.usernameExist[locale]);
            }
            else {
                alert(localizedStrings.registerSuccess[locale])
                window.location.href = "/";
            }
        });
    } else {
        alert(localizedStrings.usernameOrPassEmpty[locale])
    }
});
