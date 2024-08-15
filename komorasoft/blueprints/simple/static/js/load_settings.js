// // Function to fetch settings and populate the dropdown menu
// function loadSettings() {
//     fetch('get_settings')
//         .then(response => response.json())
//         .then(data => {
//             const dropdownMenu = document.getElementById('ddSettings');
//             dropdownMenu.innerHTML = '';  // Clear existing options

//             data.forEach(setting => {
//                 const li = document.createElement('li');
//                 li.className = 'dropdown-item'; // Optional: Bootstrap class for styling

//                 const link = document.createElement('a');
//                 // btn.className = 'btn btn-primary'; // Optional: Bootstrap button styling
//                 link.textContent = setting.name;
//                 link.title = setting.description; // Tooltip with description
//                 // link.id = setting.id
//                 link.setAttribute('data-setting-id', setting.id); // Store the ID in the button

//                 // Append button to li
//                 li.appendChild(link);

//                 // Append li to the dropdown menu
//                 dropdownMenu.appendChild(li);
//             });
//         })
//         .catch(error => console.error('Error fetching settings:', error));
// }

// // Execute loadSettings on page load
// window.onload = loadSettings;
// // Add event listener to a button
// document.getElementById('saveSettingsButton').addEventListener('click', loadSettings);


// Function to fetch and populate the dropdown menu with settings
function loadSettings() {
    fetch('get_settings')
        .then(response => response.json())
        .then(data => {
            const dropdownMenu = document.getElementById('ddSettings');
            dropdownMenu.innerHTML = '';  // Clear existing options

            data.forEach(setting => {
                const a = document.createElement('a');
                a.className = 'dropdown-item';  // Bootstrap class for dropdown items
                a.href = '#';  // Prevent default link behavior
                a.textContent = setting.name;
                a.setAttribute('data-setting-id', setting.id);  // Store setting ID in data attribute
                a.onclick = () => onSelectedSettings(setting.id);  // Attach click event

                // Append <a> to the dropdown menu
                dropdownMenu.appendChild(a);
            });
        })
        .catch(error => console.error('Error fetching settings:', error));
}

// Function to fetch the data for the selected setting and update fields on the webpage
function onSelectedSettings(settingId) {
    fetch(`get_setting/${settingId}`)
        .then(response => response.json())
        .then(data => {
            // Set what you can manually:
            const settingsID = document.getElementById('settingsID');
            const settingsTitle = document.getElementById('settingsTitle');
            const settingsDescription = document.getElementById('settingsDescription');
            const settingsDescriptionTooltip = document.getElementById('settingsDescriptionTooltip');
            const temperatureRange = document.getElementById('temperatureRange');
            const advancedCheck = document.getElementById('advancedCheck');
            const deleteTitle = document.getElementById('deleteTitle') // to display in settingsDeleteModal
            const deleteSettingId = document.getElementById('deleteSettingId') // to set the id of the setting for deletion

            settingsID.value = data['id']
            settingsTitle.value = data['settingsTitle'];
            settingsDescription.value = data['settingsDescription']
            settingsDescriptionTooltip.textContent = data['settingsDescription'];
            temperatureRange.value = data['temperature'];
            updateTempValue() // Update value in Temperatura: X°C
            deleteTitle.innerText = data['settingsTitle']
            deleteSettingId.value = settingId
            
            // Check if 'advanced' is true, and if so, simulate a click on the advancedCheck switch
            if (data['advanced'] === true && !advancedCheck.checked) {
                advancedCheck.click();
            } else if (data['advanced'] === false && advancedCheck.checked) {
                advancedCheck.click();
            }

            // Add event listener to advancedCheck to monitor changes
            advancedCheck.addEventListener('click', function() {
                if (!advancedCheck.checked) {
                    // When unchecked, set the specific element values to 0
                    setElementValuesToZero();
                }
            });

            // Prepare a dictionary for translating between HTML IDs and database entries
            const myDict = {
                'interval_days': 'IntDays',
                'interval_hours': 'IntHours',
                'interval_minutes': 'IntMinutes',
                'interval_seconds': 'IntSeconds',
                'duration_hours': 'DurHours',
                'duration_minutes': 'DurMinutes',
                'duration_seconds': 'DurSeconds'
            };

            // Iterate over the JSON data and populate the HTML elements
            Object.keys(data).forEach(category => {
                // Skip categories that are equal to "settingsTitle" or "settingsDescription"
                if (category === 'settingsTitle' || category === 'settingsDescription' || category === 'id') {
                    return;
                }
                console.log(category)
                const settings = data[category];

                // Iterate over each setting within the category
                Object.keys(settings).forEach(key => {
                    const value = settings[key];

                    const full_key = category + myDict[key];
                    console.log(full_key + " : " + value);

                    // Find the corresponding HTML element by ID
                    const element = document.getElementById(full_key);
                    if (element) {
                        element.value = value;  // Set the value for other input types
                    }
                });
            });
        })
        .catch(error => console.error('Error loading setting:', error));
}



// Execute loadSettings on page load
window.onload = loadSettings;

// Add event listener to a refresh button if needed
document.getElementById('saveSettingsButton').addEventListener('click', loadSettings);



// Function to set specific element values to 0
function setElementValuesToZero() {
    const elementsToReset = ['venUparIntDays','venUparIntHours','venUparIntMinutes','venUparIntSeconds','venUparDurHours','venUparDurMinutes','venUparDurSeconds','grelecIntDays','grelecIntHours','grelecIntMinutes','grelecIntSeconds','grelecDurHours','grelecDurMinutes','grelecDurSeconds','vlazIntDays','vlazIntHours','vlazIntMinutes','vlazIntSeconds','vlazDurHours','vlazDurMinutes','vlazDurSeconds']; // Replace with actual IDs of the elements you want to reset

    elementsToReset.forEach(elementId => {
        const element = document.getElementById(elementId);
        if (element) {
            element.value = 0;  // Set the value to 0
        }
    });
}
 
