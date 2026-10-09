(() => {
  if (!window.gsap || !window.ScrollTrigger) return;
  gsap.registerPlugin(ScrollTrigger);
  const media = gsap.matchMedia();
  media.add("(prefers-reduced-motion: no-preference)", () => {
    gsap.from(".hero-content > :not(h1)", {
      y: 14,
      opacity: 0,
      duration: 0.55,
      stagger: 0.06,
      ease: "power2.out",
      clearProps: "all",
    });
    document
      .querySelectorAll(".section-heading, .intro > div, .package")
      .forEach((section) => {
        gsap.from(section, {
          y: 24,
          opacity: 0,
          duration: 0.55,
          ease: "power2.out",
          clearProps: "all",
          scrollTrigger: { trigger: section, start: "top 92%", once: true },
        });
      });
  });
  media.add(
    "(min-width:1024px) and (min-height:760px) and (prefers-reduced-motion:no-preference)",
    () => {
      gsap.to(".hero-image", {
        y: -32,
        scale: 1.025,
        ease: "none",
        scrollTrigger: {
          trigger: ".hero",
          start: "top top",
          end: "bottom top",
          scrub: 0.4,
        },
      });
      const number = document.querySelector("#process-number");
      const label = document.querySelector("#process-label");
      const progress = document.querySelector(".process-progress span");
      const update = (step) => {
        number.textContent = `0${step.dataset.step}`;
        label.textContent = step.dataset.label;
        progress.style.transform = `scaleX(${Number(step.dataset.step) / 5})`;
        gsap.to(".process-image-wrap img", {
          scale: 1 + (Number(step.dataset.step) - 1) * 0.012,
          y: Number(step.dataset.step) % 2 ? 0 : -8,
          duration: 0.35,
          overwrite: true,
        });
      };
      document
        .querySelectorAll("[data-step]")
        .forEach((step) =>
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
      };
    },
  );
  document.fonts.ready.then(() => ScrollTrigger.refresh());
  window.addEventListener("load", () => ScrollTrigger.refresh(), {
    once: true,
  });
})();
