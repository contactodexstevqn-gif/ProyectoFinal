// index.js

// NAVBAR CON EFECTO AL HACER SCROLL
window.addEventListener("scroll", () => {
    const navbar = document.querySelector(".navbar");

    if (window.scrollY > 40) {
        navbar.classList.add("navbar-scroll");
    } else {
        navbar.classList.remove("navbar-scroll");
    }
});


// ANIMACIÓN DE APARICIÓN AL HACER SCROLL
const animatedElements = document.querySelectorAll(
    ".producto-card, .coleccion-card, .mini-card, .valor-item, .stats-box, .contacto-card"
);

const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {

        if (entry.isIntersecting) {
            entry.target.classList.add("show-animation");
        }

    });
}, {
    threshold: 0.15
});

animatedElements.forEach((element) => {
    observer.observe(element);
});


// EFECTO SUAVE EN BOTONES
const buttons = document.querySelectorAll(
    ".btn-principal, .btn-claro, .btn-cta, .btn-sistema"
);

buttons.forEach((button) => {

    button.addEventListener("mouseenter", () => {
        button.style.transform = "translateY(-3px) scale(1.02)";
    });

    button.addEventListener("mouseleave", () => {
        button.style.transform = "";
    });

});


// EFECTO PARALLAX HERO
window.addEventListener("scroll", () => {

    const scrolled = window.scrollY;

    const shapeOne = document.querySelector(".shape-one");
    const shapeTwo = document.querySelector(".shape-two");

    if (shapeOne) {
        shapeOne.style.transform =
            `translateY(${scrolled * 0.15}px)`;
    }

    if (shapeTwo) {
        shapeTwo.style.transform =
            `translateY(${scrolled * -0.12}px)`;
    }

});


// SCROLL SUAVE EN ENLACES INTERNOS
document.querySelectorAll('a[href^="#"]').forEach(anchor => {

    anchor.addEventListener("click", function (e) {

        e.preventDefault();

        const target = document.querySelector(this.getAttribute("href"));

        if (target) {
            target.scrollIntoView({
                behavior: "smooth"
            });
        }

    });

});