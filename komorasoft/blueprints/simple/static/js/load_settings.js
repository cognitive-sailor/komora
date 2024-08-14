// Function to fetch settings and populate the dropdown menu
function loadSettings() {
    fetch('get_settings')
        .then(response => response.json())
        .then(data => {
            const dropdownMenu = document.getElementById('ddSettings');
            dropdownMenu.innerHTML = '';  // Clear existing options

            data.forEach(setting => {
                const li = document.createElement('li');
                li.className = 'dropdown-item'; // Optional: Bootstrap class for styling

                const btn = document.createElement('button');
                btn.className = 'btn btn-primary'; // Optional: Bootstrap button styling
                btn.textContent = setting.name;
                btn.title = setting.description; // Tooltip with description
                btn.setAttribute('data-setting-id', setting.id); // Store the ID in the button

                // Append button to li
                li.appendChild(btn);

                // Append li to the dropdown menu
                dropdownMenu.appendChild(li);
            });
        })
        .catch(error => console.error('Error fetching settings:', error));
}

// Execute loadSettings on page load
window.onload = loadSettings;

// Add event listener to a button
document.getElementById('refreshButton').addEventListener('click', loadSettings);

