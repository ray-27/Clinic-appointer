// Filter appointments based on selected criteria
async function filterAppointments() {
    const status = document.getElementById('status-filter').value;
    const date = document.getElementById('date-filter').value;
    const doctor = document.getElementById('doctor-filter').value;
    
    const params = new URLSearchParams();
    if (status !== 'all') params.append('status', status);
    if (date) params.append('date', date);
    if (doctor) params.append('doctor', doctor);
    
    try {
        const response = await fetch(`/appointments/filter?${params}`);
        const data = await response.json();
        
        if (response.ok) {
            updateAppointmentsTable(data.appointments);
            updateAppointmentCount(data.count);
        } else {
            console.error('Error filtering appointments:', data.error);
        }
    } catch (error) {
        console.error('Error filtering appointments:', error);
    }
}

// Update the appointments table with filtered data
function updateAppointmentsTable(appointments) {
    const tbody = document.querySelector('#appointments-table tbody');
    
    if (appointments.length === 0) {
        tbody.innerHTML = '<tr><td colspan="11" class="no-appointments">No appointments found</td></tr>';
        return;
    }
    
    tbody.innerHTML = appointments.map(appointment => `
        <tr class="appointment-row status-${appointment.status}">
            <td>${appointment.appointment_id}</td>
            <td class="patient-name">${appointment.patient_name}</td>
            <td>${appointment.patient_age}</td>
            <td class="doctor-name">${appointment.doctor_name}</td>
            <td class="specialty">${appointment.specialty}</td>
            <td class="appointment-date">${appointment.appointment_date}</td>
            <td class="appointment-time">${appointment.slot_timing}</td>
            <td>
                <span class="status-badge status-${appointment.status}">
                    ${appointment.status.charAt(0).toUpperCase() + appointment.status.slice(1)}
                </span>
            </td>
            <td class="symptoms">
                <div class="symptoms-text">
                    ${appointment.symptoms || 'Not specified'}
                </div>
            </td>
            <td class="booking-date">${appointment.booking_date}</td>
            <td class="actions">
                <a href="/appointments/${appointment.appointment_id}" class="view-btn">View</a>
            </td>
        </tr>
    `).join('');
}

// Update appointment count
function updateAppointmentCount(count) {
    const countElement = document.querySelector('.appointment-count');
    countElement.textContent = `Total: ${count} appointments`;
}

// Clear all filters
function clearFilters() {
    document.getElementById('status-filter').value = 'all';
    document.getElementById('date-filter').value = '';
    document.getElementById('doctor-filter').value = '';
    filterAppointments();
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners for real-time filtering
    document.getElementById('status-filter').addEventListener('change', filterAppointments);
    document.getElementById('date-filter').addEventListener('change', filterAppointments);
    document.getElementById('doctor-filter').addEventListener('input', debounce(filterAppointments, 300));
});

// Debounce function for search input
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
