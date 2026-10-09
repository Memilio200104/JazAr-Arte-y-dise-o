(() => {
  if (!window.gsap || !window.ScrollTrigger) return;
  gsap.registerPlugin(ScrollTrigger);
  const media = gsap.matchMedia();
  media.add("(prefers-reduced-motion: no-preference)", () => {
    gsap.from(".hero-content > :not(h1)", {
      y: 18,
      opacity: 0,
      duration: 0.7,
      stagger: 0.07,
      ease: "power3.out",
      clearProps: "all",
    });
    document
      .querySelectorAll(
        ".section-heading, .intro > div, .brand-portrait, .package",
      )
      .forEach((section) => {
        gsap.from(section, {
          y: 32,
          opacity: 0,
          duration: 0.7,
          ease: "power3.out",
          clearProps: "all",
          scrollTrigger: { trigger: section, start: "top 92%", once: true },
        });
      });
    document.querySelectorAll(".product").forEach((card, index) => {
      gsap.from(card, {
        y: 28,
        opacity: 0,
        duration: 0.6,
        delay: (index % 3) * 0.06,
        clearProps: "all",
        scrollTrigger: { trigger: card, start: "top 94%", once: true },
      });
    });
    const header = document.querySelector(".site-header");
    ScrollTrigger.create({
      start: 0,
      end: "max",
      onUpdate: (self) =>
        header.style.setProperty("--reading-progress", self.progress),
    });
    const onFilter = () => {
      const cards = [...document.querySelectorAll(".product:not([hidden])")];
      gsap.killTweensOf(cards);
      gsap.fromTo(
        cards,
        { opacity: 0.35, y: 8 },
        { opacity: 1, y: 0, duration: 0.25, stagger: 0.035, clearProps: "all" },
      );
    };
    document.addEventListener("jazar:filter", onFilter);
    return () => {
      document.removeEventListener("jazar:filter", onFilter);
      header.style.removeProperty("--reading-progress");
      gsap.killTweensOf(".product");
      gsap.set(".product", { clearProps: "opacity,transform" });
    };
  });
  media.add(
    "(min-width:1024px) and (min-height:760px) and (prefers-reduced-motion:no-preference)",
    () => {
      const heroStory = gsap.timeline({
        scrollTrigger: {
          id: "hero-story",
          trigger: ".hero",
          start: () => `top top+=${document.querySelector('.site-header').offsetHeight}`,
          end: () => `+=${Math.round(window.innerHeight * .85)}`,
          pin: true,
          scrub: 0.4,
          invalidateOnRefresh: true,
        },
      });
      heroStory
        .to('.hero-image', { scale: 1.14, y: -28, transformOrigin: '75% 50%', ease: 'none', duration: 1 }, 0)
        .to('.hero h1', { y: -22, ease: 'none', duration: 1 }, 0)
        .fromTo('.hero-edition', { y: 0 }, { y: 120, ease: 'none', duration: 1 }, 0);
    },
  );
  media.add(
    "(min-width:1024px) and (min-height:600px) and (prefers-reduced-motion:no-preference)",
    () => {
      gsap.fromTo(
        ".brand-portrait img",
        { y: 10 },
        {
          y: -10,
          ease: "none",
          scrollTrigger: {
            trigger: ".intro",
            start: "top bottom",
            end: "bottom top",
            scrub: 0.45,
          },
        },
      );
      const number = document.querySelector("#process-number");
      const label = document.querySelector("#process-label");
      const progress = document.querySelector(".process-progress span");
      const layers = [...document.querySelectorAll("[data-frame]")];
      const buttons = [...document.querySelectorAll("[data-goto-step]")];
      const steps = [...document.querySelectorAll("[data-step]")];
      let current = "1";
      const update = (step) => {
        const selected = step.dataset.step;
        number.textContent = "0" + selected;
        label.textContent = step.dataset.label;
        progress.style.transform = "scaleX(" + Number(selected) / 5 + ")";
        buttons.forEach((button) =>
          button.setAttribute(
            "aria-pressed",
            String(button.dataset.gotoStep === selected),
          ),
        );
        steps.forEach((item) =>
          item.classList.toggle("is-current", item === step),
        );
        if (current === selected) return;
        current = selected;
        layers.forEach((layer) => {
          const active = layer.dataset.frame === selected;
          layer.classList.toggle("is-current", active);
          gsap.to(layer, {
            autoAlpha: active ? 1 : 0,
            duration: 0.35,
            overwrite: true,
          });
          if (active)
            gsap.fromTo(
              layer.querySelector("img"),
              { y: 10 },
              { y: 0, duration: 0.6, ease: "power2.out", overwrite: "auto" },
            );
        });
      };
      steps.forEach((step) =>
        ScrollTrigger.create({
          trigger: step,
          start: "top center",
          end: "bottom center",
          onEnter: () => update(step),
          onEnterBack: () => update(step),
        }),
      );
      return () => {
        number.textContent = "01";
        label.textContent = "La idea";
        progress.style.transform = "scaleX(.2)";
        layers.forEach((layer) =>
          layer.classList.toggle("is-current", layer.dataset.frame === "1"),
        );
        buttons.forEach((button) =>
          button.setAttribute(
            "aria-pressed",
            String(button.dataset.gotoStep === "1"),
          ),
        );
        steps.forEach((step) => step.classList.remove("is-current"));
      };
    },
  );
  document.fonts.ready.then(() => ScrollTrigger.refresh());
  window.addEventListener("load", () => ScrollTrigger.refresh(), {
    once: true,
  });
})();
