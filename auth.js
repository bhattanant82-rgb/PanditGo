// auth.js — Logged In Check for All Pages
window.addEventListener('load', function() {
    const authSection = document.getElementById('authSection');
    if (!authSection) return; // Agar page pe authSection nahi to skip

    if (localStorage.getItem('userLoggedIn') === 'true') {
        const name = localStorage.getItem('userName') || 'User';
        const phone = localStorage.getItem('userPhone') || '';
        authSection.innerHTML = `
            <div class="dropdown">
                <button class="btn btn-primary dropdown-toggle rounded-pill px-4 py-2 fw-bold" type="button" data-bs-toggle="dropdown">
                    ${name} (+91${phone})
                </button>
                <ul class="dropdown-menu dropdown-menu-end">
                    <li><a class="dropdown-item" href="my-dashboard.html">My Dashboard</a></li>
                    <li><a class="dropdown-item" href="my-bookings.html">My Bookings</a></li>
                    <li><hr class="dropdown-divider"></li>
                    <li><a class="dropdown-item text-danger" href="#" id="logoutBtn">Logout</a></li>
                </ul>
            </div>
        `;

        // Logout
        document.getElementById('logoutBtn').addEventListener('click', function(e) {
            e.preventDefault();
            localStorage.clear();
            alert('Logged Out!');
            location.reload();
        });
    }
});