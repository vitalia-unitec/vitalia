
/* =========================================
   VITALIA - MAPA DE VETERINARIAS
========================================= */

// Cambiar a false al conectar el backend.
const MODO_DEMO_MAPA = true;

// Endpoint provisional: confirmar con backend.
const API_VETERINARIAS_MAPA = "/api/veterinarias";

// Coordenadas ficticias de demostración.
// NO son ubicaciones reales de estas clínicas.
const veterinariasDemoMapa = [
    {
        id: 1,
        nombre: "Clínica Patitas Felices",
        direccion: "Ubicación ficticia de demostración",
        latitud: 19.4326,
        longitud: -99.1332,
        servicios: ["consulta", "vacunas", "urgencias"],
        abiertoAhora: true
    },
    {
        id: 2,
        nombre: "Centro Veterinario Huellitas",
        direccion: "Ubicación ficticia de demostración",
        latitud: 19.4270,
        longitud: -99.1450,
        servicios: ["consulta", "estetica"],
        abiertoAhora: false
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
        abiertoAhora: true
    },
    {
        id: 4,
        nombre: "Veterinaria Amigos Peludos",
        direccion: "Ubicación ficticia de demostración",
        latitud: 19.4200,
        longitud: -99.1550,
        servicios: ["consulta", "vacunas"],
        abiertoAhora: true
    }
];

const etiquetasServiciosMapa = {
    consulta: "Consulta general",
    vacunas: "Vacunas",
    urgencias: "Urgencias 24 h",
    estetica: "Estética"
};

// =========================================
// ELEMENTOS HTML
// =========================================

const listaMapa = document.getElementById(
    "listaVeterinariasMapa"
);

const contadorMapa = document.getElementById(
    "contadorMapa"
);

const botonCentrar = document.getElementById(
    "botonCentrarMapa"
);

const volverBusqueda = document.getElementById(
    "volverBusqueda"
);

// =========================================
// PARÁMETROS DESDE BUSCAR
// =========================================

const parametrosURL = new URLSearchParams(
    window.location.search
);

const ubicacion = parametrosURL.get("ubicacion") || "";

const radio = parametrosURL.get("radio") || "10";

const filtrosPermitidos = new Set([
    "abiertoAhora",
    "urgencias",
    "consulta",
    "vacunas",
    "estetica"
]);

const filtros = (
    parametrosURL.get("filtros") || ""
)
    .split(",")
    .filter((filtro) => filtrosPermitidos.has(filtro));

// Mantener parámetros al regresar.
const parametrosRegreso = new URLSearchParams();

if (ubicacion) {
    parametrosRegreso.set("ubicacion", ubicacion);
}

parametrosRegreso.set("radio", radio);

if (filtros.includes("urgencias")) {
    parametrosRegreso.set("urgencias", "true");
}

if (parametrosRegreso.toString()) {
    volverBusqueda.href =
        `buscar.html?${parametrosRegreso.toString()}`;
}

// =========================================
// INICIALIZAR LEAFLET
// =========================================

const mapa = L.map("mapaVeterinarias").setView(
    [19.4326, -99.1332],
    12
);

L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }
).addTo(mapa);

const grupoMarcadores = L.featureGroup().addTo(mapa);

const marcadoresPorId = new Map();

let veterinariasVisibles = [];

// =========================================
// MENSAJE SIN RESULTADOS
// =========================================

function mostrarMensajeMapa(mensaje) {
    listaMapa.replaceChildren();

    const contenedor = document.createElement("div");
    contenedor.className = "mapa-sin-resultados";

    const icono = document.createElement("i");
    icono.className = "bi bi-geo-alt";

    const texto = document.createElement("p");
    texto.className = "mb-0";
    texto.textContent = mensaje;

    contenedor.append(icono, texto);
    listaMapa.appendChild(contenedor);
}

// =========================================
// FILTRAR VETERINARIAS
// =========================================

function filtrarVeterinariasMapa(veterinarias) {
    return veterinarias.filter((veterinaria) => {
        for (const filtro of filtros) {
            if (filtro === "abiertoAhora") {
                if (!veterinaria.abiertoAhora) {
                    return false;
                }
            } else if (
                !veterinaria.servicios.includes(filtro)
            ) {
                return false;
            }
        }

        return true;
    });
}

// =========================================
// CENTRAR MAPA EN VETERINARIA
// =========================================

function seleccionarVeterinaria(id) {
    const marcador = marcadoresPorId.get(String(id));

    if (!marcador) {
        return;
    }

    const posicion = marcador.getLatLng();

    mapa.setView(posicion, 15, {
        animate: true
    });

    marcador.openPopup();

    document.querySelectorAll(".tarjeta-mapa")
        .forEach((tarjeta) => {
            tarjeta.classList.toggle(
                "seleccionada",
                tarjeta.dataset.id === String(id)
            );
        });
}

// =========================================
// CREAR TARJETA
// =========================================

function crearTarjetaMapa(veterinaria) {
    const tarjeta = document.createElement("article");

    tarjeta.className = "tarjeta-mapa";
    tarjeta.dataset.id = String(veterinaria.id);

    const titulo = document.createElement("h3");
    titulo.textContent = veterinaria.nombre;

    const direccion = document.createElement("p");
    direccion.className = "direccion-mapa";
    direccion.textContent = veterinaria.direccion;

    const servicios = document.createElement("div");
    servicios.className = "servicios-mapa";

    veterinaria.servicios.forEach((servicio) => {
        const etiqueta = document.createElement("span");

        etiqueta.className = "servicio-mapa";

        if (servicio === "urgencias") {
            etiqueta.classList.add("urgencias");
        }

        etiqueta.textContent =
            etiquetasServiciosMapa[servicio] || servicio;

        servicios.appendChild(etiqueta);
    });

    const acciones = document.createElement("div");
    acciones.className = "acciones-mapa";

    const botonUbicacion = document.createElement("button");
    botonUbicacion.type = "button";
    botonUbicacion.className = "btn-ver-ubicacion";
    botonUbicacion.textContent = "Ver ubicación";

    botonUbicacion.addEventListener("click", () => {
        seleccionarVeterinaria(veterinaria.id);
    });

    const botonDetalles = document.createElement("a");
    botonDetalles.className = "btn-ver-detalles";
    botonDetalles.textContent = "Ver detalles";

    botonDetalles.href =
        `detalle-veterinaria.html?id=${encodeURIComponent(veterinaria.id)}`;

    acciones.append(botonUbicacion, botonDetalles);

    tarjeta.append(
        titulo,
        direccion,
        servicios,
        acciones
    );

    return tarjeta;
}

// =========================================
// CREAR MARCADORES
// =========================================

function agregarMarcador(veterinaria) {
    const marcador = L.marker([
        veterinaria.latitud,
        veterinaria.longitud
    ]);

    // Popup construido con DOM para evitar
    // insertar HTML no confiable.
    const popup = document.createElement("div");

    const nombre = document.createElement("strong");
    nombre.textContent = veterinaria.nombre;

    const direccion = document.createElement("p");
    direccion.className = "mb-1";
    direccion.textContent = veterinaria.direccion;

    const aviso = document.createElement("small");

    if (MODO_DEMO_MAPA) {
        aviso.textContent = "Ubicación de demostración";
    }

    popup.append(nombre, direccion, aviso);

    marcador.bindPopup(popup);

    marcador.on("click", () => {
        seleccionarVeterinaria(veterinaria.id);
    });

    marcador.addTo(grupoMarcadores);

    marcadoresPorId.set(
        String(veterinaria.id),
        marcador
    );
}

// =========================================
// MOSTRAR TODAS LAS UBICACIONES
// =========================================

function mostrarTodasLasUbicaciones() {
    if (grupoMarcadores.getLayers().length === 0) {
        return;
    }

    mapa.fitBounds(
        grupoMarcadores.getBounds(),
        {
            padding: [35, 35],
            maxZoom: 14
        }
    );
}

botonCentrar.addEventListener(
    "click",
    mostrarTodasLasUbicaciones
);

// =========================================
// MOSTRAR RESULTADOS EN MAPA
// =========================================

function mostrarResultadosMapa(veterinarias) {
    listaMapa.replaceChildren();

    grupoMarcadores.clearLayers();
    marcadoresPorId.clear();

    veterinariasVisibles =
        filtrarVeterinariasMapa(veterinarias);

    contadorMapa.textContent =
        `${veterinariasVisibles.length} veterinaria(s) encontrada(s)`;

    if (veterinariasVisibles.length === 0) {
        mostrarMensajeMapa(
            "No hay veterinarias que coincidan con los filtros seleccionados."
        );

        return;
    }

    veterinariasVisibles.forEach((veterinaria) => {
        listaMapa.appendChild(
            crearTarjetaMapa(veterinaria)
        );

        if (
            Number.isFinite(veterinaria.latitud) &&
            Number.isFinite(veterinaria.longitud)
        ) {
            agregarMarcador(veterinaria);
        }
    });

    mostrarTodasLasUbicaciones();
}

// =========================================
// OBTENER VETERINARIAS
// =========================================

async function obtenerVeterinariasMapa() {
    if (MODO_DEMO_MAPA) {
        // Los datos demo no filtran por ubicación
        // ni por radio: solo por servicios.
        return veterinariasDemoMapa;
    }

    const parametros = new URLSearchParams({
        ubicacion,
        radio_km: radio
    });

    const respuesta = await fetch(
        `${API_VETERINARIAS_MAPA}?${parametros.toString()}`,
        {
            method: "GET",
            credentials: "include",
            headers: {
                Accept: "application/json"
            }
        }
    );

    if (!respuesta.ok) {
        throw new Error(
            "No fue posible consultar las veterinarias."
        );
    }

    const datos = await respuesta.json();

    // Confirmar estructura con el equipo backend.
    if (!Array.isArray(datos)) {
        throw new Error(
            "El backend no devolvió una lista válida."
        );
    }

    return datos;
}

// =========================================
// INICIAR MAPA
// =========================================

async function iniciarMapa() {
    contadorMapa.textContent = "Cargando veterinarias...";

    try {
        const veterinarias =
            await obtenerVeterinariasMapa();

        mostrarResultadosMapa(veterinarias);

        if (MODO_DEMO_MAPA) {
            const aviso = document.createElement("p");
            aviso.className = "small text-muted mt-3 mb-0";
            aviso.textContent =
                "Modo demostración: las clínicas y sus ubicaciones son ficticias.";

            listaMapa.after(aviso);
        }

    } catch (error) {
        console.error(error);

        contadorMapa.textContent =
            "No se pudieron cargar las veterinarias.";

        mostrarMensajeMapa(
            "Ocurrió un error al cargar el mapa. Intenta nuevamente."
        );
    }
}

iniciarMapa();
