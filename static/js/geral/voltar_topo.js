document.addEventListener("DOMContentLoaded", () => {
  const btnTopo = document.getElementById("btnTopo");
  if (!btnTopo) return;

  btnTopo.style.opacity = "0";
  btnTopo.style.display = "none";

  btnTopo.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  let lastScrollTop = 0;

  window.addEventListener("scroll", () => {
    const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;

    if (scrollTop > lastScrollTop && scrollTop > 600) {
      // DESCENDO
      if (btnTopo.style.display === "none") {
        btnTopo.style.display = "flex";
        setTimeout(() => {
          btnTopo.style.opacity = "1";
        }, 10);
      }
    } else {
      // SUBINDO
      if (btnTopo.style.display === "flex") {
        btnTopo.style.opacity = "0";
        setTimeout(() => {
          btnTopo.style.display = "none";
        }, 300);
      }
    }

    lastScrollTop = scrollTop <= 0 ? 0 : scrollTop; 
  });
});
