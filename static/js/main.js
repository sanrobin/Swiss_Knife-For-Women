/**
 * Swiss Knife for Women - Main JavaScript
 * Handles common functionality across the application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Mobile navigation toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            menuToggle.classList.toggle('active');
        });
    }
    
    // Flash message close button functionality
    const closeButtons = document.querySelectorAll('.flash-message .close-button');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const flashMessage = this.parentElement;
            flashMessage.style.opacity = '0';
            setTimeout(() => {
                flashMessage.style.display = 'none';
            }, 300);
        });
    });
    
    // SOS button functionality
    const sosButton = document.getElementById('sos-button');
    if (sosButton) {
        let pressTimer;
        let isLongPress = false;
        
        sosButton.addEventListener('mousedown', function() {
            pressTimer = setTimeout(() => {
                isLongPress = true;
                triggerSOS();
            }, 2000); // Long press for 2 seconds
        });
        
        sosButton.addEventListener('mouseup', function() {
            clearTimeout(pressTimer);
            if (!isLongPress) {
                showSOSOptions();
            }
            isLongPress = false;
        });
        
        sosButton.addEventListener('mouseleave', function() {
            clearTimeout(pressTimer);
            isLongPress = false;
        });
        
        // Touch support
        sosButton.addEventListener('touchstart', function(e) {
            pressTimer = setTimeout(() => {
                isLongPress = true;
                triggerSOS();
            }, 2000);
            e.preventDefault();
        });
        
        sosButton.addEventListener('touchend', function() {
            clearTimeout(pressTimer);
            if (!isLongPress) {
                showSOSOptions();
            }
            isLongPress = false;
        });
    }
    
    // Dark mode toggle if present
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            const isDarkMode = document.body.classList.contains('dark-mode');
            localStorage.setItem('darkMode', isDarkMode);
        });
        
        // Check for saved dark mode preference
        const savedDarkMode = localStorage.getItem('darkMode');
        if (savedDarkMode === 'true') {
            document.body.classList.add('dark-mode');
        }
    }
});

// SOS Functions
function triggerSOS() {
    console.log('SOS Triggered!');
    // Show alert to user
    alert('SOS Alert has been triggered! Emergency contacts are being notified.');
    
    // In a real app, this would send an API request to the server
    fetch('/api/emergency/sos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            timestamp: new Date().toISOString(),
            location: getCurrentLocation()
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('SOS alert sent:', data);
    })
    .catch(error => {
        console.error('Error sending SOS alert:', error);
    });
}

function showSOSOptions() {
    console.log('SOS Options Shown');
    // In a real app, this would show a modal with emergency options
    // For now, we'll just redirect to the emergency page
    window.location.href = '/emergency';
}

function getCurrentLocation() {
    // This is a placeholder. In a real app, this would use the Geolocation API
    return {
        latitude: null,
        longitude: null,
        accuracy: null
    };
}