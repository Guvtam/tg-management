document.addEventListener("DOMContentLoaded", function () {
    const modalidadSelect =
        document.getElementById("id_modalidad_pago");

    const grupoAnticipo =
        document.getElementById("grupo-porcentaje-anticipo");

    const grupoCuotas =
        document.getElementById("grupo-numero-cuotas");

    const grupoMontoServicio =
        document.getElementById("grupo-monto-servicio");

    const grupoMesesServicio =
        document.getElementById("grupo-meses-servicio");

    const grupoFechaServicio =
        document.getElementById("grupo-fecha-inicio-servicio");

    if (!modalidadSelect) {
        return;
    }

    const modalidadesConAnticipo = [
        "anticipo_saldo",
        "anticipo_cuotas",
        "anticipo_cuotas_mensual"
    ];

    const modalidadesConCuotas = [
        "anticipo_cuotas",
        "anticipo_cuotas_mensual",
        "solo_cuotas"
    ];

    const modalidadesConServicio = [
        "anticipo_cuotas_mensual",
        "servicio_mensual"
    ];

    function mostrarElemento(elemento, mostrar) {
        if (!elemento) {
            return;
        }

        elemento.style.display = mostrar ? "" : "none";
    }

    function actualizarCamposPago() {
        const modalidad = modalidadSelect.value;

        mostrarElemento(
            grupoAnticipo,
            modalidadesConAnticipo.includes(modalidad)
        );

        mostrarElemento(
            grupoCuotas,
            modalidadesConCuotas.includes(modalidad)
        );

        const tieneServicio =
            modalidadesConServicio.includes(modalidad);

        mostrarElemento(
            grupoMontoServicio,
            tieneServicio
        );

        mostrarElemento(
            grupoMesesServicio,
            tieneServicio
        );

        mostrarElemento(
            grupoFechaServicio,
            tieneServicio
        );
    }

    modalidadSelect.addEventListener(
        "change",
        actualizarCamposPago
    );

    actualizarCamposPago();
});