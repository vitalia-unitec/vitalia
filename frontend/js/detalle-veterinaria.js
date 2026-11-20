
/* =========================================
   VITALIA - DETALLE DE VETERINARIA
   Integración FastAPI + Leaflet
========================================= */

document.addEventListener("DOMContentLoaded", () => {

    const estadoDetalle = document.getElementById("estadoDetalle");
    const contenidoDetalle = document.getElementById("contenidoDetalle");

    const nombreVeterinaria = document.getElementById("nombreVeterinaria");
    const direccionVeterinaria = document.getElementById("direccionVeterinaria");
    const serviciosVeterinaria = document.getElementById("serviciosVeterinaria");
    const horariosVeterinaria = document.getElementById("horariosVeterinaria");
    const telefonoVeterinaria = document.getElementById("telefonoVeterinaria");
    const descripcionVeterinaria = document.getElementById("descripcionVeterinaria");

    const imagenVeterinaria = document.getElementById("imagenVeterinaria");
    const imagenPlaceholder = document.getElementById("imagenPlaceholder");

    const botonLlamar = document.getElementById("botonLlamar");
    const botonVerMapa = document.getElementById("botonVerMapa");
    const mensajeUbicacion = document.getElementById("mensajeUbicacion");

    const parametrosURL = new URLSearchParams(window.location.search);
    const idVeterinaria = parametrosURL.get("id");

    let mapaDetalleLeaflet = null;

    // =====================================
    // ESTADOS
    // =====================================

    function mostrarEstado(mensaje) {
        contenidoDetalle.hidden = true;
        estadoDetalle.hidden = false;
        estadoDetalle.textContent = mensaje;
    }

    function mostrarContenido() {
        estadoDetalle.hidden = true;
        contenidoDetalle.hidden = false;
    }

    // =====================================
    // DIRECCIÓN
    // =====================================

    function obtenerDireccion(direccion) {
        if (!direccion || typeof direccion !== "object") {
            return "Dirección no disponible";
        }

        if (direccion.textoCompleto) {
            return direccion.textoCompleto;
        }

        return [
            direccion.calle,
            direccion.colonia,
            direccion.alcaldiaMunicipio,
            direccion.codigoPostal,
            direccion.ciudad,
            direccion.estado
        ].filter(Boolean).join(", ") || "Dirección no disponible";
    }

    // =====================================
    // SERVICIOS
    // =====================================

    function mostrarServicios(servicios, urgencias24h) {
        serviciosVeterinaria.replaceChildren();

        const lista = Array.isArray(servicios) ? servicios : [];

        lista.forEach((servicio) => {
            const etiqueta = document.createElement("span");
            etiqueta.className = "detalle-servicio";

            etiqueta.textContent =
                typeof servicio === "string"
                    ? servicio
                    : servicio.nombre || "Servicio";

            serviciosVeterinaria.appendChild(etiqueta);
        });

        if (urgencias24h) {
            const etiqueta = document.createElement("span");
            etiqueta.className = "detalle-servicio urgencias";
            etiqueta.textContent = "Urgencias 24 h";
            serviciosVeterinaria.appendChild(etiqueta);
        }

        if (!serviciosVeterinaria.children.length) {
            const mensaje = document.createElement("span");
            mensaje.className = "text-muted small";
            mensaje.textContent = "Servicios no disponibles.";
            serviciosVeterinaria.appendChild(mensaje);
        }
    }

    // =====================================
    // HORARIOS
    // =====================================

    function mostrarHorarios(horarios) {
        horariosVeterinaria.replaceChildren();

        if (!Array.isArray(horarios) || horarios.length === 0) {
            horariosVeterinaria.textContent =
                "Horarios no disponibles.";
            return;
        }

        const dias = [
            "",
            "Lunes",
            "Martes",
            "Miércoles",
            "Jueves",
            "Viernes",
            "Sábado",
            "Domingo"
        ];

        horarios.forEach((horario) => {
            const linea = document.createElement("div");
            const dia = dias[horario.diaSemana] || "Día";

            linea.textContent =
                `${dia}: ${horario.abre} - ${horario.cierra}`;

            horariosVeterinaria.appendChild(linea);
        });
    }

    // =====================================
    // TELÉFONO
    // =====================================

    function mostrarTelefono(telefono) {
        botonLlamar.hidden = true;
        botonLlamar.removeAttribute("href");

        if (!telefono) {
            telefonoVeterinaria.textContent =
                "Teléfono no disponible.";
            return;
        }

        telefonoVeterinaria.textContent = telefono;

        const numero = String(telefono).replace(/[^\d+]/g, "");

        if (/^\+?\d{7,15}$/.test(numero)) {
            botonLlamar.href = `tel:${numero}`;
            botonLlamar.hidden = false;
        }
    }

    // =====================================
    // FOTOGRAFÍA
    // =====================================

    function mostrarImagen(veterinaria) {
        imagenVeterinaria.hidden = true;
        imagenPlaceholder.hidden = false;
        imagenVeterinaria.removeAttribute("src");

        const foto =
            veterinaria.fotoPrincipal ||
            (Array.isArray(veterinaria.fotos)
                ? veterinaria.fotos[0]?.url
                : null);

        if (!foto) {
            return;
        }

        try {
            const url = new URL(foto, window.location.href);

            if (!["https:", "http:"].includes(url.protocol)) {
                return;
            }

            imagenVeterinaria.onload = () => {
                imagenVeterinaria.hidden = false;
                imagenPlaceholder.hidden = true;
            };

            imagenVeterinaria.onerror = () => {
                imagenVeterinaria.hidden = true;
                imagenPlaceholder.hidden = false;
            };

            imagenVeterinaria.alt =
                `Fotografía de ${veterinaria.nombre}`;

            imagenVeterinaria.src = url.href;

        } catch (error) {
            console.warn("Imagen no válida:", error);
        }
    }

    // =====================================
    // MAPA INDIVIDUAL
    // =====================================

    function mostrarMapa(veterinaria) {
        const contenedorMapa = document.getElementById("mapaDetalle");

        const lat = Number(veterinaria.lat);
        const lng = Number(veterinaria.lng);

        const coordenadasValidas =
            veterinaria.lat != null &&
            veterinaria.lng != null &&
            Number.isFinite(lat) &&
            Number.isFinite(lng) &&
            lat >= -90 &&
            lat <= 90 &&
            lng >= -180 &&
            lng <= 180;

        if (!coordenadasValidas) {
            contenedorMapa.hidden = true;
            mensajeUbicacion.textContent =
                "La ubicación de esta veterinaria no está disponible.";
            botonVerMapa.href = "mapa.html";
            return;
        }

        if (typeof L === "undefined") {
            mensajeUbicacion.textContent =
                "No se pudo cargar el mapa interactivo.";
            return;
        }

        contenedorMapa.hidden = false;

        if (mapaDetalleLeaflet) {
            mapaDetalleLeaflet.remove();
        }

        mapaDetalleLeaflet = L.map("mapaDetalle").setView(
            [lat, lng],
            15
        );

        L.tileLayer(
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            {
                attribution:
                    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                maxZoom: 19
            }
        ).addTo(mapaDetalleLeaflet);

        const marcador = L.marker([lat, lng])
            .addTo(mapaDetalleLeaflet);

        const popup = document.createElement("div");

        const nombre = document.createElement("strong");
        nombre.textContent = veterinaria.nombre;

        const direccion = document.createElement("p");
        direccion.className = "mb-0";
        direccion.textContent = obtenerDireccion(veterinaria.direccion);

        popup.append(nombre, direccion);
        marcador.bindPopup(popup);

        // Mantener el ID de la clínica al abrir el mapa completo.
        botonVerMapa.href =
            `mapa.html?id=${encodeURIComponent(veterinaria.id)}`;

        mensajeUbicacion.textContent =
            "Ubicación proporcionada por la veterinaria.";

        requestAnimationFrame(() => {
            mapaDetalleLeaflet.invalidateSize();
        });
    }

    // =====================================
    // RENDERIZAR DETALLE
    // =====================================

    function mostrarVeterinaria(veterinaria) {
        nombreVeterinaria.textContent =
            veterinaria.nombre || "Veterinaria";

        direccionVeterinaria.textContent =
            obtenerDireccion(veterinaria.direccion);

        descripcionVeterinaria.textContent =
            veterinaria.descripcion ||
            "Información no disponible.";

        mostrarServicios(
            veterinaria.servicios,
            veterinaria.urgencias24h
        );

        mostrarHorarios(veterinaria.horarios);
        mostrarTelefono(veterinaria.telefono);
        mostrarImagen(veterinaria);

        mostrarContenido();
        mostrarMapa(veterinaria);

        document.title =
            `${veterinaria.nombre} | Vitalia`;
    }

    // =====================================
    // CONSULTAR FASTAPI
    // =====================================

    async function obtenerVeterinaria(id) {
        return await apiRequest(
            `/clinicas/${encodeURIComponent(id)}`
        );
    }

    // =====================================
    // INICIAR PÁGINA
    // =====================================

    async function iniciarDetalle() {
        if (!idVeterinaria || !/^\d+$/.test(idVeterinaria)) {
            mostrarEstado(
                "No se seleccionó una veterinaria válida. Regresa a Buscar veterinarias."
            );
            return;
        }

        mostrarEstado(
            "Cargando información de la veterinaria..."
        );

        try {
            const veterinaria =
                await obtenerVeterinaria(idVeterinaria);

            if (!veterinaria) {
                mostrarEstado(
                    "No encontramos la veterinaria seleccionada."
                );
                return;
            }

            mostrarVeterinaria(veterinaria);

        } catch (error) {
            console.error(
                "Error al cargar veterinaria:",
                error
            );

            mostrarEstado(
                "No fue posible cargar la información de esta veterinaria. Intenta nuevamente."
            );
        }
    }

    iniciarDetalle();
});
