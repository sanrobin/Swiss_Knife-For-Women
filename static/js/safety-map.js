// Initialize map
let map;
let userMarker;
let userCircle;
let placeMarkers = [];
let userLocation = null;
let activeFilters = ['police']; // Default filter

// Initialize the map when the page loads
document.addEventListener('DOMContentLoaded', function() {
    initMap();
    setupEventListeners();
    checkActiveShares();
});

function initMap() {
    // Create map centered at a default location (will be updated with user's location)
    map = L.map('map').setView([0, 0], 2);
    
    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(map);
    
    // Try to get user's location
    getUserLocation();
}

function setupEventListeners() {
    // Locate me button
    document.getElementById('locate-me').addEventListener('click', function() {
        getUserLocation();
    });
    
    // Share location button
    document.getElementById('share-location').addEventListener('click', function() {
        document.querySelector('.location-sharing-panel').scrollIntoView({ behavior: 'smooth' });
    });
    
    // Place filters
    document.querySelectorAll('.place-filter').forEach(function(filter) {
        filter.addEventListener('click', function() {
            const type = this.dataset.type;
            
            // Toggle active state
            if (this.classList.contains('active')) {
                this.classList.remove('active');
                activeFilters = activeFilters.filter(f => f !== type);
            } else {
                this.classList.add('active');
                activeFilters.push(type);
            }
            
            // Update map with selected filters
            updatePlaces();
        });
    });
    
    // Generate share link button
    document.getElementById('generate-share-link').addEventListener('click', function() {
        generateShareLink();
    });
    
    // Copy link button
    document.getElementById('copy-link').addEventListener('click', function() {
        const linkInput = document.getElementById('share-link');
        linkInput.select();
        document.execCommand('copy');
        alert('Link copied to clipboard!');
    });
}

function getUserLocation() {
    if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(function(position) {
            userLocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude,
                accuracy: position.coords.accuracy
            };
            
            // Update map with user's location
            updateUserLocation();
            
            // Get nearby places
            updatePlaces();
            
            // Get safety recommendations
            getSafetyRecommendations();
            
            // Save location to server
            saveLocationToServer();
        }, function(error) {
            console.error('Error getting location:', error);
            alert('Could not get your location. Please check your device settings and try again.');
        }, {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 60000
        });
    } else {
        alert('Geolocation is not supported by your browser');
    }
}

function updateUserLocation() {
    // Remove existing user marker and accuracy circle
    if (userMarker) {
        map.removeLayer(userMarker);
    }
    if (userCircle) {
        map.removeLayer(userCircle);
    }
    
    // Create custom user marker
    const userIcon = L.divIcon({
        className: 'custom-marker user',
        html: '<span>You</span>',
        iconSize: [40, 40]
    });
    
    // Add user marker to map
    userMarker = L.marker([userLocation.lat, userLocation.lng], {
        icon: userIcon,
        zIndexOffset: 1000
    }).addTo(map);
    
    // Add accuracy circle
    userCircle = L.circle([userLocation.lat, userLocation.lng], {
        radius: userLocation.accuracy,
        color: '#4dabf7',
        fillColor: '#4dabf7',
        fillOpacity: 0.1
    }).addTo(map);
    
    // Center map on user's location
    map.setView([userLocation.lat, userLocation.lng], 15);
}

function updatePlaces() {
    // Remove existing place markers
    placeMarkers.forEach(function(marker) {
        map.removeLayer(marker);
    });
    placeMarkers = [];
    
    // If no user location, return
    if (!userLocation) {
        return;
    }
    
    // For each active filter, fetch and display places
    activeFilters.forEach(function(type) {
        fetchNearbyPlaces(type);
    });
}

function fetchNearbyPlaces(type) {
    // Fetch nearby places from server
    fetch(`/map/nearby-places?latitude=${userLocation.lat}&longitude=${userLocation.lng}&type=${type}`)
        .then(response => response.json())
        .then(data => {
            // Add places to map
            data.places.forEach(function(place) {
                addPlaceMarker(place);
            });
        })
        .catch(error => {
            console.error('Error fetching nearby places:', error);
        });
}

function addPlaceMarker(place) {
    // Create custom place marker
    const placeIcon = L.divIcon({
        className: `custom-marker ${place.type}`,
        html: `<span>${place.type.charAt(0).toUpperCase()}</span>`,
        iconSize: [30, 30]
    });
    
    // Add place marker to map
    const marker = L.marker([place.latitude, place.longitude], {
        icon: placeIcon
    }).addTo(map);
    
    // Add popup with place details
    marker.bindPopup(`
        <div class="place-popup">
            <h3>${place.name}</h3>
            <p><strong>Type:</strong> ${place.type.charAt(0).toUpperCase() + place.type.slice(1)}</p>
            ${place.address ? `<p><strong>Address:</strong> ${place.address}</p>` : ''}
            ${place.phone ? `<p><strong>Phone:</strong> ${place.phone}</p>` : ''}
            <div class="actions">
                <button onclick="getDirections(${place.latitude}, ${place.longitude})">Get Directions</button>
            </div>
        </div>
    `);
    
    // Add marker to array for later removal
    placeMarkers.push(marker);
}

function getDirections(lat, lng) {
    // Open directions in Google Maps
    window.open(`https://www.google.com/maps/dir/?api=1&origin=${userLocation.lat},${userLocation.lng}&destination=${lat},${lng}`, '_blank');
}

function getSafetyRecommendations() {
    // Fetch safety recommendations from server
    fetch(`/safety/recommendations?latitude=${userLocation.lat}&longitude=${userLocation.lng}`)
        .then(response => response.json())
        .then(data => {
            // Update recommendations container
            const container = document.getElementById('recommendations-container');
            
            if (data.recommendations && data.recommendations.length > 0) {
                let html = '';
                
                data.recommendations.forEach(function(rec) {
                    html += `
                        <div class="recommendation ${rec.severity}">
                            <p>${rec.message}</p>
                        </div>
                    `;
                });
                
                container.innerHTML = html;
            } else {
                container.innerHTML = '<p>No specific safety recommendations at this time.</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching safety recommendations:', error);
            document.getElementById('recommendations-container').innerHTML = 
                '<p>Could not load safety recommendations. Please try again later.</p>';
        });
}

function saveLocationToServer() {
    // Save user's location to server
    fetch('/map/save-location', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            latitude: userLocation.lat,
            longitude: userLocation.lng,
            accuracy: userLocation.accuracy
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Location saved:', data);
    })
    .catch(error => {
        console.error('Error saving location:', error);
    });
}

function generateShareLink() {
    // Get share duration
    const duration = document.getElementById('share-duration').value;
    
    // Generate share link
    fetch('/location/share', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            duration: parseInt(duration)
        })
    })
    .then(response => response.json())
    .then(data => {
        // Show share link
        document.getElementById('share-link').value = data.tracking_url;
        document.getElementById('share-link-output').style.display = 'block';
        
        // Update active shares
        checkActiveShares();
    })
    .catch(error => {
        console.error('Error generating share link:', error);
        alert('Could not generate share link. Please try again.');
    });
}

function checkActiveShares() {
    // Check for active location shares
    fetch('/location/active-sessions')
        .then(response => response.json())
        .then(data => {
            const activeSharesList = document.getElementById('active-shares-list');
            
            if (data.active_sessions && data.active_sessions.length > 0) {
                let html = '';
                
                data.active_sessions.forEach(function(session) {
                    const expiresAt = new Date(session.expires_at);
                    html += `
                        <li>
                            <div>
                                <strong>Expires:</strong> ${expiresAt.toLocaleString()}
                                <button onclick="stopSharing('${session.tracking_id}')" class="button small danger">Stop Sharing</button>
                            </div>
                        </li>
                    `;
                });
                
                activeSharesList.innerHTML = html;
                document.getElementById('active-shares').style.display = 'block';
            } else {
                document.getElementById('active-shares').style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error checking active shares:', error);
        });
}

function stopSharing(trackingId) {
    // Stop location sharing
    fetch(`/location/stop-sharing/${trackingId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        alert('Location sharing stopped');
        checkActiveShares();
    })
    .catch(error => {
        console.error('Error stopping location sharing:', error);
        alert('Could not stop location sharing. Please try again.');
    });
}

// Start watching user's location for real-time updates
let watchId;

function startLocationWatching() {
    if ('geolocation' in navigator) {
        watchId = navigator.geolocation.watchPosition(function(position) {
            userLocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude,
                accuracy: position.coords.accuracy
            };
            
            // Update user's location on map
            updateUserLocation();
            
            // Save location to server
            saveLocationToServer();
        }, function(error) {
            console.error('Error watching location:', error);
        }, {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 30000
        });
    }
}

// Start watching location after initial load
setTimeout(startLocationWatching, 5000);

// Handle device shake for SOS
let shakeThreshold = 15;
let lastX, lastY, lastZ;
let lastUpdate = 0;

window.addEventListener('devicemotion', function(event) {
    let current = Date.now();
    if ((current - lastUpdate) > 100) {
        let diffTime = current - lastUpdate;
        lastUpdate = current;
        
        let acceleration = event.accelerationIncludingGravity;
        let x = acceleration.x;
        let y = acceleration.y;
        let z = acceleration.z;
        
        let speed = Math.abs(x + y + z - lastX - lastY - lastZ) / diffTime * 10000;
        
        if (speed > shakeThreshold) {
            // Device was shaken, trigger SOS
            if (confirm('SOS Alert: Are you sure you want to send an emergency alert?')) {
                triggerSOS();
            }
        }
        
        lastX = x;
        lastY = y;
        lastZ = z;
    }
});

function triggerSOS() {
    // Trigger SOS alert
    fetch('/emergency/sos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            latitude: userLocation ? userLocation.lat : null,
            longitude: userLocation ? userLocation.lng : null
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(`Emergency alert sent to ${data.contacts_notified} contacts`);
    })
    .catch(error => {
        console.error('Error triggering SOS:', error);
        alert('Could not send emergency alert. Please try again or call emergency services directly.');
    });
}