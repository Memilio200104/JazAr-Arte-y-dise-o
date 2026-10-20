(() => {
  window.lucide?.createIcons();
  const menu = document.querySelector(".menu-toggle");
  const nav = document.querySelector("#site-nav");
  const setMenu = (open) => {
    menu.setAttribute("aria-expanded", String(open));
    menu.setAttribute("aria-label", open ? "Cerrar menú" : "Abrir menú");
    nav.classList.toggle("is-open", open);
  };
  menu?.addEventListener("click", () =>
    setMenu(menu.getAttribute("aria-expanded") !== "true"),
  );
  nav?.addEventListener("click", (e) => {
    if (e.target.closest("a")) setMenu(false);
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && menu?.getAttribute("aria-expanded") === "true") {
      setMenu(false);
      menu.focus();
    }
  });
  document.querySelectorAll("[data-interest]").forEach((link) =>
    link.addEventListener("click", () => {
      const select = document.querySelector("#id_interest");
      if (select) {
        select.value = link.dataset.interest;
        select.dispatchEvent(new Event("change", { bubbles: true }));
      }
    }),
  );
  const cards = [...document.querySelectorAll(".product")];
  const filterButtons = [...document.querySelectorAll("[data-filter]")];
  const applyFilter = (button, updateUrl = false) => {
    document.querySelectorAll("[data-filter]").forEach((other) => {
      const active = other === button;
      other.classList.toggle("is-active", active);
      other.setAttribute("aria-pressed", String(active));
    });
    cards.forEach((card) => {
      card.hidden =
        button.dataset.filter !== "all" &&
        card.dataset.technique !== button.dataset.filter;
    });
    const count = cards.filter((card) => !card.hidden).length;
    document.querySelector(".catalog-empty").hidden =
      count > 0 || cards.length === 0;
    document.querySelector(".result-count").textContent =
      `${count} ${count === 1 ? "posibilidad" : "posibilidades"}`;
    window.ScrollTrigger?.refresh();
    document.dispatchEvent(new Event("jazar:filter"));
    if (updateUrl) {
      const url = new URL(location.href);
      if (button.dataset.filter === "all") url.searchParams.delete("tecnica");
      else url.searchParams.set("tecnica", button.dataset.filter);
      history.pushState({}, "", url);
    }
  };
  filterButtons.forEach((button) =>
    button.addEventListener("click", () => applyFilter(button, true)),
  );
  document
    .querySelector("[data-reset-filter]")
    ?.addEventListener("click", () => {
      applyFilter(filterButtons[0], true);
      filterButtons[0].focus();
    });
  const restoreFilter = () => {
    const value = new URL(location.href).searchParams.get("tecnica") || "all";
    applyFilter(
      filterButtons.find((button) => button.dataset.filter === value) ||
        filterButtons[0],
    );
  };
  if (filterButtons.length) {
    restoreFilter();
    window.addEventListener("popstate", restoreFilter);
  }
  document.querySelectorAll(".field-error").forEach((error) => {
    const input = document.querySelector(`#${error.id.replace(/_error$/, "")}`);
    input?.setAttribute("aria-invalid", "true");
    input?.setAttribute("aria-describedby", error.id);
  });
  const form = document.querySelector("#contact-form");
  document.querySelectorAll("[data-goto-step]").forEach((button) => {
    button.addEventListener("click", () => {
      document
        .querySelector(`#paso-${button.dataset.gotoStep}`)
        ?.scrollIntoView({
          block: "center",
          behavior: matchMedia("(prefers-reduced-motion: reduce)").matches
            ? "instant"
            : "smooth",
        });
    });
  });
  let dirty = false;
  form?.addEventListener("input", () => {
    dirty = true;
  });
  window.addEventListener("beforeunload", (event) => {
    if (dirty) {
      event.preventDefault();
      event.returnValue = "";
    }
  });
  form?.addEventListener("submit", () => {
    dirty = false;
    const button = form.querySelector("[type=submit]");
    button.disabled = true;
    button.querySelector("span").textContent = "Enviando…";
  });
  window.addEventListener("pageshow", () => {
    const button = form?.querySelector("[type=submit]");
    if (button) {
      button.disabled = false;
      button.querySelector("span").textContent = "Enviar mi idea";
    }
  });
  const firstError = document.querySelector("[aria-invalid=true]");
  if (firstError) firstError.focus();
  else document.querySelector(".form-status")?.focus({ preventScroll: true });
})();
