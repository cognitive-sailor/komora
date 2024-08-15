// Get references to the elements
const rangeInput = document.getElementById('temperatureRange');
const tempValue = document.getElementById('tempValue');

// Set the initial value
tempValue.textContent = rangeInput.value + " ˚C";

// Function to update the display value
function updateTempValue() {
    tempValue.textContent = rangeInput.value + " ˚C";
}

// Add an event listener to the range input
rangeInput.addEventListener('input', updateTempValue);

// Enable popovers
const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))
