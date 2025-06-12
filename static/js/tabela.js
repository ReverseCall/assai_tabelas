const toggle = document.getElementById("toggleView");
const viewImagem = document.getElementById("view-imagem");
const viewTabela = document.getElementById("view-tabela");

const toggleCarnes = document.getElementById("toggleCarnes");
const toggleVerduras = document.getElementById("toggleVerduras");

const toggleImages = document.getElementById("toggleImages");
const toggleImagesLabel = document.getElementById("toggleImagesLabel");
const toggleCarnesLabel = document.getElementById("toggleCarnesLabel");
const toggleVerdurasLabel = document.getElementById("toggleVerdurasLabel");

function updateCategoriaVisibility() {
    if (viewImagem.classList.contains("hidden")) return;

    const mostrarCarnes = toggleCarnes.checked;
    const mostrarVerduras = toggleVerduras.checked;

    document.querySelectorAll(".categoria-carnes").forEach(el => {
        el.style.display = mostrarCarnes ? "" : "none";
    });
    document.querySelectorAll(".categoria-verduras").forEach(el => {
        el.style.display = mostrarVerduras ? "" : "none";
    });
}

function updateImageVisibility() {
    if (viewImagem.classList.contains("hidden")) return;

    const mostrarImagens = toggleImages.checked;
    document.querySelectorAll(".produto-img img:first-child").forEach(img => {
        img.style.display = mostrarImagens ? "" : "none";
    });
}

toggle.addEventListener("change", function () {
    const isTabela = this.checked;

    if (isTabela) {
        viewImagem.classList.add("hidden");
        viewTabela.classList.remove("hidden");

        toggleImagesLabel.classList.add("hidden");
        toggleCarnesLabel.classList.add("hidden");
        toggleVerdurasLabel.classList.add("hidden");
    } else {
        viewTabela.classList.add("hidden");
        viewImagem.classList.remove("hidden");

        toggleImagesLabel.classList.remove("hidden");
        toggleCarnesLabel.classList.remove("hidden");
        toggleVerdurasLabel.classList.remove("hidden");
    }

    updateCategoriaVisibility();
    updateImageVisibility();
});

toggleCarnes.addEventListener("change", updateCategoriaVisibility);
toggleVerduras.addEventListener("change", updateCategoriaVisibility);
toggleImages.addEventListener("change", updateImageVisibility);

// Atualiza ao carregar a página
updateCategoriaVisibility();
updateImageVisibility();