"use strict";

function obtenerModalExportar() {
    return document.getElementById("modalExportar");
}

function abrirModalExportar() {
    const modal = obtenerModalExportar();

    if (!modal) {
        return;
    }

    modal.classList.add("activo");
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";

    const botonCerrar = modal.querySelector(".modal-exportar-cerrar");

    if (botonCerrar) {
        botonCerrar.focus();
    }
}

function cerrarModalExportar() {
    const modal = obtenerModalExportar();

    if (!modal) {
        return;
    }

    modal.classList.remove("activo");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
}

document.addEventListener("DOMContentLoaded", function () {
    const modal = obtenerModalExportar();
    const botonAbrir = document.getElementById("btnAbrirModalExportar");
    const botonesCerrar = document.querySelectorAll(
        "[data-cerrar-modal-exportar]"
    );

    if (botonAbrir) {
        botonAbrir.addEventListener("click", abrirModalExportar);
    }

    botonesCerrar.forEach(function (boton) {
        boton.addEventListener("click", cerrarModalExportar);
    });

    document.addEventListener("keydown", function (evento) {
        if (evento.key === "Escape") {
            cerrarModalExportar();
        }
    });

    if (modal) {
        modal.addEventListener("click", function (evento) {
            if (evento.target === modal) {
                cerrarModalExportar();
            }
        });
    }
});