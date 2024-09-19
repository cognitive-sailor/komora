
var socket = io.connect('http://' + document.domain + ':' + location.port);
var socket3 = io.connect('http://' + document.domain + ':' + location.port);

socket.on('update_status', function(data) {
    const statusIcon = document.getElementById('programIndicator'); // icon in navbar
    const programIndicatorText = document.getElementById('programIndicatorText'); // text in navbar
    const submittedSetting = document.getElementById('submittedSetting'); // text in execution_panel
    const settingStartButton = document.getElementById('settingStartButton'); // set button to inactive

    const sensorsIndicator = document.getElementById("sensorsIndicator")
    if (data.active) {
        sensorsIndicator.src="/static/images/sensors-green.png"
        statusIcon.src = "/static/images/check.png";  // Replace with actual path to check icon
        programIndicatorText.innerHTML = 'Izvajanje programa: <b>' + data.active_name + '</b>';
        submittedSetting.innerHTML = data.active_name;
        settingStartButton.disabled = true;

        
    } else {
        sensorsIndicator.src="/static/images/sensors-black.png"
        statusIcon.src = "/static/images/x.png";  // Replace with actual path to X icon
        programIndicatorText.innerText = 'Izvajanje programa';
        settingStartButton.disabled = false;

    }
});

socket3.on('update_temp',function(data) {
    const tempIndicatorText = document.getElementById('tempIndicatorText');
    var temp = data.temp.toFixed(2);
    console.log(temp);
    tempIndicatorText.innerHTML = "T="+temp+"˚C";
});