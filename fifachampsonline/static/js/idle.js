(function() {
    var IDLE_TIMEOUT = 10; // in minutes
    var _idleSecondsCounter = 0;
    document.onclick = function() {
        _idleSecondsCounter = 0;
    };
    document.onmousemove = function() {
        _idleSecondsCounter = 0;
    };
    document.addEventListener('keypress', function(event) {
        console.log('Key pressed');
      });
    window.setInterval(checkIdleTime, 1000);
    function checkIdleTime() {
        _idleSecondsCounter++;
        var oPanel = document.getElementById("logout-reminder");
        if (oPanel) {
            oPanel.innerHTML = "You will be logged out in " + (IDLE_TIMEOUT - _idleSecondsCounter) + " seconds.";
        }
        if (_idleSecondsCounter >= IDLE_TIMEOUT * 60) {
            window.location.href = "/logout/";
        }
    }
})();


// This library tracks user activity and can be used to log the 
// user out automatically after a specified period of inactivity.