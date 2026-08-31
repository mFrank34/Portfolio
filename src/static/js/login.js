document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const form = e.target;
    const formData = new URLSearchParams();
    formData.append('username', form.username.value);
    formData.append('password', form.password.value);

    const errorDiv = document.getElementById('error-message');
    errorDiv.style.display = 'none';

    try {
        const response = await fetch('/api/auth/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error('Incorrect username or password');
        }

        window.location.href = '/admin';
    } catch (err) {
        errorDiv.textContent = err.message;
        errorDiv.style.display = 'block';
    }
});