
document.addEventListener("DOMContentLoaded", () => {

    const paginaActual =
        window.location.pathname.split("/").pop() || "index.html";

    const enlaces = document.querySelectorAll(
        ".menu-vitalia .menu-enlace"
    );

    enlaces.forEach((enlace) => {

        const paginaEnlace =
            new URL(enlace.href).pathname.split("/").pop();

        if (paginaActual === paginaEnlace) {
            enlace.classList.add("active");
            enlace.setAttribute("aria-current", "page");
        }

    });

});
