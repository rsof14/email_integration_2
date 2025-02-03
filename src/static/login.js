async function login() {
    const email = document.getElementById("login").value;
    const password = document.getElementById("password").value;

    const response = await fetch("/api/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
    });

    if (response.ok) {
        const data = await response.json();
        console.log(data.access_token);
        localStorage.setItem("jwt", data.access_token); // Сохраняем токен в localStorage
        fetch("/api/email", {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${data.access_token}`,
        },
    })
    } else {
        alert("Login failed!");
    }
}