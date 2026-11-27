document.addEventListener("DOMContentLoaded", () => {

    const formulario = document.getElementById("formBuscarHome");
    const ubicacion = document.getElementById("ubicacionHome");

    if (formulario && ubicacion) {

        formulario.addEventListener("submit", () => {
            ubicacion.value = ubicacion.value.trim();
        });

    }

    document.querySelectorAll(".filtro").forEach((boton) => {

        boton.addEventListener("click", () => {

            boton.classList.toggle("active");

            boton.setAttribute(
                "aria-pressed",
                String(boton.classList.contains("active"))
            );

        });

    });

});