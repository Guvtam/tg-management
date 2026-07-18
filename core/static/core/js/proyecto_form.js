document.addEventListener("DOMContentLoaded", function () {
    const empresaSelect = document.getElementById("id_empresa");
    const cotizacionSelect = document.getElementById("id_cotizacion");
    const contenedor = document.getElementById(
        "campo-cotizacion-relacionada"
    );

    if (!empresaSelect || !cotizacionSelect || !contenedor) {
        return;
    }

    const urlCotizaciones = contenedor.dataset.url;

    async function cargarCotizaciones() {
        const empresaId = empresaSelect.value;

        cotizacionSelect.innerHTML = "";
        cotizacionSelect.disabled = true;

        const opcionInicial = document.createElement("option");
        opcionInicial.value = "";

        if (!empresaId) {
            opcionInicial.textContent =
                "Primero selecciona un cliente";

            cotizacionSelect.appendChild(opcionInicial);
            return;
        }

        opcionInicial.textContent =
            "Cargando cotizaciones...";

        cotizacionSelect.appendChild(opcionInicial);

        try {
            const respuesta = await fetch(
                urlCotizaciones +
                    "?empresa_id=" +
                    encodeURIComponent(empresaId)
            );

            if (!respuesta.ok) {
                throw new Error(
                    "Error HTTP " + respuesta.status
                );
            }

            const datos = await respuesta.json();

            cotizacionSelect.innerHTML = "";

            const opcionVacia =
                document.createElement("option");

            opcionVacia.value = "";
            opcionVacia.textContent =
                datos.cotizaciones.length > 0
                    ? "Selecciona una cotización"
                    : "Este cliente no tiene cotizaciones";

            cotizacionSelect.appendChild(opcionVacia);

            datos.cotizaciones.forEach(function (item) {
                const opcion =
                    document.createElement("option");

                opcion.value = item.id;
                opcion.textContent = item.texto;

                cotizacionSelect.appendChild(opcion);
            });

            cotizacionSelect.disabled = false;
        } catch (error) {
            console.error(error);

            cotizacionSelect.innerHTML = "";

            const opcionError =
                document.createElement("option");

            opcionError.value = "";
            opcionError.textContent =
                "Error al cargar cotizaciones";

            cotizacionSelect.appendChild(opcionError);
        }
    }

    /*
     * Solo se recargan las cotizaciones
     * cuando el usuario cambia el cliente.
     *
     * Al abrir una edición, Django mantiene
     * la cotización seleccionada.
     */
    empresaSelect.addEventListener(
        "change",
        cargarCotizaciones
    );
});