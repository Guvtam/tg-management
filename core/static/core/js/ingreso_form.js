
document.addEventListener("DOMContentLoaded", function () {
    const empresaSelect = document.getElementById("id_empresa");
    const proyectoSelect = document.getElementById("id_proyecto");
    const cotizacionSelect = document.getElementById("id_cotizacion");

    if (!empresaSelect || !proyectoSelect || !cotizacionSelect) {
        return;
    }

    const urlProyectos = window.finanzasUrls.proyectos;
    const urlCotizaciones = window.finanzasUrls.cotizaciones;

    const proyectoSeleccionadoInicial = proyectoSelect.value;
    const cotizacionSeleccionadaInicial = cotizacionSelect.value;

    function limpiarSelect(select, texto) {
        select.innerHTML = "";

        const option = document.createElement("option");
        option.value = "";
        option.textContent = texto;

        select.appendChild(option);
    }

    function cargarProyectos(empresaId, valorSeleccionado = "") {
        limpiarSelect(proyectoSelect, "---------");

        if (!empresaId) {
            return;
        }

        fetch(`${urlProyectos}?empresa_id=${empresaId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("No fue posible cargar los proyectos.");
                }

                return response.json();
            })
            .then(data => {
                data.proyectos.forEach(proyecto => {
                    const option = document.createElement("option");

                    option.value = proyecto.id;
                    option.textContent = proyecto.nombre;

                    if (
                        valorSeleccionado &&
                        String(proyecto.id) === String(valorSeleccionado)
                    ) {
                        option.selected = true;
                    }

                    proyectoSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error(error);
                limpiarSelect(
                    proyectoSelect,
                    "Error al cargar proyectos"
                );
            });
    }

    function cargarCotizaciones(empresaId, valorSeleccionado = "") {
        limpiarSelect(cotizacionSelect, "---------");

        if (!empresaId) {
            return;
        }

        fetch(`${urlCotizaciones}?empresa_id=${empresaId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(
                        "No fue posible cargar las cotizaciones."
                    );
                }

                return response.json();
            })
            .then(data => {
                data.cotizaciones.forEach(cotizacion => {
                    const option = document.createElement("option");

                    option.value = cotizacion.id;
                    option.textContent = cotizacion.nombre;

                    option.dataset.monto = cotizacion.monto;
                    option.dataset.moneda = cotizacion.moneda;

                    if (
                        valorSeleccionado &&
                        String(cotizacion.id) ===
                        String(valorSeleccionado)
                    ) {
                        option.selected = true;
                    }

                    cotizacionSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error(error);
                limpiarSelect(
                    cotizacionSelect,
                    "Error al cargar cotizaciones"
                );
            });
    }

    empresaSelect.addEventListener("change", function () {
        const empresaId = this.value;

        cargarProyectos(empresaId);
        cargarCotizaciones(empresaId);
    });

    if (empresaSelect.value) {
        cargarProyectos(
            empresaSelect.value,
            proyectoSeleccionadoInicial
        );

        cargarCotizaciones(
            empresaSelect.value,
            cotizacionSeleccionadaInicial
        );
    }
});
