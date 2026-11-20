
/* =========================================
   VITALIA - SESIÓN DE DEMOSTRACIÓN
========================================= */

// IMPORTANTE:
// Esto solo simula una sesión en el frontend.
// No sustituye la autenticación del backend.

const AUTH_DEMO_KEY = "vitalia_usuario_demo";

// =====================================
// OBTENER USUARIO
// =====================================

function obtenerUsuarioActual() {

    try {
        const datos = localStorage.getItem(AUTH_DEMO_KEY);

        return datos ? JSON.parse(datos) : null;

    } catch (error) {

        console.error(
            "Error al consultar la sesión:",
            error
        );

        return null;
    }
}

// =====================================
// INICIAR SESIÓN DEMO
// =====================================

function iniciarSesionDemo(usuario) {

    if (!usuario || !usuario.nombre) {
        return;
    }

    localStorage.setItem(
        AUTH_DEMO_KEY,
        JSON.stringify(usuario)
    );

    actualizarEncabezadoAuth();
}

// =====================================
// CERRAR SESIÓN DEMO
// =====================================

function cerrarSesionDemo() {

    localStorage.removeItem(AUTH_DEMO_KEY);

    window.location.href = "index.html";
}

// =====================================
// ACTUALIZAR ENCABEZADO
// =====================================

function actualizarEncabezadoAuth() {

    const usuario = obtenerUsuarioActual();

    document.querySelectorAll(".auth-invitado")
        .forEach(elemento => {

            elemento.hidden = Boolean(usuario);

        });

    document.querySelectorAll(".auth-usuario")
        .forEach(elemento => {

            elemento.hidden = !usuario;

        });

    document.querySelectorAll(".btn-cerrar-sesion")
        .forEach(boton => {

            boton.onclick = cerrarSesionDemo;

        });
}

// =====================================
// INICIAR
// =====================================

document.addEventListener(
    "DOMContentLoaded",
    actualizarEncabezadoAuth
);
