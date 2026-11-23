
/* =========================================
   VITALIA - MAPA DE VETERINARIAS
   Integración FastAPI + Leaflet
========================================= */

document.addEventListener("DOMContentLoaded", () => {

    // =====================================
    // ELEMENTOS HTML
    // =====================================

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

    const parametrosURL = new URLSearchParams(
        window.location.search
    );

    // =====================================
    // INICIALIZAR LEAFLET
    // =====================================

    const mapa = L.map("mapaVeterinarias").setView(
        [19.4326, -99.1332],
        11
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

    // =====================================
    // PARÁMETROS DESDE BUSCAR
    // =====================================

    function construirParametros() {
        const parametros = new URLSearchParams();

        const texto = (
            parametrosURL.get("q") ||
            parametrosURL.get("ubicacion") ||
            ""
        ).trim();

        if (texto.length >= 2) {
            parametros.set("q", texto);
        }

        const tipo = parametrosURL.get("tipo");
        const categoria = parametrosURL.get("categoria");

        if (tipo) {
            parametros.set("tipo", tipo);
        }

        if (categoria) {
            parametros.set("categoria", categoria);
        }

        if (parametrosURL.get("urgencias") === "true") {
            parametros.set("urgencias", "true");
        }

        if (parametrosURL.get("abiertoAhora") === "true") {
            parametros.set("abiertoAhora", "true");
        }

        // Aplicar radio únicamente con coordenadas.
        const lat = parametrosURL.get("lat");
        const lng = parametrosURL.get("lng");

        if (lat !== null && lng !== null) {
            const latNumero = Number(lat);
            const lngNumero = Number(lng);

            if (
                Number.isFinite(latNumero) &&
                Number.isFinite(lngNumero) &&
                latNumero >= -90 &&
                latNumero <= 90 &&
                lngNumero >= -180 &&
                lngNumero <= 180
            ) {
                parametros.set("lat", String(latNumero));
                parametros.set("lng", String(lngNumero));

                const radio = Number(
                    parametrosURL.get("radioKm") ||
                    parametrosURL.get("radio") ||
                    10
                );

                if (
                    Number.isFinite(radio) &&
                    radio >= 1 &&
                    radio <= 50
                ) {
                    parametros.set("radioKm", String(radio));
                }
            }
        }

        parametros.set("pagina", "1");
        parametros.set("porPagina", "50");

        return parametros;
    }

    // =====================================
    // REGRESAR A BUSCAR
    // =====================================

    function configurarRegreso() {
        const parametros = new URLSearchParams();

        const texto = (
            parametrosURL.get("ubicacion") ||
            parametrosURL.get("q") ||
            ""
        ).trim();

        if (texto) {
            parametros.set("ubicacion", texto);
        }

        const radio =
            parametrosURL.get("radio") ||
            parametrosURL.get("radioKm");

        if (radio) {
            parametros.set("radio", radio);
        }

        for (const nombre of [
            "categoria",
            "tipo",
            "urgencias",
            "abiertoAhora"
        ]) {
            const valor = parametrosURL.get(nombre);

            if (valor !== null) {
                parametros.set(nombre, valor);
            }
        }

        volverBusqueda.href = parametros.toString()
            ? `buscar.html?${parametros.toString()}`
            : "buscar.html";
    }

    // =====================================
    // MENSAJES
    // =====================================

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

    // =====================================
    // SELECCIONAR VETERINARIA
    // =====================================

    function seleccionarVeterinaria(id) {
        const marcador = marcadoresPorId.get(String(id));

        if (!marcador) {
            return false;
        }

        mapa.setView(
            marcador.getLatLng(),
            15,
            { animate: true }
        );

        marcador.openPopup();

        document.querySelectorAll(".tarjeta-mapa")
            .forEach((tarjeta) => {
                tarjeta.classList.toggle(
                    "seleccionada",
                    tarjeta.dataset.id === String(id)
                );
            });

        return true;
    }

    // =====================================
    // CREAR TARJETAS
    // =====================================

    function crearTarjetaMapa(veterinaria) {
        const tarjeta = document.createElement("article");

        tarjeta.className = "tarjeta-mapa";
        tarjeta.dataset.id = String(veterinaria.id);

        const titulo = document.createElement("h3");
        titulo.textContent =
            veterinaria.nombre || "Veterinaria";

        const descripcion = document.createElement("p");
        descripcion.className = "direccion-mapa";

        descripcion.textContent =
            Array.isArray(veterinaria.tipos)
                ? veterinaria.tipos.join(", ")
                : "Servicio veterinario";

        const servicios = document.createElement("div");
        servicios.className = "servicios-mapa";

        const destacados = Array.isArray(
            veterinaria.serviciosDestacados
        )
            ? veterinaria.serviciosDestacados
            : [];

        destacados.forEach((servicio) => {
            const etiqueta = document.createElement("span");
            etiqueta.className = "servicio-mapa";

            etiqueta.textContent =
                typeof servicio === "string"
                    ? servicio
                    : servicio.nombre || "Servicio";

            servicios.appendChild(etiqueta);
        });

        if (veterinaria.urgencias24h) {
            const etiqueta = document.createElement("span");

            etiqueta.className = "servicio-mapa urgencias";
            etiqueta.textContent = "Urgencias 24 h";

            servicios.appendChild(etiqueta);
        }

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
            descripcion,
            servicios,
            acciones
        );

        return tarjeta;
    }

    // =====================================
    // CREAR MARCADORES
    // =====================================

    function agregarMarcador(veterinaria) {
        const lat = Number(veterinaria.lat);
        const lng = Number(veterinaria.lng);

        if (
            veterinaria.lat == null ||
            veterinaria.lng == null ||
            !Number.isFinite(lat) ||
            !Number.isFinite(lng) ||
            lat < -90 ||
            lat > 90 ||
            lng < -180 ||
            lng > 180
        ) {
            return;
        }

        const marcador = L.marker([lat, lng]);

        const popup = document.createElement("div");

        const nombre = document.createElement("strong");
        nombre.textContent =
            veterinaria.nombre || "Veterinaria";

        const descripcion = document.createElement("p");
        descripcion.className = "mb-1";

        descripcion.textContent =
            Array.isArray(veterinaria.tipos)
                ? veterinaria.tipos.join(", ")
                : "Servicio veterinario";

        const enlace = document.createElement("a");

        enlace.href =
            `detalle-veterinaria.html?id=${encodeURIComponent(veterinaria.id)}`;

        enlace.textContent = "Ver detalles";

        popup.append(nombre, descripcion, enlace);

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

    // =====================================
    // MOSTRAR TODAS LAS UBICACIONES
    // =====================================

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

    // =====================================
    // MOSTRAR RESULTADOS
    // =====================================

    function mostrarResultadosMapa(veterinarias) {
        listaMapa.replaceChildren();

        grupoMarcadores.clearLayers();
        marcadoresPorId.clear();

        contadorMapa.textContent =
            `${veterinarias.length} veterinaria(s) mostrada(s)`;

        if (veterinarias.length === 0) {
            mostrarMensajeMapa(
                "No se encontraron veterinarias con los filtros seleccionados."
            );

            return;
        }

        veterinarias.forEach((veterinaria) => {
            listaMapa.appendChild(
                crearTarjetaMapa(veterinaria)
            );

            agregarMarcador(veterinaria);
        });

        mostrarTodasLasUbicaciones();

        // Seleccionar automáticamente la clínica
        // cuando llegamos desde Detalle.
        const idSeleccionado = parametrosURL.get("id");

        if (idSeleccionado) {
            seleccionarVeterinaria(idSeleccionado);
        }
    }

    // =====================================
    // CONSULTAR FASTAPI
    // =====================================

    async function obtenerVeterinariasMapa() {
        const parametros = construirParametros();

        const datos = await apiRequest(
            `/clinicas?${parametros.toString()}`
        );

        if (!Array.isArray(datos)) {
            throw new Error(
                "La API no devolvió una lista válida de clínicas."
            );
        }

        return datos;
    }

    // =====================================
    // OBTENER CLÍNICA POR ID
    // =====================================

    async function obtenerClinicaPorId(id) {
        return await apiRequest(
            `/clinicas/${encodeURIComponent(id)}`
        );
    }

    // =====================================
    // INICIAR MAPA
    // =====================================

    async function iniciarMapa() {
        configurarRegreso();

        contadorMapa.textContent =
            "Cargando veterinarias...";

        mostrarMensajeMapa(
            "Consultando ubicaciones..."
        );

        try {
            const veterinarias =
                await obtenerVeterinariasMapa();

            const idSeleccionado =
                parametrosURL.get("id");

            if (
                idSeleccionado &&
                /^\d+$/.test(idSeleccionado) &&
                !veterinarias.some(
                    (veterinaria) =>
                        String(veterinaria.id) === idSeleccionado
                )
            ) {
                // La clínica podría no estar entre
                // los primeros 50 resultados.
                try {
                    const clinica =
                        await obtenerClinicaPorId(idSeleccionado);

                    if (clinica) {
                        veterinarias.push(clinica);
                    }

                } catch (error) {
                    console.warn(
                        "No se pudo cargar la clínica seleccionada:",
                        error
                    );
                }
            }

            mostrarResultadosMapa(veterinarias);

        } catch (error) {
            console.error(
                "Error al cargar mapa:",
                error
            );

            contadorMapa.textContent =
                "No se pudieron cargar las veterinarias.";

            mostrarMensajeMapa(
                "Ocurrió un error al consultar las ubicaciones. Intenta nuevamente."
            );
        }
    }

    iniciarMapa();
});
