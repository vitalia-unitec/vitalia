
/* =========================================
   VITALIA - DETALLE DE VETERINARIA
========================================= */

// Cambiar a false cuando se conecte FastAPI.
const MODO_DEMO_DETALLE = true;

// Endpoint provisional.
// Confirmar con el equipo de backend.
const API_DETALLE = "/api/veterinarias";

// =========================================
// DATOS DE DEMOSTRACIÓN
// =========================================

// Estas clínicas son ficticias.
// Sus coordenadas son únicamente para
// probar el funcionamiento de Leaflet.

const veterinariasDemoDetalle = [
    {
        id: 1,
        nombre: "Clínica Patitas Felices",
        direccion: "Ubicación ficticia de demostración",
        latitud: 19.4326,
        longitud: -99.1332,
        servicios: [
            "consulta",
            "vacunas",
            "urgencias"
        ],
        horarios: null,
        telefono: null,
        descripcion:
            "Clínica veterinaria de demostración utilizada para probar la página de detalles de Vitalia.",
        imagen: null
    },
    {
        id: 2,
        nombre: "Centro Veterinario Huellitas",
        direccion: "Ubicación ficticia de demostración",
        latitud: 19.4270,
        longitud: -99.1450,
        servicios: [
            "consulta",
            "estetica"
        ],
        horarios: null,
        telefono: null,
        descripcion:
            "Centro veterinario ficticio utilizado para probar la presentación de servicios e información de contacto.",
        imagen: null
    },
    {
        id: 3,
        nombre: "Hospital Veterinario AnimalCare",
        direccion: "Ubicación ficticia de demostración",
        latitud: 19.4400,
        longitud: -99.1250,
        servicios: [
            "consulta",
            "vacunas",
            "urgencias",
            "estetica"
        ],
        horarios: null,
        telefono: null,
        descripcion:
            "Hospital veterinario de demostración con diferentes servicios para comprobar los componentes de Vitalia.",
        imagen: null
    },
    {
        id: 4,
        nombre: "Veterinaria Amigos Peludos",
        direccion: "Ubicación ficticia de demostración",
        latitud: 19.4200,
        longitud: -99.1550,
        servicios: [
            "consulta",
            "vacunas"
        ],
        horarios: null,
        telefono: null,
        descripcion:
            "Veterinaria ficticia creada para probar la navegación entre el buscador, el mapa y la página de detalles.",
        imagen: null
    }
];

// =========================================
// NOMBRES DE SERVICIOS
// =========================================

const nombresServiciosDetalle = {
    consulta: "Consulta general",
    vacunas: "Vacunas",
    urgencias: "Urgencias 24 h",
    estetica: "Estética"
};

// =========================================
// ELEMENTOS HTML
// =========================================

const estadoDetalle = document.getElementById(
    "estadoDetalle"
);

const contenidoDetalle = document.getElementById(
    "contenidoDetalle"
);

const nombreVeterinaria = document.getElementById(
    "nombreVeterinaria"
);

const direccionVeterinaria = document.getElementById(
    "direccionVeterinaria"
);

const serviciosVeterinaria = document.getElementById(
    "serviciosVeterinaria"
);

const horariosVeterinaria = document.getElementById(
    "horariosVeterinaria"
);

const telefonoVeterinaria = document.getElementById(
    "telefonoVeterinaria"
);

const descripcionVeterinaria = document.getElementById(
    "descripcionVeterinaria"
);

const imagenVeterinaria = document.getElementById(
    "imagenVeterinaria"
);

const imagenPlaceholder = document.getElementById(
    "imagenPlaceholder"
);

const botonLlamar = document.getElementById(
    "botonLlamar"
);

const botonVerMapa = document.getElementById(
    "botonVerMapa"
);

const mensajeUbicacion = document.getElementById(
    "mensajeUbicacion"
);

// =========================================
// OBTENER ID DESDE LA URL
// =========================================

const parametrosURLDetalle = new URLSearchParams(
    window.location.search
);

const idVeterinaria = parametrosURLDetalle.get("id");

// =========================================
// MOSTRAR ESTADO
// =========================================

function mostrarEstadoDetalle(mensaje) {
    contenidoDetalle.hidden = true;

    estadoDetalle.hidden = false;
    estadoDetalle.textContent = mensaje;
}

function mostrarContenidoDetalle() {
    estadoDetalle.hidden = true;
    contenidoDetalle.hidden = false;
}

// =========================================
// OBTENER VETERINARIA
// =========================================

async function obtenerDetalleVeterinaria(id) {

    if (MODO_DEMO_DETALLE) {
        return veterinariasDemoDetalle.find(
            (veterinaria) =>
                String(veterinaria.id) === String(id)
        ) || null;
    }

    const respuesta = await fetch(
        `${API_DETALLE}/${encodeURIComponent(id)}`,
        {
            method: "GET",
            credentials: "include",
            headers: {
                Accept: "application/json"
            }
        }
    );

    if (respuesta.status === 404) {
        return null;
    }

    if (!respuesta.ok) {
        throw new Error(
            "No fue posible consultar la veterinaria."
        );
    }

    // La estructura de respuesta debe
    // confirmarse con el backend.
    return await respuesta.json();
}

// =========================================
// MOSTRAR SERVICIOS
// =========================================

function mostrarServiciosDetalle(servicios) {

    serviciosVeterinaria.replaceChildren();

    if (!Array.isArray(servicios) ||
        servicios.length === 0) {

        const mensaje = document.createElement("span");

        mensaje.className = "text-muted small";
        mensaje.textContent =
            "Servicios no disponibles.";

        serviciosVeterinaria.appendChild(mensaje);

        return;
    }

    servicios.forEach((servicio) => {

        const etiqueta = document.createElement("span");

        etiqueta.className = "detalle-servicio";

        if (servicio === "urgencias") {
            etiqueta.classList.add("urgencias");
        }

        etiqueta.textContent =
            nombresServiciosDetalle[servicio] ||
            servicio;

        serviciosVeterinaria.appendChild(etiqueta);
    });
}

// =========================================
// MOSTRAR IMAGEN
// =========================================

function mostrarImagenDetalle(veterinaria) {

    imagenVeterinaria.hidden = true;
    imagenPlaceholder.hidden = false;

    imagenVeterinaria.removeAttribute("src");

    if (!veterinaria.imagen) {
        return;
    }

    // Aceptar únicamente URLs HTTPS.
    // El backend deberá validar las imágenes.
    try {
        const urlImagen = new URL(
            veterinaria.imagen,
            window.location.href
        );

        if (urlImagen.protocol !== "https:") {
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

        imagenVeterinaria.src = urlImagen.href;

    } catch (error) {
        console.warn(
            "La URL de la imagen no es válida.",
            error
        );
    }
}

// =========================================
// MOSTRAR TELÉFONO
// =========================================

function mostrarTelefonoDetalle(telefono) {

    botonLlamar.hidden = true;
    botonLlamar.removeAttribute("href");

    if (!telefono) {
        telefonoVeterinaria.textContent =
            "Por consultar";

        return;
    }

    telefonoVeterinaria.textContent = telefono;

    const numeroLimpio = String(telefono)
        .replace(/[^\d+]/g, "");

    if (/^\+?\d{7,15}$/.test(numeroLimpio)) {
        botonLlamar.href = `tel:${numeroLimpio}`;
        botonLlamar.hidden = false;
    }
}

// =========================================
// INICIALIZAR MAPA INDIVIDUAL
// =========================================

let mapaDetalleLeaflet = null;

function mostrarMapaDetalle(veterinaria) {

    const latitud = Number(veterinaria.latitud);
    const longitud = Number(veterinaria.longitud);

    const tieneCoordenadas =
        veterinaria.latitud !== null &&
        veterinaria.latitud !== undefined &&
        veterinaria.longitud !== null &&
        veterinaria.longitud !== undefined &&
        Number.isFinite(latitud) &&
        Number.isFinite(longitud) &&
        latitud >= -90 &&
        latitud <= 90 &&
        longitud >= -180 &&
        longitud <= 180;

    if (!tieneCoordenadas) {
        document.getElementById(
            "mapaDetalle"
        ).hidden = true;

        mensajeUbicacion.textContent =
            "La ubicación de esta veterinaria todavía no está disponible.";

        botonVerMapa.href = "mapa.html";
        return;
    }

    document.getElementById(
        "mapaDetalle"
    ).hidden = false;

    if (typeof L === "undefined") {
        mensajeUbicacion.textContent =
            "No se pudo cargar el mapa interactivo.";
        return;
    }

    if (mapaDetalleLeaflet) {
        mapaDetalleLeaflet.remove();
    }

    mapaDetalleLeaflet = L.map("mapaDetalle").setView(
        [latitud, longitud],
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

    const marcador = L.marker([
        latitud,
        longitud
    ]).addTo(mapaDetalleLeaflet);

    // Crear popup sin insertar HTML externo.
    const popup = document.createElement("div");

    const nombre = document.createElement("strong");
    nombre.textContent = veterinaria.nombre;

    const direccion = document.createElement("p");
    direccion.className = "mb-0";
    direccion.textContent = veterinaria.direccion;

    popup.append(nombre, direccion);

    marcador.bindPopup(popup);

    // Enviar el ID al mapa completo.
    const parametrosMapa = new URLSearchParams({
        id: String(veterinaria.id)
    });

    botonVerMapa.href =
        `mapa.html?${parametrosMapa.toString()}`;

    mensajeUbicacion.textContent =
        MODO_DEMO_DETALLE
            ? "Ubicación ficticia de demostración. No corresponde a una clínica real."
            : "Ubicación proporcionada por la veterinaria.";

    // Corregir el tamaño del mapa cuando
    // el contenido ya esté visible.
    requestAnimationFrame(() => {
        mapaDetalleLeaflet.invalidateSize();
    });
}

// =========================================
// RENDERIZAR DETALLE
// =========================================

function mostrarVeterinariaDetalle(veterinaria) {

    nombreVeterinaria.textContent =
        veterinaria.nombre || "Veterinaria";

    direccionVeterinaria.textContent =
        veterinaria.direccion ||
        "Dirección no disponible";

    horariosVeterinaria.textContent =
        veterinaria.horarios ||
        "Por consultar";

    descripcionVeterinaria.textContent =
        veterinaria.descripcion ||
        "Información no disponible.";

    mostrarServiciosDetalle(
        veterinaria.servicios
    );

    mostrarTelefonoDetalle(
        veterinaria.telefono
    );

    mostrarImagenDetalle(
        veterinaria
    );

    // Mostrar primero el contenedor para
    // que Leaflet pueda calcular su tamaño.
    mostrarContenidoDetalle();

    mostrarMapaDetalle(veterinaria);

    document.title =
        `${veterinaria.nombre} | Vitalia`;
}

// =========================================
// INICIAR PÁGINA
// =========================================

async function iniciarDetalleVeterinaria() {

    if (!idVeterinaria) {
        mostrarEstadoDetalle(
            "No se seleccionó ninguna veterinaria. Regresa a Buscar veterinarias."
        );

        return;
    }

    mostrarEstadoDetalle(
        "Cargando información de la veterinaria..."
    );

    try {
        const veterinaria =
            await obtenerDetalleVeterinaria(
                idVeterinaria
            );

        if (!veterinaria) {
            mostrarEstadoDetalle(
                "No encontramos la veterinaria seleccionada."
            );

            return;
        }

        mostrarVeterinariaDetalle(veterinaria);

    } catch (error) {
        console.error(error);

        mostrarEstadoDetalle(
            "Ocurrió un error al cargar la información. Intenta nuevamente."
        );
    }
}

// Iniciar
iniciarDetalleVeterinaria();
