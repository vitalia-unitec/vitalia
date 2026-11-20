
/* =========================================
   VITALIA - CARNET DIGITAL
========================================= */

document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("formCarnet");
    const foto = document.getElementById("fotoMascota");
    const inputFoto = document.getElementById("inputFotoMascota");

    const titulo = document.getElementById("tituloCarnet");
    const estado = document.getElementById("estadoCarnet");
    const mensaje = document.getElementById("mensajeCarnet");

    const btnGuardar = document.getElementById("btnGuardarCarnet");
    const btnCrear = document.getElementById("btnCrearCarnet");
    const btnConsultar = document.getElementById("btnConsultarCarnet");
    const btnEditar = document.getElementById("btnEditarCarnet");
    const btnBorrar = document.getElementById("btnBorrarCarnet");
    const btnCompartir = document.getElementById("btnCompartirCarnet");

    const campos = {
        nombre: document.getElementById("mascotaNombre"),
        sexo: document.getElementById("mascotaSexo"),
        especie: document.getElementById("mascotaEspecie"),
        edad: document.getElementById("mascotaEdad"),
        raza: document.getElementById("mascotaRaza"),
        color: document.getElementById("mascotaColor")
    };

    const FOTO_DEFAULT = "assets/img/logo-vitalia.png";

    // =====================================
    // DATOS DEMO
    // =====================================

    const mascotasDemo = {
        "1": {
            nombre: "Luna",
            sexo: "Hembra",
            especie: "Perro",
            edad: "3 años",
            raza: "Golden Retriever",
            color: "Dorado",
            foto: "https://images.unsplash.com/photo-1552053831-71594a27632d?auto=format&fit=crop&w=400&q=80"
        },
        "2": {
            nombre: "Milo",
            sexo: "Macho",
            especie: "Gato",
            edad: "2 años",
            raza: "Doméstico",
            color: "Gris",
            foto: "https://images.unsplash.com/photo-1573865526739-10659fec78a5?auto=format&fit=crop&w=400&q=80"
        }
    };

    // =====================================
    // IDENTIFICAR MASCOTA Y USUARIO
    // =====================================

    const parametros = new URLSearchParams(
        window.location.search
    );

    const idMascota = parametros.get("id") || "1";

    const usuario =
        typeof obtenerUsuarioActual === "function"
            ? obtenerUsuarioActual()
            : null;

    const usuarioId = usuario?.correo || "demo";

    const claveAlmacenamiento =
        `vitalia_carnet_${encodeURIComponent(usuarioId)}_${encodeURIComponent(idMascota)}`;

    let modoActual = "consulta";
    let fotoTemporal = null;

    // =====================================
    // MENSAJES
    // =====================================

    function mostrarMensaje(texto, tipo = "success") {

        mensaje.textContent = texto;

        mensaje.className = `alert alert-${tipo}`;

        mensaje.hidden = false;
    }

    function limpiarMensaje() {
        mensaje.hidden = true;
    }

    // =====================================
    // OBTENER DATOS
    // =====================================

    function obtenerDatosGuardados() {

        try {
            const guardado = localStorage.getItem(
                claveAlmacenamiento
            );

            return guardado
                ? JSON.parse(guardado)
                : null;

        } catch (error) {

            console.error(
                "Error al consultar carnet:",
                error
            );

            return null;
        }
    }

    function obtenerMascotaInicial() {

        const guardado = obtenerDatosGuardados();

        if (guardado) return guardado;

        if (mascotasDemo[idMascota]) {
            return { ...mascotasDemo[idMascota] };
        }

        return {
            nombre: "",
            sexo: "",
            especie: "",
            edad: "",
            raza: "",
            color: "",
            foto: FOTO_DEFAULT
        };
    }

    // =====================================
    // CARGAR FORMULARIO
    // =====================================

    function cargarMascota(datos) {

        campos.nombre.value = datos.nombre || "";
        campos.sexo.value = datos.sexo || "";
        campos.especie.value = datos.especie || "";
        campos.edad.value = datos.edad || "";
        campos.raza.value = datos.raza || "";
        campos.color.value = datos.color || "";

        foto.src = datos.foto || FOTO_DEFAULT;
        fotoTemporal = datos.foto || FOTO_DEFAULT;

        actualizarTitulo();
    }

    function actualizarTitulo() {

        const nombre = campos.nombre.value.trim();

        titulo.textContent = nombre
            ? `Carnet de ${nombre}`
            : "Carnet de mi mascota";
    }

    // =====================================
    // CAMBIAR MODO
    // =====================================

    function establecerModo(modo) {

        modoActual = modo;

        const editable = modo !== "consulta";

        Object.values(campos).forEach(campo => {
            campo.disabled = !editable;
        });

        inputFoto.disabled = !editable;

        btnGuardar.hidden = !editable;

        if (modo === "consulta") {
            estado.textContent = "Modo consulta";
        } else if (modo === "edicion") {
            estado.textContent = "Modo edición";
        } else {
            estado.textContent = "Nuevo carnet";
        }
    }

    // =====================================
    // CREAR CARNET
    // =====================================

    btnCrear.addEventListener("click", () => {

        // Crear abre un formulario nuevo.
        // No sobrescribe el carnet existente
        // hasta que se presione Guardar.

        form.reset();

        foto.src = FOTO_DEFAULT;
        fotoTemporal = FOTO_DEFAULT;

        establecerModo("creacion");

        actualizarTitulo();

        mostrarMensaje(
            "Completa los datos para crear un carnet de demostración.",
            "info"
        );
    });

    // =====================================
    // CONSULTAR
    // =====================================

    btnConsultar.addEventListener("click", () => {

        cargarMascota(obtenerMascotaInicial());

        establecerModo("consulta");

        mostrarMensaje(
            "Estás consultando el carnet.",
            "info"
        );
    });

    // =====================================
    // EDITAR
    // =====================================

    btnEditar.addEventListener("click", () => {

        establecerModo("edicion");

        mostrarMensaje(
            "Puedes modificar los datos y guardar los cambios.",
            "info"
        );
    });

    // =====================================
    // CAMBIAR FOTO
    // =====================================

    inputFoto.addEventListener("change", evento => {

        const archivo = evento.target.files[0];

        if (!archivo) return;

        if (!archivo.type.startsWith("image/")) {
            mostrarMensaje(
                "Selecciona un archivo de imagen válido.",
                "danger"
            );
            return;
        }

        if (archivo.size > 1024 * 1024) {
            mostrarMensaje(
                "Para esta demostración, la imagen debe pesar menos de 1 MB.",
                "warning"
            );
            return;
        }

        const lector = new FileReader();

        lector.onload = () => {

            fotoTemporal = lector.result;
            foto.src = fotoTemporal;
        };

        lector.readAsDataURL(archivo);
    });

    // =====================================
    // GUARDAR CARNET
    // =====================================

    form.addEventListener("submit", evento => {

        evento.preventDefault();

        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const datos = {
            nombre: campos.nombre.value.trim(),
            sexo: campos.sexo.value,
            especie: campos.especie.value,
            edad: campos.edad.value.trim(),
            raza: campos.raza.value.trim(),
            color: campos.color.value.trim(),
            foto: fotoTemporal || FOTO_DEFAULT
        };

        try {

            localStorage.setItem(
                claveAlmacenamiento,
                JSON.stringify(datos)
            );

            establecerModo("consulta");

            actualizarTitulo();

            mostrarMensaje(
                "Carnet de demostración guardado en este navegador.",
                "success"
            );

        } catch (error) {

            console.error(
                "No se pudo guardar el carnet:",
                error
            );

            mostrarMensaje(
                "No se pudo guardar. Verifica el espacio disponible del navegador.",
                "danger"
            );
        }
    });

    // =====================================
    // BORRAR CARNET
    // =====================================

    btnBorrar.addEventListener("click", () => {

        const nombre =
            campos.nombre.value.trim() || "esta mascota";

        const confirmar = window.confirm(
            `¿Quieres borrar el carnet de ${nombre} de esta demostración?`
        );

        if (!confirmar) return;

        localStorage.removeItem(claveAlmacenamiento);

        form.reset();

        foto.src = FOTO_DEFAULT;
        fotoTemporal = FOTO_DEFAULT;

        establecerModo("creacion");

        actualizarTitulo();

        mostrarMensaje(
            "Los cambios guardados de este carnet se eliminaron del navegador. El ejemplo original seguirá disponible al volver a abrirlo.",
            "warning"
        );
    });

    // =====================================
    // COMPARTIR POR WHATSAPP
    // =====================================

    btnCompartir.addEventListener("click", () => {

        const nombre =
            campos.nombre.value.trim() || "mi mascota";

        const especie = campos.especie.value;
        const raza = campos.raza.value.trim();
        const edad = campos.edad.value.trim();

        const texto = [
            "🐾 Carnet de mascota - Vitalia",
            `Nombre: ${nombre}`,
            `Especie: ${especie}`,
            `Raza: ${raza}`,
            `Edad: ${edad}`
        ].join("\n");

        const url =
            `https://api.whatsapp.com/send?text=${encodeURIComponent(texto)}`;

        window.open(
            url,
            "_blank",
            "noopener,noreferrer"
        );
    });

    // =====================================
    // INICIALIZAR
    // =====================================

    cargarMascota(obtenerMascotaInicial());

    establecerModo("consulta");

    limpiarMensaje();

});
