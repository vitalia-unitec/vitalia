
/* =====================================
   VITALIA - LOGIN Y REGISTRO CON FASTAPI
===================================== */

document.addEventListener("DOMContentLoaded", () => {

    // =====================================
    // ELEMENTOS DEL HTML
    // =====================================

    const tabLogin = document.getElementById("tabLogin");
    const tabRegistro = document.getElementById("tabRegistro");

    const loginSection =
        document.getElementById("loginSection");

    const registroSection =
        document.getElementById("registroSection");

    const formLogin =
        document.getElementById("formLogin");

    const formDueno =
        document.getElementById("formRegistroDueno");

    const formClinica =
        document.getElementById("formRegistroClinica");

    const loginMensaje =
        document.getElementById("loginMensaje");

    const registroMensaje =
        document.getElementById("registroMensaje");

    const botonesRol =
        document.querySelectorAll(".rol-boton");

    // =====================================
    // MENSAJES
    // =====================================

    function mostrarMensaje(elemento, texto, tipo = "error") {
        elemento.textContent = texto;
        elemento.className = `auth-mensaje ${tipo}`;
        elemento.hidden = false;
    }

    function limpiarMensajes() {
        loginMensaje.hidden = true;
        registroMensaje.hidden = true;
    }

    function obtenerMensajeError(error) {
        if (error instanceof TypeError) {
            return "No se pudo conectar con el servidor de Vítalia. Verifica que FastAPI esté encendido.";
        }

        return error.message ||
            "Ocurrió un error inesperado.";
    }

    // =====================================
    // CAMBIAR PESTAÑAS
    // =====================================

    function cambiarTab(tab) {
        const esLogin = tab === "login";

        loginSection.hidden = !esLogin;
        registroSection.hidden = esLogin;

        tabLogin.classList.toggle("active", esLogin);
        tabRegistro.classList.toggle("active", !esLogin);

        tabLogin.setAttribute(
            "aria-selected",
            String(esLogin)
        );

        tabRegistro.setAttribute(
            "aria-selected",
            String(!esLogin)
        );

        limpiarMensajes();
    }

    tabLogin.addEventListener("click", () => {
        cambiarTab("login");
    });

    tabRegistro.addEventListener("click", () => {
        cambiarTab("registro");
    });

    // =====================================
    // TIPO DE REGISTRO
    // =====================================

    function cambiarRol(rol) {
        const esDueno = rol === "dueno";

        formDueno.hidden = !esDueno;
        formClinica.hidden = esDueno;

        botonesRol.forEach(boton => {
            const activo = boton.dataset.rol === rol;

            boton.classList.toggle("active", activo);

            boton.setAttribute(
                "aria-pressed",
                String(activo)
            );
        });

        registroMensaje.hidden = true;
    }

    botonesRol.forEach(boton => {
        boton.addEventListener("click", () => {
            cambiarRol(boton.dataset.rol);
        });
    });

    // =====================================
    // VALIDACIONES DEL BACKEND
    // =====================================

    function passwordValida(password) {
        const tieneLongitud = password.length >= 8;
        const tieneLetra =
            /[A-Za-zÁÉÍÓÚáéíóúÑñ]/.test(password);
        const tieneNumero = /\d/.test(password);

        const longitudBytes =
            new TextEncoder().encode(password).length;

        return (
            tieneLongitud &&
            tieneLetra &&
            tieneNumero &&
            longitudBytes <= 72
        );
    }

    function telefonoValido(telefono) {
        return /^\d{10}$/.test(telefono);
    }

    function validarRegistro(nombre, password, telefono) {
        if (nombre.length < 2 || nombre.length > 100) {
            throw new Error(
                "El nombre debe tener entre 2 y 100 caracteres."
            );
        }

        if (!passwordValida(password)) {
            throw new Error(
                "La contraseña debe tener mínimo 8 caracteres, al menos una letra y un número, y no superar 72 bytes."
            );
        }

        if (telefono && !telefonoValido(telefono)) {
            throw new Error(
                "El teléfono debe contener exactamente 10 dígitos."
            );
        }
    }

    // =====================================
    // ESTADO DE BOTONES
    // =====================================

    async function ejecutarConBoton(formulario, operacion) {
        const boton = formulario.querySelector(
            'button[type="submit"]'
        );

        const textoOriginal = boton.innerHTML;

        boton.disabled = true;
        boton.textContent = "Procesando...";

        try {
            await operacion();
        } finally {
            boton.disabled = false;
            boton.innerHTML = textoOriginal;
        }
    }

    // =====================================
    // INICIAR SESIÓN REAL
    // =====================================

    formLogin.addEventListener("submit", async evento => {
        evento.preventDefault();

        limpiarMensajes();

        const email = document
            .getElementById("loginCorreo")
            .value.trim().toLowerCase();

        const password = document
            .getElementById("loginPassword")
            .value;

        if (!email || !password) {
            mostrarMensaje(
                loginMensaje,
                "Completa tu correo y contraseña."
            );
            return;
        }

        await ejecutarConBoton(formLogin, async () => {
            try {
                const usuario = await iniciarSesion(
                    email,
                    password
                );

                mostrarMensaje(
                    loginMensaje,
                    "¡Inicio de sesión exitoso!",
                    "exito"
                );

                if (usuario.rol === "dueno") {
                    window.location.href = "mi-perfil.html";
                } else if (usuario.rol === "clinica") {
                    // Pendiente: panel exclusivo de clínicas.
                    window.location.href = "index.html";
                } else {
                    window.location.href = "index.html";
                }

            } catch (error) {
                mostrarMensaje(
                    loginMensaje,
                    obtenerMensajeError(error)
                );
            }
        });
    });

    // =====================================
    // REGISTRAR DUEÑO
    // =====================================

    formDueno.addEventListener("submit", async evento => {
        evento.preventDefault();

        limpiarMensajes();

        const nombre = document
            .getElementById("duenoNombre")
            .value.trim();

        const telefono = document
            .getElementById("duenoTelefono")
            .value.trim();

        const email = document
            .getElementById("duenoCorreo")
            .value.trim().toLowerCase();

        const password = document
            .getElementById("duenoPassword")
            .value;

        try {
            validarRegistro(nombre, password, telefono);
        } catch (error) {
            mostrarMensaje(
                registroMensaje,
                error.message
            );
            return;
        }

        await ejecutarConBoton(formDueno, async () => {
            try {
                await registrarUsuario({
                    nombre,
                    email,
                    password,
                    telefono: telefono || null,
                    rol: "dueno"
                });

                formDueno.reset();
                cambiarTab("login");

                document.getElementById(
                    "loginCorreo"
                ).value = email;

                mostrarMensaje(
                    loginMensaje,
                    "¡Cuenta registrada! Ahora puedes iniciar sesión.",
                    "exito"
                );

            } catch (error) {
                mostrarMensaje(
                    registroMensaje,
                    obtenerMensajeError(error)
                );
            }
        });
    });

    // =====================================
    // REGISTRAR CLÍNICA
    // =====================================

    formClinica.addEventListener("submit", async evento => {
        evento.preventDefault();

        limpiarMensajes();

        const nombre = document
            .getElementById("clinicaNombre")
            .value.trim();

        const responsable = document
            .getElementById("clinicaResponsable")
            .value.trim();

        const direccion = document
            .getElementById("clinicaDireccion")
            .value.trim();

        const telefono = document
            .getElementById("clinicaTelefono")
            .value.trim();

        const urgencias24h = document
            .getElementById("clinicaUrgencias")
            .checked;

        const email = document
            .getElementById("clinicaCorreo")
            .value.trim().toLowerCase();

        const password = document
            .getElementById("clinicaPassword")
            .value;

        try {
            validarRegistro(nombre, password, telefono);
        } catch (error) {
            mostrarMensaje(
                registroMensaje,
                error.message
            );
            return;
        }

        await ejecutarConBoton(formClinica, async () => {
            try {
                // El endpoint de registro crea la cuenta
                // con rol "clinica". Los datos adicionales
                // de la clínica requieren otro endpoint.
                await registrarUsuario({
                    nombre,
                    email,
                    password,
                    telefono: telefono || null,
                    rol: "clinica"
                });

                console.info(
                    "Datos de clínica pendientes de registrar:",
                    {
                        responsable,
                        direccion,
                        urgencias24h
                    }
                );

                formClinica.reset();
                cambiarTab("login");

                document.getElementById(
                    "loginCorreo"
                ).value = email;

                mostrarMensaje(
                    loginMensaje,
                    "¡Cuenta de clínica registrada! Inicia sesión para continuar. Los datos del establecimiento se completarán en el módulo de negocios.",
                    "exito"
                );

            } catch (error) {
                mostrarMensaje(
                    registroMensaje,
                    obtenerMensajeError(error)
                );
            }
        });
    });

        // =====================================
    // PESTAÑA INICIAL
    // =====================================

    const parametros = new URLSearchParams(
        window.location.search
    );

    if (parametros.get("tab") === "registro") {
        cambiarTab("registro");

        if (parametros.get("rol") === "clinica") {
            cambiarRol("clinica");
        }
    } else {
        cambiarTab("login");
    }

});
