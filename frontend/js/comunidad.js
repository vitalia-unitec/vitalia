
/* =========================================
   VITALIA - COMUNIDAD
   Integración con FastAPI
========================================= */

document.addEventListener("DOMContentLoaded", () => {

    const listaPublicaciones =
        document.getElementById("listaPublicaciones");

    const estadoPublicaciones =
        document.getElementById("estadoPublicaciones");

    const mensajeComunidad =
        document.getElementById("mensajeComunidad");

    const formPublicacion =
        document.getElementById("formPublicacion");

    const textoPublicacion =
        document.getElementById("textoPublicacion");

    const contadorPublicacion =
        document.getElementById("contadorPublicacion");

    const botonCargarMas =
        document.getElementById("cargarMasPublicaciones");

    const POR_PAGINA = 10;

    let pagina = 1;
    let cargando = false;

    const publicacionesMostradas = new Set();

    // =====================================
    // FUNCIONES AUXILIARES
    // =====================================

    function haySesion() {
        return Boolean(
            obtenerToken() && obtenerUsuarioActual()
        );
    }

    function mostrarMensaje(texto, tipo = "success") {
        mensajeComunidad.className = `alert alert-${tipo}`;
        mensajeComunidad.textContent = texto;
        mensajeComunidad.hidden = false;
    }

    function limpiarMensaje() {
        mensajeComunidad.hidden = true;
        mensajeComunidad.textContent = "";
    }

    function formatearFecha(fecha) {

        if (!fecha) return "";

        const valor = new Date(fecha);

        if (Number.isNaN(valor.getTime())) {
            return "";
        }

        return valor.toLocaleString("es-MX", {
            day: "numeric",
            month: "long",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit"
        });
    }

    function crearElemento(etiqueta, clase, texto) {

        const elemento = document.createElement(etiqueta);

        if (clase) {
            elemento.className = clase;
        }

        if (texto !== undefined) {
            elemento.textContent = texto;
        }

        return elemento;
    }

    function crearBoton(icono, titulo, clase) {

        const boton = crearElemento(
            "button",
            clase || "btn-accion-comunidad"
        );

        boton.type = "button";
        boton.title = titulo;
        boton.setAttribute("aria-label", titulo);

        const i = crearElemento("i", `bi ${icono}`);
        i.setAttribute("aria-hidden", "true");

        boton.appendChild(i);

        return boton;
    }

    // =====================================
    // CONTADOR DE CARACTERES
    // =====================================

    textoPublicacion.addEventListener("input", () => {

        contadorPublicacion.textContent =
            `${textoPublicacion.value.length} / 2000`;

    });

    // =====================================
    // CONSULTAR PUBLICACIONES
    // =====================================

    async function cargarPublicaciones(reiniciar = false) {

        if (cargando) return;

        cargando = true;
        botonCargarMas.disabled = true;

        if (reiniciar) {

            pagina = 1;
            publicacionesMostradas.clear();
            listaPublicaciones.replaceChildren();

            estadoPublicaciones.hidden = false;
            estadoPublicaciones.textContent =
                "Cargando publicaciones...";

            botonCargarMas.hidden = true;
        }

        try {

            const publicaciones = await apiRequest(
                `/comunidad?pagina=${pagina}&porPagina=${POR_PAGINA}`
            );

            if (!Array.isArray(publicaciones)) {
                throw new Error(
                    "La respuesta de publicaciones no es válida."
                );
            }

            estadoPublicaciones.hidden = true;

            publicaciones.forEach(publicacion => {

                if (publicacionesMostradas.has(publicacion.id)) {
                    return;
                }

                publicacionesMostradas.add(publicacion.id);

                listaPublicaciones.appendChild(
                    crearPublicacion(publicacion)
                );

            });

            if (pagina === 1 && publicaciones.length === 0) {

                estadoPublicaciones.hidden = false;

                estadoPublicaciones.textContent =
                    "Aún no hay publicaciones. ¡Sé el primero en compartir!";

            }

            botonCargarMas.hidden =
                publicaciones.length < POR_PAGINA;

            pagina++;

        } catch (error) {

            if (pagina === 1) {

                estadoPublicaciones.hidden = false;

                estadoPublicaciones.textContent =
                    "No fue posible cargar las publicaciones.";

            }

            mostrarMensaje(error.message, "danger");

        } finally {

            cargando = false;
            botonCargarMas.disabled = false;

        }
    }

    botonCargarMas.addEventListener("click", () => {
        cargarPublicaciones();
    });

    // =====================================
    // CREAR PUBLICACIÓN
    // =====================================

    formPublicacion.addEventListener("submit", async event => {

        event.preventDefault();
        limpiarMensaje();

        if (!haySesion()) {
            window.location.href = "login.html";
            return;
        }

        const texto = textoPublicacion.value.trim();

        if (!texto || texto.length > 2000) {

            mostrarMensaje(
                "Escribe una publicación de 1 a 2000 caracteres.",
                "warning"
            );

            return;
        }

        const boton = formPublicacion.querySelector(
            'button[type="submit"]'
        );

        boton.disabled = true;

        try {

            const publicacion = await apiRequest("/comunidad", {
                method: "POST",
                body: JSON.stringify({ texto })
            });

            textoPublicacion.value = "";
            contadorPublicacion.textContent = "0 / 2000";

            if (!publicacionesMostradas.has(publicacion.id)) {

                publicacionesMostradas.add(publicacion.id);

                listaPublicaciones.prepend(
                    crearPublicacion(publicacion)
                );

            }

            estadoPublicaciones.hidden = true;

            mostrarMensaje(
                "Tu publicación se compartió correctamente."
            );

        } catch (error) {

            mostrarMensaje(error.message, "danger");

        } finally {

            boton.disabled = false;

        }
    });

    // =====================================
    // RENDERIZAR PUBLICACIÓN
    // =====================================

    function crearPublicacion(publicacion) {

        const tarjeta = crearElemento(
            "article",
            "publicacion"
        );

        tarjeta.dataset.id = publicacion.id;

        const encabezado = crearElemento(
            "div",
            "publicacion-encabezado"
        );

        const nombre = publicacion.autor?.nombre || "Usuario";

        const avatar = crearElemento(
            "div",
            "avatar-comunidad",
            nombre.charAt(0).toUpperCase()
        );

        const autor = crearElemento(
            "div",
            "publicacion-autor"
        );

        const nombreAutor = crearElemento(
            "strong",
            "",
            nombre
        );

        const fecha = crearElemento(
            "span",
            "publicacion-fecha",
            formatearFecha(publicacion.creadoEn) +
            (publicacion.editadoEn ? " · Editado" : "")
        );

        autor.append(nombreAutor, fecha);
        encabezado.append(avatar, autor);

        const contenido = crearElemento(
            "p",
            "publicacion-texto",
            publicacion.texto
        );

        // Solo el propietario puede editar o eliminar.

        if (haySesion() && publicacion.esMia === true) {

            const acciones = crearElemento(
                "div",
                "publicacion-acciones"
            );

            const editar = crearBoton(
                "bi-pencil",
                "Editar publicación"
            );

            const eliminar = crearBoton(
                "bi-trash",
                "Eliminar publicación",
                "btn-accion-comunidad btn-eliminar-comunidad"
            );

            editar.addEventListener("click", () => {

                editarPublicacion(
                    publicacion,
                    contenido,
                    fecha,
                    editar
                );

            });

            eliminar.addEventListener("click", () => {

                eliminarPublicacion(
                    publicacion.id,
                    tarjeta,
                    eliminar
                );

            });

            acciones.append(editar, eliminar);
            encabezado.appendChild(acciones);

        }

        // Comentarios

        const botonComentarios = crearElemento(
            "button",
            "btn-comentarios"
        );

        botonComentarios.type = "button";
        botonComentarios.setAttribute("aria-expanded", "false");

        function actualizarContador() {

            botonComentarios.replaceChildren();

            const icono = crearElemento(
                "i",
                "bi bi-chat-dots me-2"
            );

            botonComentarios.append(
                icono,
                document.createTextNode(
                    `${publicacion.totalComentarios || 0} comentarios`
                )
            );
        }

        actualizarContador();

        const comentarios = crearElemento(
            "div",
            "comentarios-contenedor"
        );

        comentarios.hidden = true;

        botonComentarios.addEventListener("click", () => {

            comentarios.hidden = !comentarios.hidden;

            botonComentarios.setAttribute(
                "aria-expanded",
                String(!comentarios.hidden)
            );

            if (!comentarios.hidden && !comentarios.dataset.iniciado) {

                iniciarComentarios(
                    publicacion,
                    comentarios,
                    actualizarContador
                );

            }

        });

        tarjeta.append(
            encabezado,
            contenido,
            botonComentarios,
            comentarios
        );

        return tarjeta;
    }

    // =====================================
    // EDITAR PUBLICACIÓN
    // =====================================

    function editarPublicacion(
        publicacion,
        contenido,
        fecha,
        botonEditar
    ) {

        if (!haySesion() || botonEditar.disabled) return;

        botonEditar.disabled = true;

        const formulario = crearElemento(
            "form",
            "my-3"
        );

        const campo = crearElemento(
            "textarea",
            "form-control campo-comunidad mb-3"
        );

        campo.value = publicacion.texto;
        campo.maxLength = 2000;
        campo.rows = 4;
        campo.required = true;

        campo.setAttribute(
            "aria-label",
            "Editar texto de publicación"
        );

        const guardar = crearElemento(
            "button",
            "btn btn-success rounded-pill me-2",
            "Guardar"
        );

        guardar.type = "submit";

        const cancelar = crearElemento(
            "button",
            "btn btn-outline-secondary rounded-pill",
            "Cancelar"
        );

        cancelar.type = "button";

        formulario.append(campo, guardar, cancelar);

        contenido.hidden = true;
        contenido.after(formulario);

        campo.focus();

        function cerrarEditor() {

            formulario.remove();
            contenido.hidden = false;
            botonEditar.disabled = false;

        }

        cancelar.addEventListener("click", cerrarEditor);

        formulario.addEventListener("submit", async event => {

            event.preventDefault();

            const texto = campo.value.trim();

            if (!texto || texto.length > 2000) {

                mostrarMensaje(
                    "La publicación debe tener de 1 a 2000 caracteres.",
                    "warning"
                );

                return;
            }

            guardar.disabled = true;
            cancelar.disabled = true;

            try {

                const actualizada = await apiRequest(
                    `/comunidad/${publicacion.id}`,
                    {
                        method: "PUT",
                        body: JSON.stringify({ texto })
                    }
                );

                Object.assign(publicacion, actualizada);

                contenido.textContent = actualizada.texto;

                fecha.textContent =
                    formatearFecha(actualizada.creadoEn) +
                    (actualizada.editadoEn ? " · Editado" : "");

                cerrarEditor();

                mostrarMensaje("Publicación actualizada.");

            } catch (error) {

                mostrarMensaje(error.message, "danger");

            } finally {

                guardar.disabled = false;
                cancelar.disabled = false;

            }

        });
    }

    // =====================================
    // ELIMINAR PUBLICACIÓN
    // =====================================

    async function eliminarPublicacion(id, tarjeta, boton) {

        if (!haySesion()) return;

        const confirmar = window.confirm(
            "¿Deseas eliminar esta publicación?"
        );

        if (!confirmar) return;

        boton.disabled = true;

        try {

            await apiRequest(`/comunidad/${id}`, {
                method: "DELETE"
            });

            publicacionesMostradas.delete(id);
            tarjeta.remove();

            mostrarMensaje("Publicación eliminada.");

            if (!listaPublicaciones.children.length) {

                estadoPublicaciones.hidden = false;

                estadoPublicaciones.textContent =
                    "No hay publicaciones visibles.";

            }

        } catch (error) {

            mostrarMensaje(error.message, "danger");

        } finally {

            boton.disabled = false;

        }
    }

    // =====================================
    // COMENTARIOS
    // =====================================

    function iniciarComentarios(
        publicacion,
        contenedor,
        actualizarContador
    ) {

        contenedor.dataset.iniciado = "true";

        const lista = crearElemento("div", "");

        const estado = crearElemento(
            "p",
            "text-muted small",
            "Cargando comentarios..."
        );

        const cargarMas = crearElemento(
            "button",
            "btn btn-outline-success btn-sm rounded-pill mb-3",
            "Ver más comentarios"
        );

        cargarMas.type = "button";
        cargarMas.hidden = true;

        let paginaComentarios = 1;
        let cargandoComentarios = false;

        const comentariosMostrados = new Set();

        contenedor.append(estado, lista, cargarMas);

        async function cargarComentarios(reiniciar = false) {

            if (cargandoComentarios) return;

            cargandoComentarios = true;
            cargarMas.disabled = true;

            if (reiniciar) {

                paginaComentarios = 1;
                comentariosMostrados.clear();
                lista.replaceChildren();

            }

            estado.hidden = false;
            estado.textContent = "Cargando comentarios...";

            try {

                const comentarios = await apiRequest(
                    `/comunidad/${publicacion.id}/comentarios` +
                    `?pagina=${paginaComentarios}&porPagina=${POR_PAGINA}`
                );

                if (!Array.isArray(comentarios)) {

                    throw new Error(
                        "La respuesta de comentarios no es válida."
                    );

                }

                estado.hidden = true;

                comentarios.forEach(comentario => {

                    if (comentariosMostrados.has(comentario.id)) {
                        return;
                    }

                    comentariosMostrados.add(comentario.id);

                    lista.appendChild(
                        crearComentario(
                            publicacion,
                            comentario,
                            actualizarContador,
                            comentariosMostrados,
                            lista,
                            estado
                        )
                    );

                });

                if (
                    paginaComentarios === 1 &&
                    comentarios.length === 0
                ) {

                    estado.hidden = false;
                    estado.textContent = "Aún no hay comentarios.";

                }

                cargarMas.hidden =
                    comentarios.length < POR_PAGINA;

                cargarMas.textContent = "Ver más comentarios";

                paginaComentarios++;

            } catch (error) {

                estado.hidden = false;
                estado.textContent = error.message;

                cargarMas.hidden = false;
                cargarMas.textContent = "Reintentar";

            } finally {

                cargandoComentarios = false;
                cargarMas.disabled = false;

            }
        }

        cargarMas.addEventListener("click", () => {
            cargarComentarios();
        });

        // Formulario disponible únicamente con sesión.

        if (haySesion()) {

            const formulario = crearElemento(
                "form",
                "form-comentario"
            );

            const campo = crearElemento(
                "textarea",
                "form-control campo-comunidad mb-2"
            );

            campo.placeholder = "Escribe un comentario...";
            campo.maxLength = 1000;
            campo.rows = 2;
            campo.required = true;

            campo.setAttribute(
                "aria-label",
                "Escribe un comentario"
            );

            const boton = crearElemento(
                "button",
                "btn btn-success btn-sm rounded-pill px-3",
                "Comentar"
            );

            boton.type = "submit";

            formulario.append(campo, boton);
            contenedor.appendChild(formulario);

            formulario.addEventListener("submit", async event => {

                event.preventDefault();

                if (!haySesion()) {
                    window.location.href = "login.html";
                    return;
                }

                const texto = campo.value.trim();

                if (!texto || texto.length > 1000) {

                    mostrarMensaje(
                        "El comentario debe tener de 1 a 1000 caracteres.",
                        "warning"
                    );

                    return;
                }

                boton.disabled = true;

                try {

                    await apiRequest(
                        `/comunidad/${publicacion.id}/comentarios`,
                        {
                            method: "POST",
                            body: JSON.stringify({ texto })
                        }
                    );

                    campo.value = "";

                    publicacion.totalComentarios =
                        (publicacion.totalComentarios || 0) + 1;

                    actualizarContador();

                    await cargarComentarios(true);

                    mostrarMensaje("Comentario publicado.");

                } catch (error) {

                    mostrarMensaje(error.message, "danger");

                } finally {

                    boton.disabled = false;

                }

            });

        } else {

            const aviso = crearElemento(
                "p",
                "small text-muted mt-3"
            );

            const enlace = crearElemento(
                "a",
                "text-success",
                "Inicia sesión"
            );

            enlace.href = "login.html";

            aviso.append(
                enlace,
                document.createTextNode(" para comentar.")
            );

            contenedor.appendChild(aviso);

        }

        cargarComentarios();
    }

    // =====================================
    // RENDERIZAR COMENTARIO
    // =====================================

    function crearComentario(
        publicacion,
        comentario,
        actualizarContador,
        comentariosMostrados,
        lista,
        estado
    ) {

        const tarjeta = crearElemento(
            "article",
            "comentario"
        );

        const encabezado = crearElemento(
            "div",
            "comentario-encabezado"
        );

        const autor = crearElemento(
            "span",
            "comentario-autor",
            comentario.autor?.nombre || "Usuario"
        );

        encabezado.appendChild(autor);

        if (haySesion() && comentario.esMio === true) {

            const eliminar = crearBoton(
                "bi-trash",
                "Eliminar comentario",
                "btn-accion-comunidad btn-eliminar-comunidad"
            );

            eliminar.addEventListener("click", async () => {

                if (!haySesion()) return;

                if (!window.confirm("¿Eliminar este comentario?")) {
                    return;
                }

                eliminar.disabled = true;

                try {

                    await apiRequest(
                        `/comunidad/${publicacion.id}` +
                        `/comentarios/${comentario.id}`,
                        {
                            method: "DELETE"
                        }
                    );

                    comentariosMostrados.delete(comentario.id);

                    tarjeta.remove();

                    publicacion.totalComentarios = Math.max(
                        0,
                        (publicacion.totalComentarios || 0) - 1
                    );

                    actualizarContador();

                    if (
                        !lista.children.length &&
                        publicacion.totalComentarios === 0
                    ) {

                        estado.hidden = false;
                        estado.textContent =
                            "Aún no hay comentarios.";

                    }

                    mostrarMensaje("Comentario eliminado.");

                } catch (error) {

                    mostrarMensaje(error.message, "danger");

                } finally {

                    eliminar.disabled = false;

                }

            });

            encabezado.appendChild(eliminar);

        }

        const fecha = crearElemento(
            "div",
            "publicacion-fecha",
            formatearFecha(comentario.creadoEn)
        );

        const texto = crearElemento(
            "p",
            "comentario-texto",
            comentario.texto
        );

        tarjeta.append(encabezado, fecha, texto);

        return tarjeta;
    }

    // =====================================
    // INICIALIZAR COMUNIDAD
    // =====================================

    cargarPublicaciones(true);

});
