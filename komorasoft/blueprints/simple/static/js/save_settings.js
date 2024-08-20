document.getElementById('saveSettingsButton').addEventListener('click', function() {
    const formData = {};

    // Check if settingsTitle exists
    const settingsTitle = document.getElementById('settingsTitle');
    if (settingsTitle.value.trim() === '') {
        alert("Vpiši ime pod katerim boš shranil nove nastavitve, ali pa izberi obstoječe nastavitve iz menija.");
        return;
    } else {
        // Select all input elements inside the #simple-col1 div
        const inputElements = document.querySelectorAll('#simple-col1 input');
        // Select all select elements inside the #simple-col1 div
        const selectElements = document.querySelectorAll('#simple-col1 select');

        // Object to store durations and intervals for each actuator
        const actuators = {};

        // Loop through input elements and add them to formData
        inputElements.forEach(element => {
            if (element.id === 'advancedCheck') {
                addToFormData(element.id, element.checked);
            } else {
                addToFormData(element.id, element.value);
            }
        });

        // Loop through select elements and add their selected values to formData
        selectElements.forEach(element => {
            addToFormData(element.id, element.value);

            const category = extractCategory(element.id);
            if (!actuators[category]) {
                actuators[category] = {
                    duration: 0,
                    interval: 0,
                };
            }

            // Calculate time in seconds for each component
            const valueInSeconds = (id, value) => {
                if (id.includes('DurHours') || id.includes('IntHours')) {
                    return value * 3600;
                } else if (id.includes('DurMinutes') || id.includes('IntMinutes')) {
                    return value * 60;
                } else if (id.includes('DurSeconds') || id.includes('IntSeconds')) {
                    return value * 1;
                } else if (id.includes('IntDays')) {
                    return value * 86400;
                }
                return 0;
            };

            // Add the duration or interval times
            if (element.id.includes('Dur')) {
                actuators[category].duration += valueInSeconds(element.id, parseInt(element.value));
            } else if (element.id.includes('Int')) {
                actuators[category].interval += valueInSeconds(element.id, parseInt(element.value));
            }
        });

        // Check if any duration is longer than the interval
        for (const category in actuators) {
            const { duration, interval } = actuators[category];
            if (duration > interval) {
                alert(`Aktuator ${category} je vklopljen dalj časa, kot je nastavljen interval proženja. Prosim, popravi nastavitve.`);
                return;
            }
        }

        // If all checks pass, send formData to the server using fetch
        fetch('save_settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            alert("Nastavitve uspešno shranjene!");
        })
        .then(() => {
            location.reload();  // Reload the page
            })
        .catch(error => console.error('Error:', error));
    }

    // Helper function to extract the category from element.id
    function extractCategory(id) {
        // Match the part of the id before "Dur" or "Int"
        const match = id.match(/(.*?)(Dur|Int)/);
        return match ? match[1] : id;
    }

    // Helper function to add data to the formData object
    function addToFormData(id, value) {
        const category = extractCategory(id);

        if (!formData[category]) {
            formData[category] = {};  // Create a new category object if it doesn't exist
        }

        // Use the full id as the key within the category
        formData[category][id] = value;
    }
});

function deleteSettings() {
    const settingsTitle = document.getElementById('settingsTitle');
    const deleteSettingsModal = document.getElementById('deleteSettingsModal');
    if (settingsTitle.value.trim() === '') {
        alert("Ni izbrane nastavitve za izbris!");
        window.location.reload();
        return;}
};
