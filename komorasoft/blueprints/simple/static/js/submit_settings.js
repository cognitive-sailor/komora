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
                    const settingsID = document.getElementById('settingsID');
                    const submittedSetting = document.getElementById('submittedSetting');
                    const submittedSettingID = document.getElementById('submittedSettingID');
                    submittedSetting.textContent = settingsTitle.value; // forward the Title of the settings to the execution panel
                    submittedSettingID.value = settingsID.value; // forward the ID of the settings to the execution panel
                }
            }
        })
        .catch(error => console.error('Error checking active settings:', error));
});


function settingSTART() {
    const submittedSetting = document.getElementById('submittedSetting');
    const submittedSettingID = document.getElementById('submittedSettingID');
    const confirmStart_SettingID = document.getElementById('confirmStart_SettingID');
    const confirmStartMessage = document.getElementById('confirmStartMessage');

    confirmStart_SettingID.value = submittedSettingID.value; // send the settings' ID to the modal for confirmation
    confirmStartMessage.innerHTML = "Ste prepričani, da želite zagnati program po izbranih nastavitvah: "+submittedSetting.innerText+"?";
}