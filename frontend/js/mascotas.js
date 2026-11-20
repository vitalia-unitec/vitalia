
/* =========================================
   VITALIA - MIS MASCOTAS CON FASTAPI
========================================= */

document.addEventListener("DOMContentLoaded", () => {

    // =====================================
    // ELEMENTOS HTML
    // =====================================

    const vistaInvitado =
        document.getElementById("vistaInvitado");

    const vistaMascotas =
        document.getElementById("vistaMascotas");

    const listaMascotas =
        document.getElementById("listaMascotas");

    const estadoSinMascotas =
        document.getElementById("estadoSinMascotas");

    const formMascota =
        document.getElementById("formMascota");

    const mensajeMascotas =
        document.getElementById("mensajeMascotas");

    let mascotas = [];

    // =====================================
    // MENSAJES
    // =====================================

    function mostrarMensaje(texto, tipo = "text-danger") {
        if (!mensajeMascotas) return;

        mensajeMascotas.textContent = texto;
        mensajeMascotas.className = `mt-3 ${tipo}`;
    }

    // =====================================
    // MOSTRAR VISTAS
    // =====================================

    function mostrarInvitado() {
        vistaInvitado.classList.remove("d-none");
        vistaMascotas.classList.add("d-none");
    }

    function mostrarUsuario() {
        vistaInvitado.classList.add("d-none");
        vistaMascotas.classList.remove("d-none");
    }

    // =====================================
    // FORMATO DE EDAD
    // =====================================

    function mostrarEdad(mascota) {
        const anios = mascota.edadAnios;
        const meses = mascota.edadMeses;

        if (anios == null && meses == null) {
            return "Edad no registrada";
        }

        const partes = [];

        if (anios != null) {
            partes.push(
                `${anios} ${anios === 1 ? "año" : "años"}`
            );
        }

        if (meses != null && meses > 0) {
            partes.push(
                `${meses} ${meses === 1 ? "mes" : "meses"}`
            );
        }

        return partes.join(" y ") || "0 meses";
    }

    function mostrarEspecie(especie) {
        const especies = {
            perro: "Perro",
            gato: "Gato",
            ave: "Ave",
            conejo: "Conejo",
            reptil: "Reptil",
            otro: "Otro"
        };

        return especies[especie] || especie;
    }

    // =====================================
    // CREAR TARJETAS
    // =====================================

    function mostrarMascotas() {
        listaMascotas.replaceChildren();

        if (mascotas.length === 0) {
            estadoSinMascotas.classList.remove("d-none");
            return;
        }

        estadoSinMascotas.classList.add("d-none");

        mascotas.forEach(mascota => {
            const columna = document.createElement("div");
            columna.className = "col-12 col-sm-6 col-lg-4";

            const tarjeta = document.createElement("div");
            tarjeta.className = "tarjeta-mascota";

            const avatar = document.createElement("div");
            avatar.className = "avatar-mascota";

            const icono = document.createElement("i");

            if (mascota.especie === "perro") {
                icono.className = "bi bi-heart-fill";
            } else if (mascota.especie === "gato") {
                icono.className = "bi bi-heart";
            } else {
                icono.className = "bi bi-stars";
            }

            avatar.appendChild(icono);

            const nombre = document.createElement("h2");
            nombre.className = "nombre-mascota";
            nombre.textContent = mascota.nombre;

            const detalle = document.createElement("p");
            detalle.className = "detalle-mascota";

            detalle.textContent = [
                mostrarEspecie(mascota.especie),
                mascota.raza || "Raza no registrada",
                mostrarEdad(mascota)
            ].join(" · ");

            const botonCarnet = document.createElement("a");
            botonCarnet.className = "btn-carnet";

            botonCarnet.href =
                `carnet.html?id=${encodeURIComponent(mascota.id)}`;

            const iconoCarnet = document.createElement("i");
            iconoCarnet.className = "bi bi-journal-medical";

            botonCarnet.appendChild(iconoCarnet);
            botonCarnet.append(" Ver carnet");

            tarjeta.append(
                avatar,
                nombre,
                detalle,
                botonCarnet
            );

            columna.appendChild(tarjeta);
            listaMascotas.appendChild(columna);
        });
    }

    // =====================================
    // CONSULTAR MASCOTAS REALES
    // =====================================

    async function cargarMascotas() {
        try {
            mostrarMensaje("Cargando mascotas...", "text-muted");

            const datos = await apiRequest("/me/mascotas", {
                method: "GET"
            });

            mascotas = Array.isArray(datos) ? datos : [];

            mostrarMascotas();
            mostrarMensaje("");

        } catch (error) {
            console.error("Error al cargar mascotas:", error);

            listaMascotas.replaceChildren();
            estadoSinMascotas.classList.add("d-none");

            mostrarMensaje(
                "No fue posible cargar tus mascotas. Comprueba la conexión con el servidor."
            );
        }
    }

    // =====================================
    // CALCULAR EDAD DESDE FECHA
    // =====================================

    function calcularEdadDesdeNacimiento(fechaTexto) {
        if (!fechaTexto) {
            return {
                edadAnios: null,
                edadMeses: null
            };
        }

        const nacimiento = new Date(
            `${fechaTexto}T00:00:00`
        );

        const hoy = new Date();

        if (
            Number.isNaN(nacimiento.getTime()) ||
            nacimiento > hoy
        ) {
            throw new Error(
                "La fecha de nacimiento no es válida."
            );
        }

        let mesesTotales =
            (hoy.getFullYear() - nacimiento.getFullYear()) * 12 +
            (hoy.getMonth() - nacimiento.getMonth());

        if (hoy.getDate() < nacimiento.getDate()) {
            mesesTotales--;
        }

        if (mesesTotales < 0) {
            throw new Error(
                "La fecha de nacimiento no puede ser futura."
            );
        }

        const edadAnios = Math.floor(mesesTotales / 12);
        const edadMeses = mesesTotales % 12;

        if (edadAnios > 40) {
            throw new Error(
                "La edad no puede superar 40 años."
            );
        }

        return {
            edadAnios,
            edadMeses
        };
    }

    // =====================================
    // REGISTRAR MASCOTA
    // =====================================

    formMascota.addEventListener("submit", async evento => {
        evento.preventDefault();

        if (!formMascota.checkValidity()) {
            formMascota.reportValidity();
            return;
        }

        const nombre = document
            .getElementById("nombreMascota")
            .value.trim();

        const especie = document
            .getElementById("especieMascota")
            .value.trim().toLowerCase();

        const raza = document
            .getElementById("razaMascota")
            .value.trim();

        const nacimiento = document
            .getElementById("nacimientoMascota")
            .value;

        const campoSexo = document.getElementById("sexoMascota");

        if (!campoSexo) {
            mostrarMensaje(
                "Falta agregar el campo Sexo al formulario."
            );
            return;
        }

        const sexo = campoSexo.value.trim().toLowerCase();

        if (!["macho", "hembra"].includes(sexo)) {
            mostrarMensaje(
                "Selecciona si tu mascota es macho o hembra."
            );
            return;
        }

        const especiesValidas = [
            "perro", "gato", "ave",
            "conejo", "reptil", "otro"
        ];

        if (!especiesValidas.includes(especie)) {
            mostrarMensaje(
                "Selecciona una especie válida."
            );
            return;
        }

        try {
            const edad = calcularEdadDesdeNacimiento(nacimiento);

            const nuevaMascota = {
                nombre,
                especie,
                raza: raza || null,
                sexo,
                edadAnios: edad.edadAnios,
                edadMeses: edad.edadMeses,
                color: null
            };

            mostrarMensaje(
                "Registrando mascota...",
                "text-muted"
            );

            await apiRequest("/me/mascotas", {
                method: "POST",
                body: JSON.stringify(nuevaMascota)
            });

            formMascota.reset();

            const modalElemento =
                document.getElementById("modalMascota");

            const modal = modalElemento
                ? bootstrap.Modal.getInstance(modalElemento)
                : null;

            modal?.hide();

            await cargarMascotas();

            mostrarMensaje(
                "¡Mascota registrada correctamente!",
                "text-success"
            );

        } catch (error) {
            console.error("Error al registrar mascota:", error);

            mostrarMensaje(
                error.message ||
                "No fue posible registrar la mascota."
            );
        }
    });

    // =====================================
    // INICIAR PÁGINA
    // =====================================

    async function iniciarPagina() {
        const token = typeof obtenerToken === "function"
            ? obtenerToken()
            : null;

        if (!token) {
            mostrarInvitado();
            return;
        }

        try {
            const usuario = await consultarUsuarioActual();

            if (!usuario || usuario.rol !== "dueno") {
                mostrarInvitado();
                return;
            }

            mostrarUsuario();
            await cargarMascotas();

        } catch (error) {
            console.error(
                "Error al verificar la sesión:",
                error
            );

            mostrarInvitado();
        }
    }

    iniciarPagina();

});
