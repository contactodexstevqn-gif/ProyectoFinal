const togglePassword = document.getElementById("togglePassword");
const passwordInput = document.getElementById("password");

if (togglePassword && passwordInput) {
    togglePassword.addEventListener("click", () => {
        const isPassword = passwordInput.type === "password";

        passwordInput.type = isPassword ? "text" : "password";

        togglePassword.innerHTML = isPassword
            ? "<i class='bx bx-hide'></i>"
            : "<i class='bx bx-show'></i>";
    });
}