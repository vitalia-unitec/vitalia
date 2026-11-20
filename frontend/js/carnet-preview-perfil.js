
/* =========================================
   VITALIA - MASCOTAS Y CARNETS EN MI PERFIL
   CONEXIÓN CON FASTAPI
========================================= */

document.addEventListener("DOMContentLoaded", () => {

    const listaMascotas =
        document.getElementById("listaMascotasPerfil");

    const previewCarnets =
        document.getElementById("previewCarnetsPerfil");

    // =====================================
    // VALIDAR SESIÓN
    // =====================================

    function tieneSesion() {
        return typeof obtenerToken === "function" &&
            Boolean(obtenerToken());
    }

    // =====================================
    // FORMATO DE INFORMACIÓN
    // =====================================

    function obtenerEspecie(especie) {
        const especies = {
            perro: "Perro",
            gato: "Gato",
            ave: "Ave",
            conejo: "Conejo",
            reptil: "Reptil",
            otro: "Otro"
        };

        return especies[especie] || "Otra especie";
    }

    function obtenerEdad(mascota) {
        const partes = [];

        if (mascota.edad_anios != null &&
            mascota.edad_anios > 0) {
            partes.push(
                `${mascota.edad_anios} ${
                    mascota.edad_anios === 1
                        ? "año"
                        : "años"
                }`
            );
        }

        if (mascota.edad_meses != null &&
            mascota.edad_meses > 0) {
            partes.push(
                `${mascota.edad_meses} ${
                    mascota.edad_meses === 1
                        ? "mes"
                        : "meses"
                }`
            );
        }

        if (partes.length > 0) {
            return partes.join(" y ");
        }

        if (mascota.edad_anios === 0 ||
            mascota.edad_meses === 0) {
            return "0 meses";
        }

        return "Edad no registrada";
    }

    // =====================================
    // CREAR TARJETA DE MASCOTA
    // =====================================

    function crearTarjeta(mascota) {

        const tarjeta = document.createElement("div");
        tarjeta.className =
            "card border-0 shadow-sm rounded-4 p-3 h-100";

        const contenido = document.createElement("div");
        contenido.className =
            "d-flex flex-wrap align-items-center gap-3";

        // FOTO
        const avatar = document.createElement("div");

        avatar.className =
            "rounded-circle bg-light d-flex align-items-center justify-content-center";

        avatar.style.width = "65px";
        avatar.style.height = "65px";
        avatar.style.flexShrink = "0";
        avatar.style.overflow = "hidden";

        if (mascota.foto_url) {

            const imagen = document.createElement("img");

            imagen.src = mascota.foto_url;
            imagen.alt = `Foto de ${mascota.nombre}`;

            imagen.style.width = "100%";
            imagen.style.height = "100%";
            imagen.style.objectFit = "cover";

            avatar.appendChild(imagen);

        } else {

            const icono = document.createElement("i");

            icono.className =
                "bi bi-heart-fill text-success fs-3";

            avatar.appendChild(icono);
        }

        // INFORMACIÓN
        const informacion = document.createElement("div");

        informacion.className = "flex-grow-1";

        const nombre = document.createElement("h3");
        nombre.className = "h6 fw-bold mb-1";
        nombre.textContent = mascota.nombre;

        const detalle = document.createElement("p");
        detalle.className = "text-muted small mb-0";

        detalle.textContent = [
            obtenerEspecie(mascota.especie),
            mascota.raza || "Raza no registrada",
            obtenerEdad(mascota)
        ].join(" · ");

        informacion.append(nombre, detalle);

        // BOTÓN CARNET
        const enlace = document.createElement("a");

        enlace.href =
            `carnet.html?id=${encodeURIComponent(mascota.id)}`;

        enlace.className =
            "btn btn-outline-success rounded-pill";

        enlace.textContent = "Ver carnet";

        contenido.append(
            avatar,
            informacion,
            enlace
        );

        tarjeta.appendChild(contenido);

        return tarjeta;
    }

    // =====================================
    // MOSTRAR MIS MASCOTAS
    // =====================================

    function mostrarMascotas(mascotas) {

        if (!listaMascotas) return;

        listaMascotas.replaceChildren();

        if (mascotas.length === 0) {

            const contenedor = document.createElement("div");

            contenedor.className =
                "estado-vacio text-center py-4";

            const icono = document.createElement("i");

            icono.className = "bi bi-heart fs-1";

            const texto = document.createElement("p");

            texto.className = "mt-3 mb-2";
            texto.textContent =
                "Aquí aparecerán tus mascotas registradas.";

            const enlace = document.createElement("a");

            enlace.href = "mis-mascotas.html";

            enlace.className =
                "btn btn-outline-success rounded-pill mt-2";

            enlace.textContent = "Agregar mascota";

            contenedor.append(icono, texto, enlace);

            listaMascotas.appendChild(contenedor);

            return;
        }

        const contenedor = document.createElement("div");

        contenedor.className = "d-grid gap-3";

        mascotas.forEach(mascota => {
            contenedor.appendChild(
                crearTarjeta(mascota)
            );
        });

        listaMascotas.appendChild(contenedor);
    }

    // =====================================
    // MOSTRAR CARNETS
    // =====================================

    function mostrarCarnets(mascotas) {

        if (!previewCarnets) return;

        // IMPORTANTE:
        // Solo limpiamos previewCarnetsPerfil.
        // No eliminamos listaCarnetsPerfil.

        previewCarnets.replaceChildren();

        if (mascotas.length === 0) {

            const mensaje = document.createElement("p");

            mensaje.className = "text-muted";
            mensaje.textContent =
                "Todavía no tienes carnets digitales registrados.";

            previewCarnets.appendChild(mensaje);

            return;
        }

        mascotas.forEach(mascota => {

            const columna = document.createElement("div");

            columna.className = "col-md-6";

            columna.appendChild(
                crearTarjeta(mascota)
            );

            previewCarnets.appendChild(columna);
        });
    }

    // =====================================
    // MOSTRAR MENSAJES
    // =====================================

    function mostrarError(texto) {

        [listaMascotas, previewCarnets]
            .filter(Boolean)
            .forEach(contenedor => {

                contenedor.replaceChildren();

                const mensaje = document.createElement("p");

                mensaje.className = "text-danger";
                mensaje.textContent = texto;

                contenedor.appendChild(mensaje);
            });
    }

    // =====================================
    // CONSULTAR MASCOTAS EN FASTAPI
    // =====================================

    async function cargarMascotasPerfil() {

        if (!tieneSesion()) {
            return;
        }

        try {

            const usuario =
                await consultarUsuarioActual();

            if (!usuario || usuario.rol !== "dueno") {
                return;
            }

            const mascotas = await apiRequest(
                "/me/mascotas",
                {
                    method: "GET"
                }
            );

            const lista = Array.isArray(mascotas)
                ? mascotas
                : [];

            mostrarMascotas(lista);
            mostrarCarnets(lista);

        } catch (error) {

            console.error(
                "Error al cargar las mascotas del perfil:",
                error
            );

            mostrarError(
                "No fue posible cargar tus mascotas. Comprueba la conexión con el servidor."
            );
        }
    }

    // =====================================
    // INICIALIZAR
    // =====================================

    cargarMascotasPerfil();

});
