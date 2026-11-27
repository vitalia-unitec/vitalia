/* =========================================
   VITALIA - GEOLOCALIZACIÓN
   OpenStreetMap / Nominatim
========================================= */

const cacheUbicaciones = new Map();

let colaNominatim = Promise.resolve();
let ultimaPeticionNominatim = 0;

async function geocodificarUbicacion(texto) {

    const consulta = texto.trim();

    if (consulta.length < 2) {
        return null;
    }

    const clave = consulta.toLowerCase();

    if (cacheUbicaciones.has(clave)) {
        return cacheUbicaciones.get(clave);
    }

    const tarea = colaNominatim.then(async () => {

        const espera = Math.max(
            0,
            1100 - (Date.now() - ultimaPeticionNominatim)
        );

        if (espera > 0) {
            await new Promise(resolve => {
                setTimeout(resolve, espera);
            });
        }

        const parametros = new URLSearchParams({
            format: "json",
            limit: "1",
            countrycodes: "mx",
            q: `${consulta}, Ciudad de México`
        });

        ultimaPeticionNominatim = Date.now();

        const controlador = new AbortController();

        const temporizador = setTimeout(() => {
            controlador.abort();
        }, 8000);

        try {

            const respuesta = await fetch(
                `https://nominatim.openstreetmap.org/search?${parametros}`,
                {
                    headers: {
                        Accept: "application/json"
                    },
                    signal: controlador.signal
                }
            );

            if (!respuesta.ok) {
                throw new Error("Nominatim no disponible.");
            }

            const resultados = await respuesta.json();

            if (!Array.isArray(resultados) || !resultados.length) {
                return null;
            }

            const lat = Number(resultados[0].lat);
            const lng = Number(resultados[0].lon);

            if (
                !Number.isFinite(lat) ||
                !Number.isFinite(lng) ||
                lat < -90 ||
                lat > 90 ||
                lng < -180 ||
                lng > 180
            ) {
                return null;
            }

            return { lat, lng };

        } catch (error) {

            console.warn(
                "No se pudo geocodificar la ubicación:",
                error
            );

            return null;

        } finally {

            clearTimeout(temporizador);

        }

    });

    cacheUbicaciones.set(clave, tarea);

    colaNominatim = tarea.catch(() => null);

    return tarea;
}