
const AUTH_TOKEN_KEY = "vitalia_token";
const AUTH_USER_KEY = "vitalia_usuario";

function obtenerToken() {
    return sessionStorage.getItem(AUTH_TOKEN_KEY);
}

function obtenerUsuarioActual() {
    try {
        const datos = sessionStorage.getItem(AUTH_USER_KEY);
        return datos ? JSON.parse(datos) : null;
    } catch (error) {
        console.error("Error al leer el usuario:", error);
        return null;
    }
}

function guardarSesion(sesion) {
    if (!sesion?.token || !sesion?.usuario) {
        throw new Error("La respuesta de inicio de sesión no es válida.");
    }

    sessionStorage.setItem(AUTH_TOKEN_KEY, sesion.token);
    sessionStorage.setItem(
        AUTH_USER_KEY,
        JSON.stringify(sesion.usuario)
    );

    actualizarEncabezadoAuth();
}

async function iniciarSesion(email, password) {
    const sesion = await apiRequest("/auth/login", {
        method: "POST",
        body: JSON.stringify({
            email: email.trim().toLowerCase(),
            password
        })
    });

    guardarSesion(sesion);
    return sesion.usuario;
}

async function registrarUsuario(datos) {
    return await apiRequest("/auth/registro", {
        method: "POST",
        body: JSON.stringify(datos)
    });
}

async function consultarUsuarioActual() {
    if (!obtenerToken()) {
        return null;
    }

    const usuario = await apiRequest("/auth/me", {
        method: "GET"
    });

    sessionStorage.setItem(
        AUTH_USER_KEY,
        JSON.stringify(usuario)
    );

    actualizarEncabezadoAuth();
    return usuario;
}

function cerrarSesionDemo() {
    sessionStorage.removeItem(AUTH_TOKEN_KEY);
    sessionStorage.removeItem(AUTH_USER_KEY);
    actualizarEncabezadoAuth();
    window.location.href = "index.html";
}

function actualizarEncabezadoAuth() {
    const usuario = obtenerUsuarioActual();
    const autenticado = Boolean(obtenerToken() && usuario);

    document.querySelectorAll(".auth-invitado").forEach(
        elemento => {
            elemento.hidden = autenticado;
        }
    );

    document.querySelectorAll(".auth-usuario").forEach(
        elemento => {
            elemento.hidden = !autenticado;
        }
    );

    document.querySelectorAll(".btn-cerrar-sesion").forEach(
        boton => {
            boton.onclick = cerrarSesionDemo;
        }
    );
}

document.addEventListener(
    "DOMContentLoaded",
    actualizarEncabezadoAuth
);
