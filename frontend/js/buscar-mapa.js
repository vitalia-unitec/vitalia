/* =========================================
   VITALIA - MAPA INTEGRADO EN BUSCAR
========================================= */

const mapaBusquedaVitalia = (() => {

    let mapa = null;
    let grupoMarcadores = null;

    const marcadores = new Map();

    function coordenadasValidas(veterinaria) {

        if (
            veterinaria.lat == null ||
            veterinaria.lng == null ||
            veterinaria.lat === "" ||
            veterinaria.lng === ""
        ) {
            return false;
        }

        const lat = Number(veterinaria.lat);
        const lng = Number(veterinaria.lng);

        return (
            Number.isFinite(lat) &&
            Number.isFinite(lng) &&
            lat >= -90 &&
            lat <= 90 &&
            lng >= -180 &&
            lng <= 180
        );
    }

    function mostrarMensaje(mensaje) {

        const estado = document.getElementById(
            "estadoMapaBusqueda"
        );

        if (estado) {
            estado.textContent = mensaje;
        }
    }

    function inicializar() {

        if (mapa) {
            return true;
        }

        const contenedor = document.getElementById(
            "mapaBusqueda"
        );

        if (!contenedor || typeof L === "undefined") {

            mostrarMensaje(
                "No fue posible cargar el mapa."
            );

            return false;
        }

        mapa = L.map(contenedor).setView(
            [19.4326, -99.1332],
            11
        );

        L.tileLayer(
            "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
            {
                attribution:
                    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                maxZoom: 19
            }
        ).addTo(mapa);

        grupoMarcadores = L.featureGroup().addTo(mapa);

        if (typeof ResizeObserver !== "undefined") {

            const observador = new ResizeObserver(() => {
                mapa.invalidateSize();
            });

            observador.observe(contenedor);
        }

        return true;
    }

    function centrar() {

        if (!mapa || !grupoMarcadores) {
            return;
        }

        mapa.invalidateSize();

        if (grupoMarcadores.getLayers().length > 0) {

            mapa.fitBounds(
                grupoMarcadores.getBounds(),
                {
                    padding: [30, 30],
                    maxZoom: 15
                }
            );
        }
    }

    function limpiar(mensaje = "Consultando ubicaciones...") {

        if (grupoMarcadores) {
            grupoMarcadores.clearLayers();
        }

        marcadores.clear();

        mostrarMensaje(mensaje);
    }

    function seleccionar(id, desplazar = false) {

        const marcador = marcadores.get(String(id));

        if (!marcador || !mapa) {
            return;
        }

        mapa.invalidateSize();

        mapa.setView(
            marcador.getLatLng(),
            16,
            { animate: true }
        );

        marcador.openPopup();

        document.querySelectorAll(".tarjeta-veterinaria")
            .forEach(tarjeta => {

                tarjeta.classList.toggle(
                    "seleccionada",
                    tarjeta.dataset.id === String(id)
                );

            });

        if (desplazar && window.innerWidth < 992) {

            document.getElementById("mapaBusqueda")
                ?.scrollIntoView({
                    behavior: "smooth",
                    block: "center"
                });
        }
    }

    function agregarMarcador(veterinaria) {

        if (!coordenadasValidas(veterinaria)) {
            return;
        }

        const marcador = L.marker([
            Number(veterinaria.lat),
            Number(veterinaria.lng)
        ]);

        const popup = document.createElement("div");

        const nombre = document.createElement("strong");
        nombre.textContent = veterinaria.nombre;

        const descripcion = document.createElement("p");
        descripcion.className = "mb-2";

        descripcion.textContent =
            veterinaria.tipos?.join(", ") ||
            "Servicio veterinario";

        const enlace = document.createElement("a");

        enlace.href =
            `detalle-veterinaria.html?id=${encodeURIComponent(veterinaria.id)}`;

        enlace.textContent = "Ver detalles";

        popup.append(nombre, descripcion, enlace);

        marcador.bindPopup(popup);

        marcador.on("click", () => {
            seleccionar(veterinaria.id);
        });

        marcador.addTo(grupoMarcadores);

        marcadores.set(
            String(veterinaria.id),
            marcador
        );
    }

    function actualizar(veterinarias, coordenadas = null) {

        if (!inicializar()) {
            return;
        }

        limpiar();

        veterinarias.forEach(agregarMarcador);

        if (marcadores.size > 0) {

            mostrarMensaje(
                `${marcadores.size} de ${veterinarias.length} clínicas ubicadas en el mapa.`
            );

            requestAnimationFrame(centrar);

        } else {

            mostrarMensaje(
                "No hay clínicas con coordenadas para mostrar."
            );

            mapa.setView(
                coordenadas
                    ? [coordenadas.lat, coordenadas.lng]
                    : [19.4326, -99.1332],
                coordenadas ? 13 : 11
            );
        }
    }

    return {
        inicializar,
        actualizar,
        limpiar,
        centrar,
        seleccionar,
        coordenadasValidas
    };

})();
