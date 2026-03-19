const navLinks = document.getElementById("nav-links");
const menuBtn = document.getElementById("menu-btn");

if (menuBtn) {
  const menuBtnIcon = menuBtn.querySelector("i");

  menuBtn.addEventListener("click", () => {
    navLinks.classList.toggle("open");
    const isOpen = navLinks.classList.contains("open");
    menuBtnIcon.setAttribute("class", isOpen ? "ri-close-line" : "ri-menu-3-line");
  });

  navLinks.addEventListener("click", () => {
    navLinks.classList.remove("open");
    menuBtnIcon.setAttribute("class", "ri-menu-3-line");
  });
}

// ScrollReveal animations
const scrollRevealOption = {
  distance: "40px",
  origin: "bottom",
  duration: 900,
  easing: "ease-out",
};

if (typeof ScrollReveal !== "undefined") {
  ScrollReveal().reveal(".header__content h1", {
    ...scrollRevealOption,
  });

  ScrollReveal().reveal(".header__content .section__description", {
    ...scrollRevealOption,
    delay: 200,
  });

  ScrollReveal().reveal(".header__meta", {
    ...scrollRevealOption,
    delay: 300,
  });

  ScrollReveal().reveal(".header__btn", {
    ...scrollRevealOption,
    delay: 400,
  });

  ScrollReveal().reveal(".header__image", {
    ...scrollRevealOption,
    origin: "right",
    delay: 250,
  });

  ScrollReveal().reveal(".about__image", {
    ...scrollRevealOption,
  });

  ScrollReveal().reveal(".about__content", {
    ...scrollRevealOption,
    delay: 250,
  });

  ScrollReveal().reveal(".experience__item", {
    ...scrollRevealOption,
    interval: 150,
  });

  ScrollReveal().reveal(".skills__card", {
    ...scrollRevealOption,
    interval: 120,
  });

  ScrollReveal().reveal(".education__item", {
    ...scrollRevealOption,
  });

  ScrollReveal().reveal(".contact__container .logo, .contact__details, .contact__socials", {
    ...scrollRevealOption,
    interval: 120,
  });
}
