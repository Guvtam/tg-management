(function () {
    "use strict";

    const root = document.getElementById("modalidad-pago-configurador");
    if (!root) return;

    const total = parseNumero(root.dataset.total);
    const moneda = root.dataset.moneda || "CLP";
    const inputDescuento = root.querySelector('[data-calculo="descuento"]');
    const inputPie = root.querySelector('[data-calculo="pie"]');
    const inputMantencion = root.querySelector('[data-calculo="mantencion"]');
    const checkPagoUnico = root.querySelector('[data-toggle-target="pago-unico"]');
    const checkPlan12 = root.querySelector('[data-toggle-target="plan-12"]');

    function parseNumero(valor) {
        if (typeof valor === "number") return Number.isFinite(valor) ? valor : 0;
        const normalizado = String(valor || "")
            .trim()
            .replace(/\s/g, "")
            .replace(/\.(?=\d{3}(?:\D|$))/g, "")
            .replace(",", ".");
        const numero = Number(normalizado);
        return Number.isFinite(numero) ? numero : 0;
    }

    function valorInput(input) {
        if (!input) return 0;
        if (Number.isFinite(input.valueAsNumber)) return input.valueAsNumber;
        return parseNumero(input.value);
    }

    function formatearMoneda(valor) {
        const decimales = moneda === "CLP" ? 0 : 2;
        return new Intl.NumberFormat("es-CL", {
            style: "currency",
            currency: moneda === "UF" ? "CLP" : moneda,
            minimumFractionDigits: decimales,
            maximumFractionDigits: decimales,
        }).format(valor).replace("CLP", moneda);
    }

    function formatearPorcentaje(valor) {
        return new Intl.NumberFormat("es-CL", {
            minimumFractionDigits: 0,
            maximumFractionDigits: 2,
        }).format(valor) + "%";
    }

    function escribir(nombre, valor) {
        root.querySelectorAll(`[data-salida="${nombre}"]`).forEach((elemento) => {
            elemento.textContent = valor;
        });
    }

    function actualizarVisibilidad(check, nombre) {
        const activo = Boolean(check && check.checked);
        root.querySelectorAll(`[data-seccion="${nombre}"], [data-preview="${nombre}"]`).forEach((elemento) => {
            elemento.classList.toggle("mp-deshabilitado", !activo);
        });
    }

    function recalcular() {
        const descuento = Math.min(Math.max(valorInput(inputDescuento), 0), 100);
        const porcentajePie = Math.min(Math.max(valorInput(inputPie), 0), 100);
        const mantencion = Math.max(valorInput(inputMantencion), 0);

        const descuentoMonto = total * descuento / 100;
        const pagoUnico = total - descuentoMonto;
        const pieMonto = total * porcentajePie / 100;
        const saldo = total - pieMonto;
        const cuotaDesarrollo = saldo / 12;
        const cuotaFinal = cuotaDesarrollo + mantencion;

        escribir("valor-proyecto", formatearMoneda(total));
        escribir("pago-unico-normal", formatearMoneda(total));
        escribir("descuento-monto", `− ${formatearMoneda(descuentoMonto)}`);
        escribir("pago-unico-total", formatearMoneda(pagoUnico));
        escribir("pie-monto", `${formatearMoneda(pieMonto)} (${formatearPorcentaje(porcentajePie)})`);
        escribir("saldo-financiado", formatearMoneda(saldo));
        escribir("cuota-desarrollo", formatearMoneda(cuotaDesarrollo));
        escribir("mantencion-mensual", formatearMoneda(mantencion));
        escribir("cuota-final", formatearMoneda(cuotaFinal));
        escribir("preview-pago-unico", formatearMoneda(pagoUnico));
        escribir("preview-pie", formatearMoneda(pieMonto));
        escribir("preview-cuota", `${formatearMoneda(cuotaFinal)} / mes`);
        escribir(
            "preview-descuento",
            descuento > 0
                ? `Incluye ${formatearPorcentaje(descuento)} de descuento`
                : "Sin descuento adicional"
        );

        actualizarVisibilidad(checkPagoUnico, "pago-unico");
        actualizarVisibilidad(checkPlan12, "plan-12");
    }

    [inputDescuento, inputPie, inputMantencion].forEach((input) => {
        if (!input) return;
        input.addEventListener("input", recalcular);
        input.addEventListener("change", recalcular);
    });

    [checkPagoUnico, checkPlan12].forEach((check) => {
        if (check) check.addEventListener("change", recalcular);
    });

    recalcular();
})();
