
/* =========================================
   VITALIA - CARNET DIGITAL CON FASTAPI
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
        edadAnios: document.getElementById("mascotaEdadAnios"),
        edadMeses: document.getElementById("mascotaEdadMeses"),
        raza: document.getElementById("mascotaRaza"),
        color: document.getElementById("mascotaColor")
    };

    const FOTO_DEFAULT = "assets/img/logo-vitalia.png";

    const parametros = new URLSearchParams(
        window.location.search
    );

    let idMascota = parametros.get("id");
    let mascotaActual = null;
    let modoActual = "consulta";
    let fotoSeleccionada = null;
    let fotoTemporalUrl = null;
    let guardando = false;

    // =====================================
    // MENSAJES
    // =====================================

    function mostrarMensaje(texto, tipo = "info") {
        mensaje.textContent = texto;
        mensaje.className = `alert alert-${tipo}`;
        mensaje.hidden = false;
    }

    function limpiarMensaje() {
        mensaje.hidden = true;
        mensaje.textContent = "";
    }

    function obtenerError(error) {
        return error?.message ||
            "No fue posible completar la operación.";
    }

    // =====================================
    // VALIDAR SESIÓN
    // =====================================

    function tieneSesion() {
        return typeof obtenerToken === "function" &&
            Boolean(obtenerToken());
    }

    // =====================================
    // MOSTRAR DATOS
    // =====================================

    function cargarMascota(datos) {
        mascotaActual = datos;

        campos.nombre.value = datos.nombre || "";
        campos.sexo.value = datos.sexo || "";
        campos.especie.value = datos.especie || "";

        campos.edadAnios.value =
            datos.edadAnios ?? "";

        campos.edadMeses.value =
            datos.edadMeses ?? "";

        campos.raza.value = datos.raza || "";
        campos.color.value = datos.color || "";

        limpiarFotoTemporal();

        foto.src = datos.fotoUrl || FOTO_DEFAULT;

        actualizarTitulo();
    }

    function actualizarTitulo() {
        const nombre = campos.nombre.value.trim();

        titulo.textContent = nombre
            ? `Carnet de ${nombre}`
            : "Carnet de mi mascota";
    }

    function limpiarFotoTemporal() {
        if (fotoTemporalUrl) {
            URL.revokeObjectURL(fotoTemporalUrl);
            fotoTemporalUrl = null;
        }

        fotoSeleccionada = null;
        inputFoto.value = "";
    }

    function limpiarFormulario() {
        form.reset();
        mascotaActual = null;
        limpiarFotoTemporal();
        foto.src = FOTO_DEFAULT;
        actualizarTitulo();
    }

    // =====================================
    // MODOS
    // =====================================

    function establecerModo(modo) {
        modoActual = modo;

        const editable = modo !== "consulta";

        Object.values(campos).forEach(campo => {
            campo.disabled = !editable;
        });

        inputFoto.disabled = !editable;
        btnGuardar.hidden = !editable;

        btnBorrar.disabled = !idMascota ||
            modo === "creacion";

        btnCompartir.disabled = !idMascota ||
            modo === "creacion";

        btnEditar.disabled = !idMascota ||
            modo === "creacion";

        if (modo === "consulta") {
            estado.textContent = "Modo consulta";
        } else if (modo === "edicion") {
            estado.textContent = "Modo edición";
        } else {
            estado.textContent = "Nuevo carnet";
        }
    }

    // =====================================
    // CONSULTAR MASCOTA
    // =====================================

    async function consultarMascota() {
        if (!tieneSesion()) {
            mostrarMensaje(
                "Inicia sesión para consultar el carnet.",
                "warning"
            );
            return;
        }

        if (!idMascota) {
            limpiarFormulario();
            establecerModo("creacion");
            mostrarMensaje(
                "Completa los datos para registrar una mascota.",
                "info"
            );
            return;
        }

        try {
            mostrarMensaje(
                "Cargando información del carnet...",
                "info"
            );

            const datos = await apiRequest(
                `/me/mascotas/${encodeURIComponent(idMascota)}`,
                { method: "GET" }
            );

            cargarMascota(datos);
            establecerModo("consulta");
            limpiarMensaje();

        } catch (error) {
            console.error("Error al consultar carnet:", error);

            establecerModo("consulta");

            mostrarMensaje(
                obtenerError(error),
                "danger"
            );
        }
    }

    // =====================================
    // CREAR NUEVO CARNET
    // =====================================

    btnCrear.addEventListener("click", () => {
        idMascota = null;

        window.history.replaceState(
            {},
            "",
            "carnet.html"
        );

        limpiarFormulario();
        establecerModo("creacion");

        mostrarMensaje(
            "Completa los datos para crear un nuevo carnet.",
            "info"
        );
    });

    // =====================================
    // CONSULTAR
    // =====================================

    btnConsultar.addEventListener(
        "click",
        consultarMascota
    );

    // =====================================
    // EDITAR
    // =====================================

    btnEditar.addEventListener("click", () => {
        if (!idMascota || !mascotaActual) {
            mostrarMensaje(
                "Primero debes consultar un carnet existente.",
                "warning"
            );
            return;
        }

        establecerModo("edicion");

        mostrarMensaje(
            "Puedes modificar los datos y guardar los cambios.",
            "info"
        );
    });

    // =====================================
    // SELECCIONAR FOTO
    // =====================================

    inputFoto.addEventListener("change", evento => {
        const archivo = evento.target.files[0];

        if (!archivo) return;

        if (!archivo.type.startsWith("image/")) {
            mostrarMensaje(
                "Selecciona un archivo de imagen válido.",
                "danger"
            );
            inputFoto.value = "";
            return;
        }

        limpiarFotoTemporal();

        fotoSeleccionada = archivo;
        fotoTemporalUrl = URL.createObjectURL(archivo);
        foto.src = fotoTemporalUrl;

        mostrarMensaje(
            "Fotografía seleccionada. Se intentará subir al guardar.",
            "info"
        );
    });

    // =====================================
    // PREPARAR DATOS PARA FASTAPI
    // =====================================

    function numeroOpcional(valor, maximo, etiqueta) {
        if (valor === "") return null;

        const numero = Number(valor);

        if (
            !Number.isInteger(numero) ||
            numero < 0 ||
            numero > maximo
        ) {
            throw new Error(
                `${etiqueta} debe estar entre 0 y ${maximo}.`
            );
        }

        return numero;
    }

    function obtenerDatosFormulario() {
        const datos = {
            nombre: campos.nombre.value.trim(),
            sexo: campos.sexo.value,
            especie: campos.especie.value,
            edadAnios: numeroOpcional(
                campos.edadAnios.value,
                40,
                "La edad en años"
            ),
            edadMeses: numeroOpcional(
                campos.edadMeses.value,
                11,
                "La edad en meses"
            ),
            raza: campos.raza.value.trim() || null,
            color: campos.color.value.trim() || null
        };

        if (!datos.nombre) {
            throw new Error(
                "Debes ingresar el nombre de la mascota."
            );
        }

        if (!["macho", "hembra"].includes(datos.sexo)) {
            throw new Error(
                "Selecciona un sexo válido."
            );
        }

        const especiesValidas = [
            "perro",
            "gato",
            "ave",
            "conejo",
            "reptil",
            "otro"
        ];

        if (!especiesValidas.includes(datos.especie)) {
            throw new Error(
                "Selecciona una especie válida."
            );
        }

        return datos;
    }

    // =====================================
    // SUBIR FOTO
    // =====================================

    async function subirFoto(mascotaId, archivo) {
        const formData = new FormData();
        formData.append("foto", archivo);

        return await apiRequest(
            `/me/mascotas/${encodeURIComponent(mascotaId)}/foto`,
            {
                method: "POST",
                body: formData
            }
        );
    }

    // =====================================
    // GUARDAR CARNET
    // =====================================

    form.addEventListener("submit", async evento => {
        evento.preventDefault();

        if (guardando) return;

        if (!tieneSesion()) {
            mostrarMensaje(
                "Debes iniciar sesión para guardar un carnet.",
                "warning"
            );
            return;
        }

        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        try {
            const datos = obtenerDatosFormulario();

            guardando = true;
            btnGuardar.disabled = true;

            mostrarMensaje(
                "Guardando carnet...",
                "info"
            );

            const esNuevo = modoActual === "creacion" ||
                !idMascota;

            const endpoint = esNuevo
                ? "/me/mascotas"
                : `/me/mascotas/${encodeURIComponent(idMascota)}`;

            const mascotaGuardada = await apiRequest(
                endpoint,
                {
                    method: esNuevo ? "POST" : "PUT",
                    body: JSON.stringify(datos)
                }
            );

            idMascota = String(mascotaGuardada.id);

            window.history.replaceState(
                {},
                "",
                `carnet.html?id=${encodeURIComponent(idMascota)}`
            );

            let errorFoto = null;

            if (fotoSeleccionada) {
                try {
                    await subirFoto(
                        idMascota,
                        fotoSeleccionada
                    );
                } catch (error) {
                    errorFoto = error;
                    console.error(
                        "Error al subir fotografía:",
                        error
                    );
                }
            }

            await consultarMascota();

            if (errorFoto) {
                mostrarMensaje(
                    "Los datos del carnet se guardaron, pero no fue posible subir la fotografía: " +
                    obtenerError(errorFoto),
                    "warning"
                );
            } else {
                mostrarMensaje(
                    "¡Carnet guardado correctamente!",
                    "success"
                );
            }

        } catch (error) {
            console.error("Error al guardar carnet:", error);

            mostrarMensaje(
                obtenerError(error),
                "danger"
            );

        } finally {
            guardando = false;
            btnGuardar.disabled = false;
        }
    });

    // =====================================
    // BORRAR CARNET
    // =====================================

    btnBorrar.addEventListener("click", async () => {
        if (!idMascota || !mascotaActual) {
            mostrarMensaje(
                "No hay un carnet seleccionado para borrar.",
                "warning"
            );
            return;
        }

        const nombre = mascotaActual.nombre ||
            "esta mascota";

        const confirmado = window.confirm(
            `¿Quieres eliminar definitivamente a ${nombre} y su carnet de Vítalia? Esta acción no se puede deshacer.`
        );

        if (!confirmado) return;

        try {
            btnBorrar.disabled = true;

            mostrarMensaje(
                "Eliminando carnet...",
                "info"
            );

            await apiRequest(
                `/me/mascotas/${encodeURIComponent(idMascota)}`,
                { method: "DELETE" }
            );

            window.location.href = "mis-mascotas.html";

        } catch (error) {
            console.error("Error al borrar carnet:", error);

            mostrarMensaje(
                obtenerError(error),
                "danger"
            );

            btnBorrar.disabled = false;
        }
    });

    // =====================================
    // COMPARTIR POR WHATSAPP
    // =====================================

    btnCompartir.addEventListener("click", () => {
        if (!mascotaActual || !idMascota) {
            mostrarMensaje(
                "Primero guarda o consulta un carnet.",
                "warning"
            );
            return;
        }

        const mascota = mascotaActual;

        const edad = [];

        if (mascota.edadAnios != null) {
            edad.push(
                `${mascota.edadAnios} años`
            );
        }

        if (mascota.edadMeses != null) {
            edad.push(
                `${mascota.edadMeses} meses`
            );
        }

        const texto = [
            "🐾 Carnet de mascota - Vítalia",
            `Nombre: ${mascota.nombre}`,
            `Especie: ${mascota.especie}`,
            `Sexo: ${mascota.sexo}`,
            `Raza: ${mascota.raza || "No registrada"}`,
            `Edad: ${edad.join(" y ") || "No registrada"}`,
            `Color: ${mascota.color || "No registrado"}`
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
    // INICIAR PÁGINA
    // =====================================

    establecerModo("consulta");

    if (tieneSesion()) {
        consultarMascota();
    } else {
        establecerModo("consulta");

        mostrarMensaje(
            "Inicia sesión para consultar o administrar tus carnets.",
            "warning"
        );
    }

});
