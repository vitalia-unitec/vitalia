
const API_BASE_URL = "http://localhost:8000/api/v1";

async function apiRequest(endpoint, options = {}) {
    const token = sessionStorage.getItem("vitalia_token");

    const headers = {
        Accept: "application/json",
        ...options.headers
    };

    if (options.body && !(options.body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
    }

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(
            `${API_BASE_URL}${endpoint}`,
            { ...options, headers }
        );

        if (response.status === 204) {
            return null;
        }

        const result = await response.json();

        if (!response.ok || result.ok === false) {
            throw new Error(
                result.error?.mensaje ||
                "Ocurrió un error al comunicarse con Vítalia."
            );
        }

        return result.data;

    } catch (error) {
        console.error("Error de API:", error);
        throw error;
    }
}
