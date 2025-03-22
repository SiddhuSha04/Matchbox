// Handle registration form submission
document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('http://127.0.0.1:5000/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const result = await response.json();
        alert(result.message);

        // Redirect to a new page after successful registration
        if (response.ok) {
            window.location.href = 'welcome.html'; // Redirect to welcome.html
        }
    } catch (error) {
        console.error('Error during registration:', error);
        alert('An error occurred during registration.');
    }
});

// Handle login link click to toggle login form visibility
document.getElementById('loginLink').addEventListener('click', function(event) {
    event.preventDefault(); // Prevent the link from navigating
    const loginFormContainer = document.getElementById('loginFormContainer');
    if (loginFormContainer.style.display === 'none') {
        loginFormContainer.style.display = 'block';
    } else {
        loginFormContainer.style.display = 'none';
    }
});

// Handle login form submission
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const response = await fetch('http://127.0.0.1:5000/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const result = await response.json();
        alert(result.message);

        // Redirect to a new page after successful login
        if (response.ok) {
            window.location.href = 'dashboard.html'; // Redirect to dashboard.html
        }
    } catch (error) {
        console.error('Error during login:', error);
        alert('An error occurred during login.');
    }
});