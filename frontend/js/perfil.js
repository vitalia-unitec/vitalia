
/* =========================================
   VITALIA - MI PERFIL
========================================= */

document.addEventListener("DOMContentLoaded", () => {

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
    // CONFIGURACIÓN
    // =====================================

    const MODO_DEMO = true;

    const usuarioDemo = {
        nombre: "María",
        apellido: "García",
        correo: "maria@ejemplo.com",
        telefono: "5512345678"
    };

    // =====================================
    // VISTA DE INVITADO
    // =====================================

    function mostrarInvitado() {

        vistaInvitado.classList.remove("d-none");

        perfilUsuario.classList.add("d-none");

        if (typeof limpiarCarnetsPerfil === "function") {
            limpiarCarnetsPerfil();
        }
    }

    // =====================================
    // VISTA DE USUARIO
    // =====================================

    function mostrarUsuario(usuario) {

        vistaInvitado.classList.add("d-none");

        perfilUsuario.classList.remove("d-none");

        document.getElementById("nombre").value =
            usuario.nombre || "";

        document.getElementById("apellido").value =
            usuario.apellido || "";

        document.getElementById("correo").value =
            usuario.correo || "";

        document.getElementById("telefono").value =
            usuario.telefono || "";

        // Mostrar carnets de demostración
        if (MODO_DEMO) {

            if (
                typeof cargarCarnetsDemoPerfil === "function"
            ) {
                cargarCarnetsDemoPerfil();
            }

        } else {

            // Pendiente: obtener mascotas reales
            // desde el backend.

            if (
                typeof limpiarCarnetsPerfil === "function"
            ) {
                limpiarCarnetsPerfil();
            }
        }
    }

    // =====================================
    // CONSULTAR SESIÓN
    // =====================================

    async function cargarSesion() {

        if (MODO_DEMO) {

            const sesion =
                typeof obtenerUsuarioActual === "function"
                    ? obtenerUsuarioActual()
                    : null;

            if (sesion) {

                mostrarUsuario({
                    ...usuarioDemo,
                    ...sesion
                });

            } else {

                mostrarInvitado();
            }

            return;
        }

        // Endpoint provisional.
        // Confirmar con backend.

        try {

            const respuesta = await fetch(
                "/api/usuarios/me",
                {
                    method: "GET",
                    credentials: "include",
                    headers: {
                        "Accept": "application/json"
                    }
                }
            );

            if (
                respuesta.status === 401 ||
                respuesta.status === 403
            ) {
                mostrarInvitado();
                return;
            }

            if (!respuesta.ok) {
                throw new Error(
                    "No se pudo consultar la sesión."
                );
            }

            const usuario = await respuesta.json();

            mostrarUsuario(usuario);

        } catch (error) {

            console.error(
                "Error al consultar sesión:",
                error
            );

            mostrarInvitado();
        }
    }

    // =====================================
    // GUARDAR INFORMACIÓN PERSONAL
    // =====================================

    formPerfil.addEventListener(
        "submit",
        async (evento) => {

            evento.preventDefault();

            mensajePerfil.textContent = "";

            mensajePerfil.className =
                "small mt-3 mb-0";

            if (!formPerfil.checkValidity()) {

                formPerfil.reportValidity();
                return;
            }

            const datosActualizados = {

                nombre:
                    document.getElementById("nombre")
                        .value.trim(),

                apellido:
                    document.getElementById("apellido")
                        .value.trim(),

                telefono:
                    document.getElementById("telefono")
                        .value.trim()

            };

            // Modo demostración
            if (MODO_DEMO) {

                mensajePerfil.textContent =
                    "Vista de demostración: los cambios no se han guardado.";

                mensajePerfil.classList.add(
                    "text-muted"
                );

                console.log(
                    "Datos de prueba:",
                    datosActualizados
                );

                return;
            }

            // Backend real (ruta provisional)
            try {

                const respuesta = await fetch(
                    "/api/usuarios/me",
                    {
                        method: "PATCH",
                        credentials: "include",
                        headers: {
                            "Content-Type": "application/json",
                            "Accept": "application/json"
                        },
                        body: JSON.stringify(
                            datosActualizados
                        )
                    }
                );

                if (
                    respuesta.status === 401 ||
                    respuesta.status === 403
                ) {
                    mostrarInvitado();
                    return;
                }

                if (!respuesta.ok) {
                    throw new Error(
                        "No se pudieron guardar los cambios."
                    );
                }

                mensajePerfil.textContent =
                    "Tus cambios se guardaron correctamente.";

                mensajePerfil.classList.add(
                    "text-success"
                );

            } catch (error) {

                console.error(
                    "Error al actualizar perfil:",
                    error
                );

                mensajePerfil.textContent =
                    "No fue posible guardar los cambios. Intenta nuevamente.";

                mensajePerfil.classList.add(
                    "text-danger"
                );
            }
        }
    );

    // =====================================
    // CERRAR SESIÓN
    // =====================================

    btnCerrarSesion.addEventListener(
        "click",
        async () => {

            if (MODO_DEMO) {

                cerrarSesionDemo();
                return;
            }

            // Endpoint provisional de backend
            try {

                const respuesta = await fetch(
                    "/api/auth/logout",
                    {
                        method: "POST",
                        credentials: "include"
                    }
                );

                if (!respuesta.ok) {
                    throw new Error(
                        "No se pudo cerrar sesión."
                    );
                }

                window.location.href = "index.html";

            } catch (error) {

                console.error(
                    "Error al cerrar sesión:",
                    error
                );

                alert(
                    "No fue posible cerrar sesión. Intenta nuevamente."
                );
            }
        }
    );

    // =====================================
    // INICIAR PÁGINA
    // =====================================

    cargarSesion();

});
