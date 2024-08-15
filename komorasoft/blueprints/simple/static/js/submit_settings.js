document.getElementById('submitSettingsButton').addEventListener('click', function() {
    // Check for any active settings
    fetch('check_active_settings')
        .then(response => response.json())
        .then(data => {
            if (data.active) {
                console.log("There are active settings.");
                alert("Nastavitev ${data.settingName} je aktivna! Potrebno je zaustaviti izvajanje te aktivnosti, če želite naložiti novo.")
            } else {
                console.log("No active settings found.");
                // No setting is active, submit the selected setting to the Execute panel
                const settingsID = document.getElementById('settingsID');
                if (settingsID.value === ''){
                    alert("Nobena nastavitev ni izbrana!")
                }
                else {
                    const settingsTitle = document.getElementById('settingsTitle');
                    const submittedSetting = document.getElementById('submittedSetting');
                    const submittedSettingID = document.getElementById('submittedSettingID');
                    submittedSetting.textContent = settingsTitle.value;
                }
            }
        })
        .catch(error => console.error('Error checking active settings:', error));
});





document.getElementById('playStopButton').addEventListener('click', function() {
    const playStopIcon = document.getElementById('playStopIcon');

    if (playStopIcon.getAttribute('src') === "static/images/play-button.png") {
        playStopIcon.setAttribute('src', "static/images/stop-button-rounded.png");
        playStopIcon.setAttribute('alt', 'Stop Icon');
    } else {
        playStopIcon.setAttribute('src', "static/images/play-button.png");
        playStopIcon.setAttribute('alt', 'Play Icon');
    }
});
