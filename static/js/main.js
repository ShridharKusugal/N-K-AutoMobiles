// Main JS for NK Automobiles

document.addEventListener('DOMContentLoaded', function () {
    const currentPath = window.location.pathname;

    // Handle Navbar Navigation Arrow behavior
    const backBtn = document.querySelector('.nav-arrow-btn-back');
    if (backBtn) {
        backBtn.addEventListener('click', function (e) {
            window.history.back();
        });
    }

    const forwardBtn = document.querySelector('.nav-arrow-btn-forward');
    if (forwardBtn) {
        forwardBtn.addEventListener('click', function (e) {
            window.history.forward();
        });
    }

    /**
     * LOGIN PAGE PROTECTION (The "Hard Stop")
     * When the user is on the login page, we prevent the "Back" button from re-entering 
     * previous authenticated pages. This ensures that reaching the login page 
     * is the end of the history line for that session.
     */
    if (currentPath.includes('/login')) {
        // Hide navigation arrows on the login page for a cleaner "hard stop"
        const navArrows = document.querySelectorAll('.nav-arrow-btn');
        navArrows.forEach(btn => btn.style.display = 'none');

        // Push a new state so the back button is trapped on the login page
        window.history.pushState(null, "", window.location.href);
        window.onpopstate = function () {
            window.history.pushState(null, "", window.location.href);
        };
    }
});
