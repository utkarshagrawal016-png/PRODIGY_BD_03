let token = "";

async function registerUser() {
    const res = await fetch('/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: regName.value,
            email: regEmail.value,
            password: regPassword.value
        })
    });

    const data = await res.json();
    message.innerText = data.message;
    if (data.success) {
        setTimeout(() => {
            window.location.href = '/login-page';
        }, 1000);
    }
}

async function loginUser() {
    const res = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            email: loginEmail.value,
            password: loginPassword.value
        })
    });

    const data = await res.json();
    console.log(data)
    if (data.token) {
        localStorage.setItem("token", data.token);

        const profileRes = await fetch('/profile', {
            headers: {
                Authorization: `Bearer ${data.token}`
            }
        });

        const profileData = await profileRes.json();

        if (profileData.user.role === "admin") {
            window.location.href = "/admin-dashboard";
        } else {
            window.location.href = "/dashboard";
        }
    } else {
        document.getElementById("message").innerText = data.message;
    }
}

async function getProfile() {
    const token = localStorage.getItem("token");

    if (!token) {
        alert("Please login first");
        window.location.href = "/login-page";
        return;
    }

    const res = await fetch('/profile', {
        headers: {
            Authorization: `Bearer ${token}`
        }
    });

    const data = await res.json();
    document.getElementById("output").innerText = JSON.stringify(data, null, 2);
}

async function adminOnly() {
    const token = localStorage.getItem("token");

    const res = await fetch('/admin-only', {
        headers: {
            Authorization: `Bearer ${token}`
        }
    });

    const data = await res.json();

    document.getElementById("message").innerText = data.message;
}

function logoutUser() {
    localStorage.removeItem("token");
    window.location.href = "/login-page";
}

async function loadProfile() {
    const token = localStorage.getItem("token");

    if (!token) {
        alert("Please login first");
        window.location.href = "/login-page";
        return;
    }

    const res = await fetch('/profile', {
        headers: {
            Authorization: `Bearer ${token}`
        }
    });

    const data = await res.json();

    if (data.success) {
        document.getElementById("profileName").innerText =
            data.user.name;

        document.getElementById("profileEmail").innerText =
            data.user.email;

        document.getElementById("profileRole").innerText =
            data.user.role;
    }
}