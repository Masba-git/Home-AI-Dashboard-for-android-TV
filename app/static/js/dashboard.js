// Global variables
let currentSessionId = 'tv_dashboard_' + Date.now();

// Initialize dashboard on load
document.addEventListener('DOMContentLoaded', function() {
    loadAllModules();
    updateDateTime();
    setInterval(updateDateTime, 1000);
    setInterval(refreshAllModules, 300000); // Refresh every 5 minutes
});

// Update date and time
function updateDateTime() {
    const now = new Date();
    const dateTimeStr = now.toLocaleString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    document.getElementById('datetime').textContent = dateTimeStr;
}

// Load all modules
async function loadAllModules() {
    await Promise.all([
        refreshWeather(),
        refreshNews(),
        refreshNetwork(),
        refreshTasks(),
        refreshYouTubeVideos(),
        refreshCalendarEvents(),
        refreshPrayerTimes(),
        refreshNotes(),
        refreshReminders(),
        refreshCCTV()
    ]);
}

function refreshAllModules() {
    console.log('Refreshing all modules...');
    loadAllModules();
}

// Weather Module
async function refreshWeather() {
    try {
        const response = await fetch('/api/weather/current?city=London');
        const weather = await response.json();
        
        const forecastResponse = await fetch('/api/weather/forecast?city=London');
        const forecast = await forecastResponse.json();
        
        let html = `
            <div class="weather-main">
                <h3>${weather.city}</h3>
                <div class="temperature">${Math.round(weather.temperature)}°C</div>
                <div>${weather.description}</div>
                <div class="weather-details">
                    <div>Feels like: ${Math.round(weather.feels_like)}°C</div>
                    <div>Humidity: ${weather.humidity}%</div>
                    <div>Wind: ${weather.wind_speed} m/s</div>
                    <div>Pressure: ${weather.pressure} hPa</div>
                </div>
            </div>
            <div class="weather-forecast">
                <h4>5-Day Forecast</h4>
        `;
        
        forecast.forEach(day => {
            html += `
                <div class="forecast-item">
                    <span>${day.day_name}</span>
                    <span>${Math.round(day.temp_min)}° / ${Math.round(day.temp_max)}°</span>
                    <span>${day.description}</span>
                </div>
            `;
        });
        
        html += `</div>`;
        document.getElementById('weather-content').innerHTML = html;
    } catch (error) {
        console.error('Weather error:', error);
        document.getElementById('weather-content').innerHTML = '<div class="loading">Error loading weather data</div>';
    }
}

// News Module
async function refreshNews() {
    try {
        const response = await fetch('/api/news/headlines?category=general&country=us');
        const data = await response.json();
        
        let html = '';
        data.articles.forEach(article => {
            html += `
                <div class="news-item" onclick="window.open('${article.url}', '_blank')">
                    <div class="news-title">${article.title}</div>
                    <div class="news-source">${article.source} - ${new Date(article.published_at).toLocaleDateString()}</div>
                    <div class="news-description">${article.description || ''}</div>
                </div>
            `;
        });
        
        document.getElementById('news-content').innerHTML = html || '<div class="loading">No news available</div>';
    } catch (error) {
        console.error('News error:', error);
        document.getElementById('news-content').innerHTML = '<div class="loading">Error loading news</div>';
    }
}

// Network Module
async function refreshNetwork() {
    try {
        const response = await fetch('/api/network/status');
        const data = await response.json();
        
        let html = `
            <div class="network-info">
                <p>Local IP: ${data.local_ip}</p>
                <p>Gateway: ${data.gateway}</p>
                <p>Total Devices: ${data.total_devices}</p>
            </div>
            <div class="devices-list">
                <h4>Connected Devices:</h4>
        `;
        
        data.devices.forEach(device => {
            html += `
                <div class="device-item">
                    <span class="device-status status-online"></span>
                    <strong>${device.hostname || device.ip}</strong>
                    <div class="device-ip">${device.ip}</div>
                    <div>Response: ${device.response_time}ms</div>
                </div>
            `;
        });
        
        html += `</div>`;
        document.getElementById('network-content').innerHTML = html;
    } catch (error) {
        console.error('Network error:', error);
        document.getElementById('network-content').innerHTML = '<div class="loading">Error scanning network</div>';
    }
}

// Tasks Module
async function refreshTasks() {
    try {
        const response = await fetch('/api/tasks/');
        const tasks = await response.json();
        
        let html = '';
        tasks.forEach(task => {
            html += `
                <div class="task-item ${task.completed ? 'task-completed' : ''}">
                    <div>
                        <div class="task-title">${task.title}</div>
                        ${task.description ? `<div class="task-desc">${task.description}</div>` : ''}
                        ${task.due_date ? `<div class="task-due">Due: ${new Date(task.due_date).toLocaleDateString()}</div>` : ''}
                    </div>
                    <div class="task-actions">
                        <button onclick="toggleTask(${task.id})">${task.completed ? '✓' : '○'}</button>
                        <button onclick="deleteTask(${task.id})">🗑️</button>
                    </div>
                </div>
            `;
        });
        
        document.getElementById('tasks-content').innerHTML = html || '<div class="loading">No tasks</div>';
    } catch (error) {
        console.error('Tasks error:', error);
        document.getElementById('tasks-content').innerHTML = '<div class="loading">Error loading tasks</div>';
    }
}

// Chatbot Module
async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addChatMessage(message, 'user');
    input.value = '';
    
    try {
        const response = await fetch('/api/chatbot/message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                message: message,
                session_id: currentSessionId 
            })
        });
        
        const data = await response.json();
        addChatMessage(data.response, 'assistant');
    } catch (error) {
        console.error('Chat error:', error);
        addChatMessage('Sorry, I encountered an error. Please try again.', 'assistant');
    }
}

function addChatMessage(text, role) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.textContent = text;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendChatMessage();
    }
}

// YouTube Module
async function refreshYouTubeVideos() {
    try {
        const response = await fetch('/api/youtube/videos');
        const videos = await response.json();
        
        let html = '';
        videos.forEach(video => {
            html += `
                <div class="video-item">
                    <div>
                        <div class="video-title">${video.title}</div>
                        <div class="video-status">${video.watched ? '✓ Watched' : '○ Unwatched'}</div>
                    </div>
                    <div class="video-actions">
                        <button onclick="playVideo('${video.url}')">▶ Play</button>
                        <button onclick="toggleVideoWatched(${video.id})">${video.watched ? 'Unmark' : 'Mark Watched'}</button>
                        <button onclick="deleteVideo(${video.id})">🗑️</button>
                    </div>
                </div>
            `;
        });
        
        document.getElementById('youtube-content').innerHTML = html || '<div class="loading">No videos in study list</div>';
    } catch (error) {
        console.error('YouTube error:', error);
        document.getElementById('youtube-content').innerHTML = '<div class="loading">Error loading videos</div>';
    }
}

// Calendar Module
async function refreshCalendarEvents() {
    try {
        const response = await fetch('/api/calendar/events');
        const events = await response.json();
        
        let html = '';
        events.forEach(event => {
            html += `
                <div class="event-item">
                    <div>
                        <div class="event-title">${event.title}</div>
                        <div class="event-date">${new Date(event.start_time).toLocaleString()}</div>
                        ${event.description ? `<div class="event-desc">${event.description}</div>` : ''}
                    </div>
                    <div class="event-actions">
                        <button onclick="deleteEvent(${event.id})">🗑️</button>
                    </div>
                </div>
            `;
        });
        
        document.getElementById('calendar-content').innerHTML = html || '<div class="loading">No upcoming events</div>';
    } catch (error) {
        console.error('Calendar error:', error);
        document.getElementById('calendar-content').innerHTML = '<div class="loading">Error loading calendar</div>';
    }
}

// Prayer Times Module
async function refreshPrayerTimes() {
    try {
        const response = await fetch('/api/prayer/times?city=London&country=UK');
        const prayers = await response.json();
        
        let html = `
            <div class="prayer-times-grid">
                <div class="prayer-item"><span class="prayer-name">Fajr</span><span class="prayer-time">${prayers.fajr}</span></div>
                <div class="prayer-item"><span class="prayer-name">Sunrise</span><span class="prayer-time">${prayers.sunrise}</span></div>
                <div class="prayer-item"><span class="prayer-name">Dhuhr</span><span class="prayer-time">${prayers.dhuhr}</span></div>
                <div class="prayer-item"><span class="prayer-name">Asr</span><span class="prayer-time">${prayers.asr}</span></div>
                <div class="prayer-item"><span class="prayer-name">Maghrib</span><span class="prayer-time">${prayers.maghrib}</span></div>
                <div class="prayer-item"><span class="prayer-name">Isha</span><span class="prayer-time">${prayers.isha}</span></div>
            </div>
            <div class="prayer-date">
                <div>${prayers.date}</div>
                <div>${prayers.hijri_date}</div>
            </div>
        `;
        
        document.getElementById('prayer-content').innerHTML = html;
    } catch (error) {
        console.error('Prayer times error:', error);
        document.getElementById('prayer-content').innerHTML = '<div class="loading">Error loading prayer times</div>';
    }
}

// Notes Module
async function refreshNotes() {
    try {
        const response = await fetch('/api/notes/');
        const notes = await response.json();
        
        let html = '';
        notes.forEach(note => {
            html += `
                <div class="note-item">
                    <div>
                        <div class="note-title">${note.title}</div>
                        <div class="note-preview">${note.content.substring(0, 100)}...</div>
                    </div>
                    <div class="note-actions">
                        <button onclick="editNote(${note.id})">✏️</button>
                        <button onclick="deleteNote(${note.id})">🗑️</button>
                    </div>
                </div>
            `;
        });
        
        document.getElementById('notes-content').innerHTML = html || '<div class="loading">No notes</div>';
    } catch (error) {
        console.error('Notes error:', error);
        document.getElementById('notes-content').innerHTML = '<div class="loading">Error loading notes</div>';
    }
}

// Reminders Module
async function refreshReminders() {
    try {
        const response = await fetch('/api/reminders/');
        const reminders = await response.json();
        
        let html = '';
        reminders.forEach(reminder => {
            html += `
                <div class="reminder-item ${reminder.completed ? 'task-completed' : ''}">
                    <div>
                        <div class="reminder-title">${reminder.title}</div>
                        <div class="reminder-desc">${reminder.description || ''}</div>
                        <div class="reminder-date">${reminder.date ? new Date(reminder.date).toLocaleString() : 'No date'}</div>
                        <div class="reminder-creator">By: ${reminder.created_by}</div>
                    </div>
                    <div class="reminder-actions">
                        <button onclick="completeReminder(${reminder.id})">✓</button>
                        <button onclick="deleteReminder(${reminder.id})">🗑️</button>
                    </div>
                </div>
            `;
        });
        
        document.getElementById('reminders-content').innerHTML = html || '<div class="loading">No reminders</div>';
    } catch (error) {
        console.error('Reminders error:', error);
        document.getElementById('reminders-content').innerHTML = '<div class="loading">Error loading reminders</div>';
    }
}

// CCTV Module
async function refreshCCTV() {
    try {
        const response = await fetch('/api/cctv/streams');
        const cameras = await response.json();
        
        let html = '';
        cameras.forEach(camera => {
            html += `
                <div class="camera-stream">
                    <h4>${camera.name}</h4>
                    <img src="/api/cctv/snapshot/${camera.id}" alt="${camera.name}" style="width:100%; border-radius:10px;">
                </div>
            `;
        });
        
        document.getElementById('cctv-content').innerHTML = html || '<div class="loading">No cameras configured</div>';
    } catch (error) {
        console.error('CCTV error:', error);
        document.getElementById('cctv-content').innerHTML = '<div class="loading">Error loading cameras</div>';
    }
}

// Modal functions
function showAddTaskModal() {
    document.getElementById('task-modal').style.display = 'block';
}

function showAddVideoModal() {
    document.getElementById('video-modal').style.display = 'block';
}

function showAddEventModal() {
    document.getElementById('event-modal').style.display = 'block';
}

function showAddNoteModal() {
    document.getElementById('note-modal').style.display = 'block';
}

function showAddReminderModal() {
    document.getElementById('reminder-modal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Task CRUD operations
async function saveTask() {
    const title = document.getElementById('task-title').value;
    const description = document.getElementById('task-description').value;
    const dueDate = document.getElementById('task-due-date').value;
    
    try {
        await fetch('/api/tasks/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description, due_date: dueDate })
        });
        
        closeModal('task-modal');
        refreshTasks();
        
        // Clear form
        document.getElementById('task-title').value = '';
        document.getElementById('task-description').value = '';
        document.getElementById('task-due-date').value = '';
    } catch (error) {
        console.error('Error saving task:', error);
    }
}

async function toggleTask(taskId) {
    try {
        await fetch(`/api/tasks/${taskId}/toggle`, { method: 'PATCH' });
        refreshTasks();
    } catch (error) {
        console.error('Error toggling task:', error);
    }
}

async function deleteTask(taskId) {
    if (confirm('Are you sure you want to delete this task?')) {
        try {
            await fetch(`/api/tasks/${taskId}`, { method: 'DELETE' });
            refreshTasks();
        } catch (error) {
            console.error('Error deleting task:', error);
        }
    }
}

// Video CRUD operations
async function saveVideo() {
    const title = document.getElementById('video-title').value;
    const url = document.getElementById('video-url').value;
    
    if (!url) {
        alert('Please enter a YouTube URL');
        return;
    }
    
    try {
        await fetch('/api/youtube/videos', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, url })
        });
        
        closeModal('video-modal');
        refreshYouTubeVideos();
        
        // Clear form
        document.getElementById('video-title').value = '';
        document.getElementById('video-url').value = '';
    } catch (error) {
        console.error('Error saving video:', error);
    }
}

function playVideo(url) {
    window.open(url, '_blank');
}

async function toggleVideoWatched(videoId) {
    try {
        const response = await fetch(`/api/youtube/videos/${videoId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ watched: true })
        });
        refreshYouTubeVideos();
    } catch (error) {
        console.error('Error updating video:', error);
    }
}

async function deleteVideo(videoId) {
    if (confirm('Are you sure you want to delete this video?')) {
        try {
            await fetch(`/api/youtube/videos/${videoId}`, { method: 'DELETE' });
            refreshYouTubeVideos();
        } catch (error) {
            console.error('Error deleting video:', error);
        }
    }
}

// Event CRUD operations
async function saveEvent() {
    const title = document.getElementById('event-title').value;
    const description = document.getElementById('event-description').value;
    const startTime = document.getElementById('event-start').value;
    const endTime = document.getElementById('event-end').value;
    const allDay = document.getElementById('event-all-day').checked;
    
    if (!title || !startTime) {
        alert('Please fill in required fields');
        return;
    }
    
    try {
        await fetch('/api/calendar/events', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description, start_time: startTime, end_time: endTime, all_day: allDay })
        });
        
        closeModal('event-modal');
        refreshCalendarEvents();
        
        // Clear form
        document.getElementById('event-title').value = '';
        document.getElementById('event-description').value = '';
        document.getElementById('event-start').value = '';
        document.getElementById('event-end').value = '';
        document.getElementById('event-all-day').checked = false;
    } catch (error) {
        console.error('Error saving event:', error);
    }
}

async function deleteEvent(eventId) {
    if (confirm('Are you sure you want to delete this event?')) {
        try {
            await fetch(`/api/calendar/events/${eventId}`, { method: 'DELETE' });
            refreshCalendarEvents();
        } catch (error) {
            console.error('Error deleting event:', error);
        }
    }
}

// Note CRUD operations
async function saveNote() {
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    
    try {
        await fetch('/api/notes/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, content })
        });
        
        closeModal('note-modal');
        refreshNotes();
        
        // Clear form
        document.getElementById('note-title').value = '';
        document.getElementById('note-content').value = '';
    } catch (error) {
        console.error('Error saving note:', error);
    }
}

async function deleteNote(noteId) {
    if (confirm('Are you sure you want to delete this note?')) {
        try {
            await fetch(`/api/notes/${noteId}`, { method: 'DELETE' });
            refreshNotes();
        } catch (error) {
            console.error('Error deleting note:', error);
        }
    }
}

function editNote(noteId) {
    // Implement edit functionality
    alert('Edit functionality coming soon!');
}

// Reminder CRUD operations
async function saveReminder() {
    const title = document.getElementById('reminder-title').value;
    const description = document.getElementById('reminder-description').value;
    const date = document.getElementById('reminder-date').value;
    const createdBy = document.getElementById('reminder-created-by').value;
    
    try {
        await fetch('/api/reminders/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description, date, created_by: createdBy })
        });
        
        closeModal('reminder-modal');
        refreshReminders();
        
        // Clear form
        document.getElementById('reminder-title').value = '';
        document.getElementById('reminder-description').value = '';
        document.getElementById('reminder-date').value = '';
    } catch (error) {
        console.error('Error saving reminder:', error);
    }
}

async function completeReminder(reminderId) {
    try {
        await fetch(`/api/reminders/${reminderId}/complete`, { method: 'PATCH' });
        refreshReminders();
    } catch (error) {
        console.error('Error completing reminder:', error);
    }
}

async function deleteReminder(reminderId) {
    if (confirm('Are you sure you want to delete this reminder?')) {
        try {
            await fetch(`/api/reminders/${reminderId}`, { method: 'DELETE' });
            refreshReminders();
        } catch (error) {
            console.error('Error deleting reminder:', error);
        }
    }
}