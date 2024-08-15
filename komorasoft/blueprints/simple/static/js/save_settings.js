document.getElementById('saveSettingsButton').addEventListener('click', function() {
    const formData = {};

    // Check if settingsTitle exist
    const settingsTitle = document.getElementById('settingsTitle')
    if (settingsTitle.value.trim() === '') {
        alert("Vpiši ime pod katerim boš shranil nove nastavitve, ali pa izberi obstoječe nastavitve iz menija.")
    }
    else {
        // Select all input elements inside the #simple-col1 div
        const inputElements = document.querySelectorAll('#simple-col1 input');
        // Select all select elements inside the #simple-col1 div
        const selectElements = document.querySelectorAll('#simple-col1 select');

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
        });

        // Send formData to the server using fetch
        fetch('save_settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        }).then(response => response.json())
        .then(data => console.log(data))
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

    location.reload();
    alert("Nastavitve uspešno shranjene!");
});
