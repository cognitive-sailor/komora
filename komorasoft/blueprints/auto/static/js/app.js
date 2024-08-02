document.addEventListener('DOMContentLoaded', () => {
    loadSchedules();
    // loadEvents(); // Uncomment when `loadEvents` function is implemented

    document.getElementById('newScheduleForm').addEventListener('submit', addSchedule);
    document.getElementById('newEventForm').addEventListener('submit', addEvent);

    document.getElementById('editScheduleForm').addEventListener('submit', updateSchedule);
    document.getElementById('confirmDeleteSchedule').addEventListener('click', deleteSchedule);
});

function loadSchedules() {
    fetch('get_schedules', { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#schedulesTable tbody');
            tableBody.innerHTML = '';
            data.forEach(schedule => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${schedule.name}</td>
                    <td>${schedule.description}</td>
                    <td>${schedule.start_time}</td>
                    <td>
                        <button class="btn btn-warning btn-sm" onclick="editSchedule('${schedule.schedule_id}')">Edit</button>
                        <button class="btn btn-danger btn-sm" onclick="confirmDeleteSchedule('${schedule.schedule_id}')">Delete</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error loading schedules:', error));
}

function addSchedule(event) {
    event.preventDefault();
    const name = document.getElementById('scheduleName').value;
    const description = document.getElementById('scheduleDescription').value;
    const startTime = document.getElementById('scheduleStartTime').value;

    fetch('/add_schedule', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description, start_time: startTime })
    })
    .then(response => response.json())
    .then(() => loadSchedules())
    .catch(error => console.error('Error adding schedule:', error));
}

function addEvent(event) {
    event.preventDefault();
    const actuatorName = document.getElementById('actuatorName').value;
    const state = document.getElementById('eventState').value === 'true';
    const offset = document.getElementById('eventOffset').value;
    const scheduleId = document.getElementById('eventScheduleId').value;

    fetch('/add_event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ actuator_name: actuatorName, state, offset, schedule_id: scheduleId })
    })
    .then(response => response.json())
    .then(() => loadEvents())  // Make sure `loadEvents` is properly implemented
    .catch(error => console.error('Error adding event:', error));
}

function editSchedule(scheduleId) {
    // Implement this function to show the modal with existing schedule data for editing
}

function confirmDeleteSchedule(scheduleId) {
    // Implement this function to show a confirmation modal for schedule deletion
}

function updateSchedule(event) {
    event.preventDefault();
    // Implement this function to handle the form submission for updating a schedule
}

function deleteSchedule() {
    // Implement this function to delete the selected schedule
}
