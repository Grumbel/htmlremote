"use strict";
var g_volume_value = 50;
var g_volume_next_value = 50;
var g_volume_timeout = null;
function volume_set_instantly(value) {
    if (g_volume_value !== value) {
        g_volume_value = value;
        g_volume_next_value = value;
        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", "/service/volume", true);
        xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhttp.send("action=" + g_volume_value.toString() + "%");
    }
}
function volume_timeout() {
    volume_set_instantly(g_volume_next_value);
    g_volume_timeout = null;
}
function volume_set(value) {
    if (value < 0) {
        value = 0;
    }
    else if (value > 100) {
        value = 100;
    }
    g_volume_next_value = value;
    var volumeslider = document.getElementById("volumeslider");
    volumeslider.value = value.toString();
    if (g_volume_timeout == null) {
        volume_set_instantly(g_volume_next_value);
        g_volume_timeout = setTimeout(volume_timeout, 150);
    }
}
function volume_get() {
    return g_volume_next_value;
}
window.onload = function () {
    var volumeslider = document.getElementById("volumeslider");
    if (volumeslider) {
        volumeslider.addEventListener("input", function () {
            volume_set(parseInt(volumeslider.value));
        });
        volumeslider.addEventListener("change", function () {
            volume_set_instantly(parseInt(volumeslider.value));
        });
    }
    var volume_up_button = document.getElementById("volumeup");
    if (volume_up_button) {
        volume_up_button.addEventListener("click", function () {
            volume_set(volume_get() + 5);
        });
    }
    var volume_down_button = document.getElementById("volumedown");
    if (volume_down_button) {
        volume_down_button.addEventListener("click", function () {
            volume_set(volume_get() - 5);
        });
    }
};
