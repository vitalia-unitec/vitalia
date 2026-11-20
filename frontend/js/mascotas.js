
/* =========================================
   VITALIA - MIS MASCOTAS
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

    // =====================================
    // MODO DEMOSTRACIÓN
    // =====================================

    // Mantener los mismos valores que perfil.js.
    // Estas variables NO representan una sesión real.

    const MODO_DEMO = true;
    const DEMO_USUARIO_REGISTRADO = false;

    // Mascotas ficticias para probar el diseño.

    let mascotas = [
        {
            id: 1,
            nombre: "Luna",
            especie: "Perro",
            raza: "Golden Retriever",
            nacimiento: "2023-05-12"
        },
        {
            id: 2,
            nombre: "Milo",
            especie: "Gato",
            raza: "Siamés",
            nacimiento: "2024-08-20"
        }
    ];

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

        mostrarMascotas();
    }

    // =====================================
    // CALCULAR EDAD
    // =====================================

    function calcularEdad(fechaNacimiento) {

        if (!fechaNacimiento) {
            return "Edad no registrada";
        }

        const hoy = new Date();
        const nacimiento = new Date(
            fechaNacimiento + "T00:00:00"
        );

        let edad = hoy.getFullYear() -
                   nacimiento.getFullYear();

        const diferenciaMeses =
            hoy.getMonth() - nacimiento.getMonth();

        if (
            diferenciaMeses < 0 ||
            (diferenciaMeses === 0 &&
             hoy.getDate() < nacimiento.getDate())
        ) {
            edad--;
        }

        if (edad < 0) {
            return "Fecha no válida";
        }

        return edad === 1
            ? "1 año"
            : `${edad} años`;
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

        mascotas.forEach((mascota) => {

            const columna = document.createElement("div");

            columna.className =
                "col-12 col-sm-6 col-lg-4";

            const tarjeta = document.createElement("div");
            tarjeta.className = "tarjeta-mascota";

            const avatar = document.createElement("div");
            avatar.className = "avatar-mascota";

            const icono = document.createElement("i");

            if (mascota.especie === "Perro") {
                icono.className = "bi bi-heart-fill";
            } else if (mascota.especie === "Gato") {
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
                mascota.especie,
                mascota.raza || "Raza no registrada",
                calcularEdad(mascota.nacimiento)
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
    // REGISTRAR MASCOTA
    // =====================================

    formMascota.addEventListener("submit", (evento) => {

        evento.preventDefault();

        if (!formMascota.checkValidity()) {
            formMascota.reportValidity();
            return;
        }

        const nombre =
            document.getElementById("nombreMascota").value.trim();

        const especie =
            document.getElementById("especieMascota").value;

        const raza =
            document.getElementById("razaMascota").value.trim();

        const nacimiento =
            document.getElementById("nacimientoMascota").value;

        if (!nombre) {
            mensajeMascotas.textContent =
                "Debes ingresar el nombre de tu mascota.";
            return;
        }

        if (nacimiento) {

            const fecha = new Date(nacimiento + "T00:00:00");

            if (fecha > new Date()) {

                mensajeMascotas.textContent =
                    "La fecha de nacimiento no puede ser futura.";

                mensajeMascotas.className =
                    "mt-3 text-danger";

                return;
            }
        }

        if (!MODO_DEMO) {

            mensajeMascotas.textContent =
                "El registro real estará disponible al conectar la API.";

            mensajeMascotas.className =
                "mt-3 text-muted";

            return;
        }

        const nuevaMascota = {
            id: crypto.randomUUID(),
            nombre,
            especie,
            raza,
            nacimiento
        };

        mascotas.push(nuevaMascota);

        mostrarMascotas();

        formMascota.reset();

        const modalElemento =
            document.getElementById("modalMascota");

        const modal =
            bootstrap.Modal.getInstance(modalElemento);

        modal?.hide();

        mensajeMascotas.textContent =
            "Mascota agregada a la demostración. " +
            "No se ha guardado en una base de datos.";

        mensajeMascotas.className =
            "mt-3 text-success";
    });

    // =====================================
    // INICIAR PÁGINA
    // =====================================

    if (MODO_DEMO) {

        if (DEMO_USUARIO_REGISTRADO) {
            mostrarUsuario();
        } else {
            mostrarInvitado();
        }

    } else {

        // Hasta conectar la autenticación real,
        // no se mostrarán datos privados.
        mostrarInvitado();
    }

});
