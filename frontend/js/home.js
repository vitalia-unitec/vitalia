
const formulario = document.getElementById("formBusqueda");

formulario.addEventListener("submit", function(event) {
    event.preventDefault();

    const ubicacion = document.getElementById("ubicacion").value;
    const radio = document.getElementById("radio").value;

    if (!ubicacion.trim()) {
        alert("Por favor, ingresa tu ubicación.");
        return;
    }

    // Por ahora solo comprobamos los datos del formulario.
    // Después conectaremos la búsqueda con FastAPI.
    console.log("Ubicación:", ubicacion);
    console.log("Radio:", radio);
});

// Seleccionar y deseleccionar filtros visualmente
document.querySelectorAll(".filtro").forEach(function(boton) {
    boton.addEventListener("click", function() {
        boton.classList.toggle("active");
        boton.setAttribute(
            "aria-pressed",
            boton.classList.contains("active")
        );
    });
});
