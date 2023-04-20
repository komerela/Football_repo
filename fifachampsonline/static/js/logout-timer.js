$(document).ready(function() {
    // Set the countdown time in seconds (adjust as needed)
    var countdownTime = 60;

    // Set the refresh interval in milliseconds (adjust as needed)
    var refreshInterval = 1000;

    // Start the countdown timer
    var timer = setInterval(function() {
        countdownTime--;
        if (countdownTime > 0) {
            // Update the timer display
            $('#timer').text(' (' + countdownTime + ' seconds)');
        } else {
            // Redirect the user to the logout URL
            clearInterval(timer);
            window.location.href = '/logout/';
        }
    }, refreshInterval);
});

// This code uses jQuery to set up a timer that counts down from a specified 
// time (in this case, 60 seconds). When the timer reaches zero, the user will 
// be redirected to the logout URL (in this case, /logout/).