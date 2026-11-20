
/* =========================================
   VITALIA - BUSCAR VETERINARIAS
========================================= */

// Cambiar a false cuando conectemos FastAPI.
const MODO_DEMO = true;

// Endpoint provisional.
// Debe confirmarse con el equipo de backend.
const API_VETERINARIAS = "/api/veterinarias";

// Datos ficticios exclusivamente para probar el frontend.
// No representan negocios reales.
const veterinariasDemo = [
    {
        id: 1,
        nombre: "Clínica Patitas Felices",
        direccion: "Dirección de demostración 1",
        servicios: ["consulta", "vacunas", "urgencias"],
        abiertoAhora: true
    },
    {
        id: 2,
        nombre: "Centro Veterinario Huellitas",
        direccion: "Dirección de demostración 2",
        servicios: ["consulta", "estetica"],
        abiertoAhora: false
    },
    {
        id: 3,
        nombre: "Hospital Veterinario AnimalCare",
        direccion: "Dirección de demostración 3",
        servicios: ["consulta", "vacunas", "urgencias", "estetica"],
        abiertoAhora: true
    },
    {
        id: 4,
        nombre: "Veterinaria Amigos Peludos",
        direccion: "Dirección de demostración 4",
        servicios: ["consulta", "vacunas"],
        abiertoAhora: true
    }
];

const nombresServicios = {
    consulta: "Consulta general",
    vacunas: "Vacunas",
    urgencias: "Urgencias 24 h",
    estetica: "Estética"
};

// =========================================
// ELEMENTOS HTML
// =========================================

const formulario = document.getElementById(
    "formBuscarVeterinarias"
);

const ubicacionInput = document.getElementById(
    "ubicacionBuscar"
);

const radioSelect = document.getElementById(
    "radioBuscar"
);

const filtrosBotones = document.querySelectorAll(
    ".filtro-buscar"
);

const resultadosContenedor = document.getElementById(
    "resultadosVeterinarias"
);

const contadorResultados = document.getElementById(
    "contadorResultados"
);

const estadoBusqueda = document.getElementById(
    "estadoBusqueda"
);

const enlaceMapa = document.getElementById(
    "enlaceMapa"
);

// =========================================
// ESTADO DE BÚSQUEDA
// =========================================

const filtrosActivos = new Set();

let busquedaRealizada = false;
let veterinariasCargadas = [];

// =========================================
// FUNCIONES DE INTERFAZ
// =========================================

function mostrarEstado(mensaje) {
    estadoBusqueda.hidden = false;
    estadoBusqueda.style.display = "block";

    estadoBusqueda.replaceChildren();

    const icono = document.createElement("i");
    icono.className = "bi bi-search-heart fs-1";

    const texto = document.createElement("p");
    texto.className = "mt-3 mb-0";
    texto.textContent = mensaje;

    estadoBusqueda.append(icono, texto);
}

function ocultarEstado() {
    estadoBusqueda.hidden = true;
    estadoBusqueda.style.display = "none";
}

function crearEtiqueta(servicio) {
    const etiqueta = document.createElement("span");

    etiqueta.className = "etiqueta-servicio";

    if (servicio === "urgencias") {
        etiqueta.classList.add("etiqueta-urgencias");
    }

    etiqueta.textContent =
        nombresServicios[servicio] || servicio;

    return etiqueta;
}

// =========================================
// CREAR TARJETAS DE VETERINARIAS
// =========================================

function crearTarjeta(veterinaria) {
    const columna = document.createElement("div");

    columna.className = "col-md-6";

    const tarjeta = document.createElement("article");
    tarjeta.className = "tarjeta-veterinaria";

    const encabezado = document.createElement("div");
    encabezado.className =
        "d-flex align-items-start gap-3";

    const iconoContenedor = document.createElement("div");
    iconoContenedor.className = "veterinaria-icono";

    const icono = document.createElement("i");
    icono.className = "bi bi-hospital";

    iconoContenedor.appendChild(icono);

    const informacion = document.createElement("div");
    informacion.className = "flex-grow-1";

    const nombre = document.createElement("h3");
    nombre.className = "veterinaria-nombre";
    nombre.textContent = veterinaria.nombre;

    const direccion = document.createElement("p");
    direccion.className =
        "veterinaria-direccion mb-0";
    direccion.textContent = veterinaria.direccion;

    informacion.append(nombre, direccion);

    encabezado.append(iconoContenedor, informacion);

    const servicios = document.createElement("div");
    servicios.className = "veterinaria-servicios";

    veterinaria.servicios.forEach((servicio) => {
        servicios.appendChild(crearEtiqueta(servicio));
    });

    const acciones = document.createElement("div");
    acciones.className = "veterinaria-acciones";

    const detalle = document.createElement("a");
    detalle.className = "btn-detalle";

    detalle.href =
        `detalle-veterinaria.html?id=${encodeURIComponent(veterinaria.id)}`;

    detalle.textContent = "Ver detalles";

    const flecha = document.createElement("i");
    flecha.className = "bi bi-arrow-right";

    detalle.appendChild(flecha);
    acciones.appendChild(detalle);

    tarjeta.append(encabezado, servicios, acciones);
    columna.appendChild(tarjeta);

    return columna;
}

// =========================================
// APLICAR FILTROS
// =========================================

function filtrarVeterinarias(veterinarias) {
    return veterinarias.filter((veterinaria) => {

        if (
            filtrosActivos.has("abiertoAhora") &&
            !veterinaria.abiertoAhora
        ) {
            return false;
        }

        for (const filtro of filtrosActivos) {
            if (filtro === "abiertoAhora") {
                continue;
            }

            if (!veterinaria.servicios.includes(filtro)) {
                return false;
            }
        }

        return true;
    });
}

// =========================================
// MOSTRAR RESULTADOS
// =========================================

function mostrarResultados() {
    resultadosContenedor.replaceChildren();

    if (!busquedaRealizada) {
        contadorResultados.textContent =
            "Ingresa una ubicación para comenzar.";

        mostrarEstado(
            "Realiza una búsqueda para explorar veterinarias."
        );

        return;
    }

    const filtradas = filtrarVeterinarias(
        veterinariasCargadas
    );

    contadorResultados.textContent =
        `${filtradas.length} resultado(s) encontrado(s)`;

    if (filtradas.length === 0) {
        mostrarEstado(
            "No se encontraron veterinarias con los filtros seleccionados."
        );

        return;
    }

    ocultarEstado();

    filtradas.forEach((veterinaria) => {
        resultadosContenedor.appendChild(
            crearTarjeta(veterinaria)
        );
    });
}

// =========================================
// OBTENER RESULTADOS
// =========================================

async function obtenerVeterinarias() {
    if (MODO_DEMO) {
        // La ubicación y el radio no se aplican en demo,
        // porque los registros ficticios no tienen coordenadas.
        return veterinariasDemo;
    }

    const parametros = new URLSearchParams({
        ubicacion: ubicacionInput.value.trim(),
        radio_km: radioSelect.value
    });

    const respuesta = await fetch(
        `${API_VETERINARIAS}?${parametros.toString()}`,
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

    // Este formato debe validarse con el backend.
    if (!Array.isArray(datos)) {
        throw new Error(
            "El formato de respuesta no es el esperado."
        );
    }

    return datos;
}

// =========================================
// EJECUTAR BÚSQUEDA
// =========================================

async function ejecutarBusqueda() {
    const ubicacion = ubicacionInput.value.trim();

    if (!ubicacion) {
        ubicacionInput.focus();

        contadorResultados.textContent =
            "Escribe una ubicación.";

        mostrarEstado(
            "Necesitamos una ubicación para buscar veterinarias."
        );

        return;
    }

    busquedaRealizada = true;

    resultadosContenedor.replaceChildren();

    contadorResultados.textContent = "Buscando...";

    mostrarEstado(
        MODO_DEMO
            ? "Cargando veterinarias de demostración..."
            : "Consultando veterinarias..."
    );

    try {
        veterinariasCargadas =
            await obtenerVeterinarias();

        mostrarResultados();

        // Conserva los parámetros para el mapa.
        const parametrosMapa = new URLSearchParams({
            ubicacion,
            radio: radioSelect.value
        });

        if (filtrosActivos.size > 0) {
            parametrosMapa.set(
                "filtros",
                [...filtrosActivos].join(",")
            );
        }

        enlaceMapa.href =
            `mapa.html?${parametrosMapa.toString()}`;

    } catch (error) {
        console.error(error);

        veterinariasCargadas = [];
        busquedaRealizada = false;

        contadorResultados.textContent =
            "No se pudo completar la búsqueda.";

        mostrarEstado(
            "Ocurrió un error. Intenta nuevamente."
        );
    }
}

// =========================================
// FORMULARIO
// =========================================

formulario.addEventListener("submit", (evento) => {
    evento.preventDefault();
    ejecutarBusqueda();
});

// =========================================
// BOTONES DE FILTROS
// =========================================

function actualizarBotonFiltro(boton) {
    const activo = filtrosActivos.has(
        boton.dataset.filtro
    );

    boton.classList.toggle("active", activo);

    boton.setAttribute(
        "aria-pressed",
        String(activo)
    );
}

filtrosBotones.forEach((boton) => {
    boton.addEventListener("click", () => {
        const filtro = boton.dataset.filtro;

        if (filtrosActivos.has(filtro)) {
            filtrosActivos.delete(filtro);
        } else {
            filtrosActivos.add(filtro);
        }

        actualizarBotonFiltro(boton);

        if (busquedaRealizada) {
            mostrarResultados();
        }
    });
});

// =========================================
// PARÁMETROS DESDE HOME
// =========================================

function inicializarDesdeURL() {
    const parametros = new URLSearchParams(
        window.location.search
    );

    const ubicacion =
        parametros.get("ubicacion") ||
        parametros.get("location") ||
        "";

    const radio =
        parametros.get("radio") ||
        parametros.get("radio_km");

    const urgencias =
        parametros.get("urgencias") === "true";

    const servicio = parametros.get("servicio");

    if (ubicacion) {
        ubicacionInput.value = ubicacion;
    }

    if (
        radio &&
        [...radioSelect.options].some(
            (opcion) => opcion.value === radio
        )
    ) {
        radioSelect.value = radio;
    }

    if (urgencias) {
        filtrosActivos.add("urgencias");
    }

    if (
        servicio &&
        Object.prototype.hasOwnProperty.call(
            nombresServicios,
            servicio
        )
    ) {
        filtrosActivos.add(servicio);
    }

    filtrosBotones.forEach(actualizarBotonFiltro);

    // Si viene una ubicación, realiza la búsqueda.
    if (ubicacionInput.value.trim()) {
        ejecutarBusqueda();
    } else if (urgencias) {
        contadorResultados.textContent =
            "Filtro de urgencias activado.";

        mostrarEstado(
            "Escribe una ubicación para buscar veterinarias con urgencias 24 h."
        );
    }
}

// =========================================
// INICIO
// =========================================

inicializarDesdeURL();
