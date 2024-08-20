var socket2 = io.connect('http://'+document.domain+':'+location.port);

socket2.on('toggle_actuators', function(msg) {
    var act_data = msg.data;
    for (var key in act_data) {
        const element = document.getElementById("card_head_"+key);
        element.classList.remove("bg-on","bg-off"); // clear both stylings for ON and OFF
        if (act_data[key]) {
            element.classList.add("bg-on")
        } else {
            element.classList.add("bg-off")
        }
        
    }
});