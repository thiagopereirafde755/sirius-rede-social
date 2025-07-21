document.addEventListener("DOMContentLoaded", function () {
  const campo = document.getElementById("campo-pesquisa");
  const lista = document.getElementById("sugestoes");

  if (!campo || !lista) return;

  campo.addEventListener("input", async function () {
    const termo = campo.value.trim();

    if (termo.length < 1) {
      lista.style.display = "none";
      return;
    }

    try {
      const res = await fetch(`/sugestoes_pesquisa?termo=${encodeURIComponent(termo)}`);
      const sugestoes = await res.json();

      if (sugestoes.length > 0) {
        lista.innerHTML = "";
        sugestoes.forEach(item => {
          const li = document.createElement("li");
          li.textContent = item;
          li.onclick = () => {
            campo.value = item;
            lista.style.display = "none";
          };
          lista.appendChild(li);
        });
        lista.style.display = "block";
      } else {
        lista.style.display = "none";
      }
    } catch (error) {
      console.error("Erro ao buscar sugestões:", error);
      lista.style.display = "none";
    }
  });

  // Esconder lista ao clicar fora
  document.addEventListener("click", function (e) {
    if (!campo.parentElement.contains(e.target)) {
      lista.style.display = "none";
    }
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const campoMobile = document.getElementById("campo-pesquisa-mobile");
  const listaMobile = document.getElementById("sugestoes-mobile");

  if (!campoMobile || !listaMobile) return;

  campoMobile.addEventListener("input", async function () {
    const termo = campoMobile.value.trim();

    if (termo.length < 1) {
      listaMobile.style.display = "none";
      return;
    }

    try {
      const res = await fetch(`/sugestoes_pesquisa?termo=${encodeURIComponent(termo)}`);
      const sugestoes = await res.json();

      if (sugestoes.length > 0) {
        listaMobile.innerHTML = "";
        sugestoes.forEach(item => {
          const li = document.createElement("li");
          li.textContent = item;
          li.onclick = () => {
            campoMobile.value = item;
            listaMobile.style.display = "none";
          };
          listaMobile.appendChild(li);
        });
        listaMobile.style.display = "block";
      } else {
        listaMobile.style.display = "none";
      }
    } catch (error) {
      console.error("Erro ao buscar sugestões (mobile):", error);
      listaMobile.style.display = "none";
    }
  });

  // Esconder lista ao clicar fora do campo mobile
  document.addEventListener("click", function (e) {
    if (!campoMobile.parentElement.contains(e.target)) {
      listaMobile.style.display = "none";
    }
  });
});
