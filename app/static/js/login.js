// login.js — JS specific to the login page

document.addEventListener("DOMContentLoaded", () => {
    console.log("Login page JS loaded ✅");

    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", (e) => {
            console.log("Login form submitted");
            // Backend handles validation and security; no front-end blocking
        });
    }
});
