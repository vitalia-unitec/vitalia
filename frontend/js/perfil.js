
/* =========================================
   VITALIA - MI PERFIL CON FASTAPI
========================================= */

document.addEventListener("DOMContentLoaded", () => {

    // =====================================
    // ELEMENTOS DEL HTML
    // =====================================

    const vistaInvitado =
        document.getElementById("vistaInvitado");

    const perfilUsuario =
        document.getElementById("perfilUsuario");

    const formPerfil =
        document.getElementById("formPerfil");

    const mensajePerfil =
        document.getElementById("mensajePerfil");

    const btnCerrarSesion =
        document.getElementById("btnCerrarSesion");

    // =====================================
    // MENSAJES
    // =====================================

    function mostrarMensaje(texto, tipo = "text-muted") {
        if (!mensajePerfil) return;

        mensajePerfil.textContent = texto;
        mensajePerfil.className =
            `small mt-3 mb-0 ${tipo}`;
    }

    // =====================================
    // VISTA DE INVITADO
    // =====================================

    function mostrarInvitado() {
        if (vistaInvitado) {
            vistaInvitado.classList.remove("d-none");
        }

        if (perfilUsuario) {
            perfilUsuario.classList.add("d-none");
        }
    }

    // =====================================
    // VISTA DE USUARIO
    // =====================================

    function mostrarUsuario(usuario) {
        if (vistaInvitado) {
            vistaInvitado.classList.add("d-none");
        }

        if (perfilUsuario) {
            perfilUsuario.classList.remove("d-none");
        }

        const nombreCompleto =
            (usuario.nombre || "").trim();

        const partesNombre =
            nombreCompleto.split(/\s+/);

        const primerNombre =
            partesNombre.shift() || "";

        const apellidos =
            partesNombre.join(" ");

        const nombre =
            document.getElementById("nombre");

        const apellido =
            document.getElementById("apellido");

        const correo =
            document.getElementById("correo");

        const telefono =
            document.getElementById("telefono");

        if (nombre) {
            nombre.value = primerNombre;
        }

        if (apellido) {
            apellido.value = apellidos;
        }

        if (correo) {
            correo.value = usuario.email || "";
        }

        if (telefono) {
            telefono.value = usuario.telefono || "";
        }

        // Los carnets se administran por separado
        // desde carnet-preview-perfil.js.
        // No eliminamos ni sobrescribimos sus tarjetas.
    }

    // =====================================
    // CONSULTAR SESIÓN REAL
    // =====================================

    async function cargarSesion() {
        const token =
            typeof obtenerToken === "function"
                ? obtenerToken()
                : null;

        if (!token) {
            mostrarInvitado();
            return;
        }

        try {
            const usuario =
                await consultarUsuarioActual();

            if (!usuario) {
                mostrarInvitado();
                return;
            }

            mostrarUsuario(usuario);

        } catch (error) {
            console.error(
                "Error al consultar el perfil:",
                error
            );

            mostrarInvitado();

            mostrarMensaje(
                "No fue posible verificar tu sesión.",
                "text-danger"
            );
        }
    }

    // =====================================
    // GUARDAR INFORMACIÓN PERSONAL
    // =====================================

    if (formPerfil) {
        formPerfil.addEventListener(
            "submit",
            async (evento) => {
                evento.preventDefault();

                mostrarMensaje("");

                if (!formPerfil.checkValidity()) {
                    formPerfil.reportValidity();
                    return;
                }

                // Pendiente de confirmar el endpoint
                // de actualización del perfil.

                mostrarMensaje(
                    "La consulta de tu perfil está conectada. La edición estará disponible cuando integremos el endpoint correspondiente.",
                    "text-muted"
                );
            }
        );
    }

    // =====================================
    // CERRAR SESIÓN
    // =====================================

    if (btnCerrarSesion) {
        btnCerrarSesion.addEventListener(
            "click",
            () => {
                cerrarSesionDemo();
            }
        );
    }

    // =====================================
    // INICIAR PÁGINA
    // =====================================

    cargarSesion();

});
