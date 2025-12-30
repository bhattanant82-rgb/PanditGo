const socket = io('http://localhost:3000'); // Server URL change kar

let watchId = null;
let currentBookingId = 'BK123456'; // Real me booking ID le

// Pandit side - Start Journey
if (document.getElementById('startJourney')) {
    document.getElementById('startJourney').addEventListener('click', () => {
        if (navigator.geolocation) {
            watchId = navigator.geolocation.watchPosition(pos => {
                socket.emit('panditLocation', {
                    bookingId: currentBookingId,
                    lat: pos.coords.latitude,
                    lng: pos.coords.longitude
                });
            }, err => alert('GPS error'), { enableHighAccuracy: true });

            document.getElementById('reachedBtn').style.display = 'block';
            alert('GPS Tracking Started');
        }
    });
}

// Pandit side - Reached
if (document.getElementById('reachedBtn')) {
    document.getElementById('reachedBtn').addEventListener('click', () => {
        navigator.geolocation.clearWatch(watchId);
        document.getElementById('pinSection').style.display = 'block';
        alert('GPS Stopped - Enter PIN');
    });
}

// Pandit side - Verify PIN
if (document.getElementById('verifyPin')) {
    document.getElementById('verifyPin').addEventListener('click', () => {
        const pin = document.getElementById('arrivalPin').value;
        socket.emit('verifyPin', { bookingId: currentBookingId, pin });
    });
}

// Customer side - Map + Location Update
if (document.getElementById('liveMap')) {
    const map = L.map('liveMap').setView([23.0225, 72.5714], 13); // Default Ahmedabad
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

    let panditMarker = L.marker([23.0225, 72.5714]).addTo(map).bindPopup('Pandit');

    socket.on('panditLocationUpdate', data => {
        panditMarker.setLatLng([data.lat, data.lng]);
        map.panTo([data.lat, data.lng]);
    });

    socket.on('pinVerified', () => {
        alert('Pandit Arrived & PIN Verified! Puja can start');
    });
}