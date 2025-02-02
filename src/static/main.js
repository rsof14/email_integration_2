const token = localStorage.getItem("jwt");
if (!token) {
    // Если токена нет, перенаправляем на страницу логина
    window.location.href = "/api/login";
} else {
    // Используем токен для запросов
    fetch("/api/", {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`,
        },
    })
}