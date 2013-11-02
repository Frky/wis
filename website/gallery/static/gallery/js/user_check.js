!function($) {

    // Constructor of an XMLHttpRequest object
    var getXMLHttpRequest = function() {
        var xhr = null;
         
        if (window.XMLHttpRequest || window.ActiveXObject) {
            if (window.ActiveXObject) {
                try {
                    xhr = new ActiveXObject("Msxml2.XMLHTTP");
                } catch(e) {
                    xhr = new ActiveXObject("Microsoft.XMLHTTP");
                }
            } else {
                xhr = new XMLHttpRequest(); 
            }
        } else {
            // XMLHttpRequest not supported by the browser
            return null;
        }
         
        return xhr;
    }

    // AJAX method to check is username is available for registration 
    var checkAvailability = function(callback, div, field) {

        // Creation of an object
        var xhr = getXMLHttpRequest(); 

        // AJAX function on change    
        xhr.onreadystatechange = function() {
            if (xhr.readyState == 4 && (xhr.status == 200 || xhr.status == 0)) {
                // Callback for results
                callback(div, xhr.responseText);
            } else if (xhr.readyState < 4) {
                // The request is in treatment, displaying loader image
                document.getElementById("loader").style.display = "inline";
            }
        };
    
        var user = document.getElementById(field).value;
    
        // Initialisation
        xhr.open("GET", "checkUser/" + user, true);
        // Sending request
        xhr.send(null);
    }

    var userCheckCallback = function(field, data) {

        // Hidding loader
        document.getElementById("loader").style.display = "none";

        // If the server returns False, it means that the username is already used
        if (data === "False") {
            $("#" + field).removeClass("has-success");
            $("#" + field).addClass("has-error");
            $("#" + field + "> div.help-block").html("* Ce pseudo est déjà utilisé.");
        } else {
            $("#" + field).removeClass("has-error");
            $("#" + field).addClass("has-success");
            $("#" + field + "> div.help-block").html("Ce pseudo est disponible.");
        }
    }


    // Handler for username input
    $('#id_username').on('change', function () {
        $("#id_username").addClass("form-control");
        checkAvailability(userCheckCallback, "usernameField", "id_username");
    });

}(window.jQuery);
