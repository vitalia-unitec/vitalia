
/* =========================================
   VITALIA - BUSCAR VETERINARIAS
   Integración con FastAPI
========================================= */

document.addEventListener("DOMContentLoaded", () => {

    const formulario = document.getElementById("formBuscarVeterinarias");
    const ubicacionInput = document.getElementById("ubicacionBuscar");
    const radioSelect = document.getElementById("radioBuscar");
    const filtrosBotones = document.querySelectorAll(".filtro-buscar");
    const resultadosContenedor = document.getElementById("resultadosVeterinarias");
    const contadorResultados = document.getElementById("contadorResultados");
    const estadoBusqueda = document.getElementById("estadoBusqueda");
    const enlaceMapa = document.getElementById("enlaceMapa");

    const filtrosActivos = new Set();
    let busquedaRealizada = false;
    let veterinariasCargadas = [];
    let totalResultados = 0;
    let solicitudActual = 0;

    const nombresServicios = {
        consulta: "Consulta general",
        vacunas: "Vacunas",
        urgencias: "Urgencias 24 h",
        estetica: "Estética"
    };

    // =====================================
    // ESTADOS DE LA INTERFAZ
    // =====================================

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

        etiqueta.textContent = nombresServicios[servicio] || servicio;
        return etiqueta;
    }

    // =====================================
    // TARJETAS DE CLÍNICAS
    // =====================================

    function crearTarjeta(veterinaria) {
        const columna = document.createElement("div");
        columna.className = "col-md-6";

        const tarjeta = document.createElement("article");
        tarjeta.className = "tarjeta-veterinaria";

        const encabezado = document.createElement("div");
        encabezado.className = "d-flex align-items-start gap-3";

        const iconoContenedor = document.createElement("div");
        iconoContenedor.className = "veterinaria-icono";

        if (veterinaria.fotoPrincipal) {
            const imagen = document.createElement("img");
            imagen.src = veterinaria.fotoPrincipal;
            imagen.alt = `Foto de ${veterinaria.nombre}`;
            imagen.style.width = "100%";
            imagen.style.height = "100%";
            imagen.style.objectFit = "cover";
            iconoContenedor.appendChild(imagen);
        } else {
            const icono = document.createElement("i");
            icono.className = "bi bi-hospital";
            iconoContenedor.appendChild(icono);
        }

        const informacion = document.createElement("div");
        informacion.className = "flex-grow-1";

        const nombre = document.createElement("h3");
        nombre.className = "veterinaria-nombre";
        nombre.textContent = veterinaria.nombre;

        const descripcion = document.createElement("p");
        descripcion.className = "veterinaria-direccion mb-0";
        descripcion.textContent = veterinaria.tipos?.join(", ") || "Servicio veterinario";

        informacion.append(nombre, descripcion);
        encabezado.append(iconoContenedor, informacion);

        const servicios = document.createElement("div");
        servicios.className = "veterinaria-servicios";

        const destacados = Array.isArray(veterinaria.serviciosDestacados)
            ? veterinaria.serviciosDestacados
            : [];

        destacados.forEach((servicio) => {
            servicios.appendChild(crearEtiqueta(servicio));
        });

        if (veterinaria.urgencias24h) {
            servicios.appendChild(crearEtiqueta("urgencias"));
        }

        const acciones = document.createElement("div");
        acciones.className = "veterinaria-acciones";

        const detalle = document.createElement("a");
        detalle.className = "btn-detalle";
        detalle.href = `detalle-veterinaria.html?id=${encodeURIComponent(veterinaria.id)}`;
        detalle.textContent = "Ver detalles";

        const flecha = document.createElement("i");
        flecha.className = "bi bi-arrow-right";

        detalle.appendChild(flecha);
        acciones.appendChild(detalle);

        tarjeta.append(encabezado, servicios, acciones);
        columna.appendChild(tarjeta);

        return columna;
    }

    // =====================================
    // CONSTRUIR PARÁMETROS DE LA API
    // =====================================

    function construirParametros() {
        const parametros = new URLSearchParams();
        const texto = ubicacionInput.value.trim();

        if (texto.length >= 2) {
            parametros.set("q", texto);
        }

        if (filtrosActivos.has("abiertoAhora")) {
            parametros.set("abiertoAhora", "true");
        }

        if (filtrosActivos.has("urgencias")) {
            parametros.set("urgencias", "true");
        }

        // Categorías según el catálogo del backend.
        const categorias = ["consulta-general", "vacunas", "estetica"];
        const categoriaSeleccionada = categorias.find(
            categoria => filtrosActivos.has(categoria)
        );

        if (categoriaSeleccionada) {
            parametros.set("categoria", categoriaSeleccionada);
        }

        // La API solo permite una categoría por petición.
        // La distancia se aplica únicamente con coordenadas.
        parametros.set("pagina", "1");
        parametros.set("porPagina", "50");

        return parametros;
    }

    // =====================================
    // CONSULTAR FASTAPI
    // =====================================

    async function obtenerVeterinarias() {
        const parametros = construirParametros();

        const datos = await apiRequest(
            `/clinicas?${parametros.toString()}`
        );

        if (!Array.isArray(datos)) {
            throw new Error("La API no devolvió una lista de clínicas.");
        }

        return datos;
    }

    // =====================================
    // MOSTRAR RESULTADOS
    // =====================================

    function mostrarResultados() {
        resultadosContenedor.replaceChildren();

        if (!busquedaRealizada) {
            contadorResultados.textContent =
                "Ingresa una colonia o nombre para comenzar.";

            mostrarEstado("Realiza una búsqueda para explorar veterinarias.");
            return;
        }

        contadorResultados.textContent =
            `${veterinariasCargadas.length} clínica(s) mostrada(s)`;

        if (veterinariasCargadas.length === 0) {
            mostrarEstado(
                "No se encontraron veterinarias con los criterios seleccionados."
            );
            return;
        }

        ocultarEstado();

        veterinariasCargadas.forEach((veterinaria) => {
            resultadosContenedor.appendChild(crearTarjeta(veterinaria));
        });
    }

    // =====================================
    // EJECUTAR BÚSQUEDA
    // =====================================

    async function ejecutarBusqueda() {
        const texto = ubicacionInput.value.trim();

        if (texto.length < 2) {
            ubicacionInput.focus();
            contadorResultados.textContent =
                "Escribe al menos dos caracteres.";

            mostrarEstado(
                "Ingresa una colonia o el nombre de una veterinaria."
            );
            return;
        }

        const numeroSolicitud = ++solicitudActual;

        resultadosContenedor.replaceChildren();
        contadorResultados.textContent = "Buscando...";
        mostrarEstado("Consultando veterinarias...");

        try {
            const datos = await obtenerVeterinarias();

            if (numeroSolicitud !== solicitudActual) {
                return;
            }

            veterinariasCargadas = datos;
            totalResultados = datos.length;
            busquedaRealizada = true;

            mostrarResultados();

            const parametrosMapa = construirParametros();
            parametrosMapa.set("ubicacion", texto);

            enlaceMapa.href = `mapa.html?${parametrosMapa.toString()}`;

        } catch (error) {
            if (numeroSolicitud !== solicitudActual) {
                return;
            }

            console.error("Error al buscar clínicas:", error);

            veterinariasCargadas = [];
            totalResultados = 0;
            busquedaRealizada = false;

            contadorResultados.textContent =
                "No se pudo completar la búsqueda.";

            mostrarEstado(
                "No fue posible consultar las veterinarias. Intenta nuevamente."
            );
        }
    }

    // =====================================
    // FORMULARIO
    // =====================================

    formulario.addEventListener("submit", (evento) => {
        evento.preventDefault();
        ejecutarBusqueda();
    });

    // =====================================
    // FILTROS
    // =====================================

    function actualizarBotonFiltro(boton) {
        const activo = filtrosActivos.has(boton.dataset.filtro);
        boton.classList.toggle("active", activo);
        boton.setAttribute("aria-pressed", String(activo));
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
                ejecutarBusqueda();
            }
        });
    });

    // =====================================
    // PARÁMETROS DESDE HOME
    // =====================================

    function inicializarDesdeURL() {
        const parametros = new URLSearchParams(window.location.search);

        const ubicacion =
            parametros.get("ubicacion") ||
            parametros.get("location") ||
            parametros.get("q") ||
            "";

        const radio =
            parametros.get("radio") ||
            parametros.get("radioKm");

        const urgencias =
            parametros.get("urgencias") === "true";

        const categoria =
            parametros.get("categoria") ||
            parametros.get("servicio");

        if (ubicacion) {
            ubicacionInput.value = ubicacion;
        }

        if (
            radio &&
            [...radioSelect.options].some(
                opcion => opcion.value === radio
            )
        ) {
            radioSelect.value = radio;
        }

        if (urgencias) {
            filtrosActivos.add("urgencias");
        }

        if (categoria) {
            filtrosActivos.add(categoria);
        }

        if (parametros.get("abiertoAhora") === "true") {
            filtrosActivos.add("abiertoAhora");
        }

        filtrosBotones.forEach(actualizarBotonFiltro);

        if (ubicacionInput.value.trim().length >= 2) {
            ejecutarBusqueda();
        } else if (urgencias) {
            contadorResultados.textContent =
                "Filtro de urgencias activado.";

            mostrarEstado(
                "Ingresa una colonia o nombre para buscar veterinarias con urgencias."
            );
        }
    }

    inicializarDesdeURL();
});
