
/* =====================================
   VITALIA - LOGIN Y REGISTRO
===================================== */

document.addEventListener("DOMContentLoaded", () => {

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

    function mostrarMensaje(elemento, texto, tipo) {

        elemento.textContent = texto;

        elemento.className =
            `auth-mensaje ${tipo}`;

        elemento.hidden = false;
    }

    function limpiarMensajes() {
        loginMensaje.hidden = true;
        registroMensaje.hidden = true;
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
    // VALIDAR CONTRASEÑA
    // =====================================

    function passwordValida(password) {

        return /^(?=.*[A-Z])(?=.*\d).{6,}$/
            .test(password);
    }

    // =====================================
    // INICIAR SESIÓN DEMO
    // =====================================

    formLogin.addEventListener("submit", evento => {

        evento.preventDefault();

        const correo = document
            .getElementById("loginCorreo")
            .value.trim();

        const password = document
            .getElementById("loginPassword")
            .value;

        if (!correo || !password) {
            mostrarMensaje(
                loginMensaje,
                "Completa todos los campos.",
                "error"
            );
            return;
        }

        // Solo demostración visual.
        // No verifica credenciales reales.

        if (typeof iniciarSesionDemo !== "function") {

            mostrarMensaje(
                loginMensaje,
                "No se pudo iniciar la demostración.",
                "error"
            );
            return;
        }

        const nombre = correo
            .split("@")[0]
            .replace(/[._-]+/g, " ");

        iniciarSesionDemo({
            nombre: nombre || "Usuario",
            apellido: "",
            correo: correo,
            telefono: "",
            rol: "dueno"
        });

        window.location.href = "mi-perfil.html";
    });

    // =====================================
    // REGISTRAR DUEÑO - DEMO
    // =====================================

    formDueno.addEventListener("submit", evento => {

        evento.preventDefault();

        const nombre = document
            .getElementById("duenoNombre")
            .value.trim();

        const password = document
            .getElementById("duenoPassword")
            .value;

        if (!passwordValida(password)) {

            mostrarMensaje(
                registroMensaje,
                "La contraseña necesita mínimo 6 caracteres, una mayúscula y un número.",
                "error"
            );
            return;
        }

        mostrarMensaje(
            registroMensaje,
            `Formulario de ${nombre} validado. El registro real estará disponible al conectar el backend.`,
            "exito"
        );

        // No almacenar contraseñas ni crear
        // cuentas ficticias en localStorage.
    });

    // =====================================
    // REGISTRAR CLÍNICA - DEMO
    // =====================================

    formClinica.addEventListener("submit", evento => {

        evento.preventDefault();

        const password = document
            .getElementById("clinicaPassword")
            .value;

        if (!passwordValida(password)) {

            mostrarMensaje(
                registroMensaje,
                "La contraseña necesita mínimo 6 caracteres, una mayúscula y un número.",
                "error"
            );
            return;
        }

        mostrarMensaje(
            registroMensaje,
            "Formulario de veterinaria validado. El registro real estará disponible al conectar el backend.",
            "exito"
        );
    });

    // =====================================
    // PESTAÑA INICIAL
    // =====================================

    const parametros =
        new URLSearchParams(window.location.search);

    if (parametros.get("tab") === "registro") {
        cambiarTab("registro");
    } else {
        cambiarTab("login");
    }

});
