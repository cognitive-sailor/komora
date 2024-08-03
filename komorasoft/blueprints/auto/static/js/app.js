document.addEventListener('DOMContentLoaded', () => {
    loadSchedules();
    loadEvents(); 

    const heading = document.getElementById('eventsHeading');
    heading.textContent = `Dogodki aktuatorjev`;

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
                row.dataset.scheduleId = schedule.schedule_id; // Store schedule_id in data attribute
                row.dataset.scheduleName = schedule.name; // Store schedule name in data attribute
                row.innerHTML = `
                    <td>${schedule.name}</td>
                    <td>${schedule.description}</td>
                    <td>${schedule.start_time}</td>
                    <td>
                        <div class="btn-group" role="group">
                        <button type="button" class="btn btn-dark btn-icon" data-bs-toggle="modal" data-bs-target="#editScheduleModal" onclick="editSchedule('${schedule.schedule_id}')">
                            <i class="bi bi-pencil-fill"></i>
                        </button>
                        <button class="btn btn-danger btn-icon" data-bs-toggle="modal" data-bs-target="#removeScheduleModal" onclick="deleteSchedule('${schedule.schedule_id}')">
                            <i class="bi bi-trash3-fill"></i>
                        </button>
                        </div>
                    </td>
                `;
                row.addEventListener('click', () => handleRowClick(schedule.schedule_id,schedule.name,true)); // Add click event listener
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error loading schedules:', error));
}

function handleRowClick(scheduleId, scheduleName="", reset=true) {
    // Remove 'selected-row' class from previously selected row
    document.querySelectorAll('#schedulesTable tbody tr').forEach(row => row.classList.remove('selected-row'));

    // Add 'selected-row' class to the clicked row
    const selectedRow = document.querySelector(`#schedulesTable tbody tr[data-schedule-id="${scheduleId}"]`);
    if (selectedRow) {
        selectedRow.classList.add('selected-row');
    }
    // Set the scheduleId parameter to the hidden input in the form
    if (reset){
    const sID_input = document.querySelector('#createEventScheduleId');
    sID_input.value = scheduleId;}
    else{
        const sID_input = document.querySelector('#createEventScheduleId');
        sID_input.value = "";
    }

    if (scheduleName!=""){
    // Update the heading with the selected schedule name
    const heading = document.getElementById('eventsHeading');
    heading.innerHTML = `Dogodki aktuatorjev v: &nbsp;&nbsp;&nbsp;&nbsp;<b>${scheduleName}</b>`;}
    else{
        const heading = document.getElementById('eventsHeading');
        heading.textContent = `Dogodki aktuatorjev`;
    }

    // Fetch and display actuator events
    fetch(`get_actuator_events?schedule_id=${scheduleId}`, { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#eventsTable tbody');
            tableBody.innerHTML = '';
            data.forEach(event => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${event.actuator_name}</td>
                    <td>${event.state}</td>
                    <td>${event.offset}</td>
                    <td>${event.absolute_time}</td>
                    <td>
                        <button class="btn btn-warning btn-sm" onclick="editEvent('${event.id}')">Uredi</button>
                        <button class="btn btn-danger btn-sm" onclick="confirmDeleteEvent('${event.id}')">Odstrani</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error loading actuator events:', error));
}




function loadEvents() {
    fetch('get_events', { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#eventsTable tbody');
            tableBody.innerHTML = '';
            data.forEach(event => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${event.actuator_name}</td>
                    <td>${event.state}</td>
                    <td>${event.offset}</td>
                    <td>${event.offset}</td>
                    <td>
                        <button class="btn btn-warning btn-sm" onclick="editEvent('${event.id}')">Uredi</button>
                        <button class="btn btn-danger btn-sm" onclick="confirmDeleteEvent('${event.id}')">Odstrani</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error loading events:', error));
}

function addSchedule(event) {
    event.preventDefault();
    const name = document.getElementById('scheduleName').value;
    const description = document.getElementById('scheduleDescription').value;
    const startTime = document.getElementById('scheduleStartTime').value;

    fetch('add_schedule', {
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
    const scheduleId = document.getElementById('createEventScheduleId').value;

    fetch('add_event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ actuator_name: actuatorName, state, offset, schedule_id: scheduleId })
    })
    .then(response => response.json())
    .then(() => handleRowClick(scheduleId, false))  // Make sure `loadEvents` is properly implemented
    .catch(error => console.error('Error adding event:', error));
}

function editSchedule(scheduleId) {
        fetch(`get_schedule/${scheduleId}`, { method: 'GET' })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error:', data.error);
                    return;
                }
    
                // Populate the form with the existing data
                document.getElementById('editScheduleId').value = data.schedule_id;
                document.getElementById('editScheduleName').value = data.name;
                document.getElementById('editScheduleDescription').value = data.description;
                document.getElementById('editScheduleStartTime').value = data.start_time;  // datetime-local expects ISO format
            })
            .catch(error => console.error('Error fetching schedule data:', error));
    }


function confirmDeleteSchedule(scheduleId) {
    // Implement this function to show a confirmation modal for schedule deletion
    
}

function updateSchedule(event) {
    event.preventDefault();
    // Implement this function to handle the form submission for updating a schedule
}

function deleteSchedule(scheduleId) {
    // Implement this function to delete the selected schedule
    fetch(`get_schedule/${scheduleId}`, { method: 'GET' })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error:', data.error);
                    return;
                }
    
                // Populate the form with the existing data
                document.getElementById('removeScheduleId').value = scheduleId;
                document.getElementById('removeScheduleName').value = data.name;
                document.getElementById('removeScheduleDescription').value = data.description;
                document.getElementById('removeScheduleStartTime').value = data.start_time;  // datetime-local expects ISO format
                document.getElementById('scheduleDeleteMessage').textContent = `Ali ste prepričani, da želite odstraniti protokol ${data.name}?`;
            })
            .catch(error => console.error('Error fetching schedule data:', error));
}
