document.addEventListener('DOMContentLoaded', function() {
    // Set the correct icons and text for sensor + program indicators
    const programIndicatorText = document.getElementById('programIndicatorText');
    const programIndicator = document.getElementById('programIndicator');
    fetch('/simple/check_active_settings')
        .then(response => response.json())
        .then(data => {
            if (data.active) {
                programIndicatorText.innerHTML = 'Izvajanje programa: <b>' + data.settingName + '</b>';
                programIndicator.src = "/static/images/check.png";
            }
            else {
                programIndicatorText.innerHTML = 'Izvajanje programa';
                programIndicator.src = "/static/images/x.png";
            }
        })
        .catch(error => console.error('Error fetching settings:', error));
})