function startTimer(minutes, formId) {
    let seconds = minutes * 60;
    const timerElement = document.getElementById("time");
    const quizForm = document.getElementById(formId);

    function updateTimer() {
        if (seconds < 0) return; // Prevent timer from going negative if submission is slow

        let min = Math.floor(seconds / 60);
        let sec = seconds % 60;
        
        // Add leading zero if seconds is less than 10
        timerElement.textContent = `${min}:${sec < 10 ? "0" + sec : sec}`;
        
        if (seconds === 0) {
            // Use a small delay to ensure the last second is displayed
            setTimeout(() => {
                if (quizForm) {
                    alert("Time's up! Submitting your answers.");
                    quizForm.submit();
                }
            }, 100);
        }
        seconds--;
    }

    updateTimer(); // Initial call to display timer immediately
    setInterval(updateTimer, 1000);
}