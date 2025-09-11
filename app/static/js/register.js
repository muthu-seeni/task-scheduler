// JS specific to register page

document.addEventListener("DOMContentLoaded", () => {
  console.log("Register page JS loaded ✅");

  const registerForm = document.getElementById("registerForm");
  if (registerForm) {
    registerForm.addEventListener("submit", (e) => {
      console.log("Register form submitted");
      // let backend handle validation
    });
  }
});
