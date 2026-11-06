/*
 * Mohamed Nabil Pro — brand interactions (no dependencies, ~4 KB).
 * - sticky nav: scrolled state + accessible mobile menu
 * - hero: lightweight 3D point-sphere on <canvas> (pauses off-screen / reduced motion)
 * - 3D tilt for [data-tilt] cards on precise pointers
 */
(function () {
  "use strict";
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var finePointer = window.matchMedia("(pointer: fine)").matches;

  /* ---------- nav ---------- */
  var nav = document.getElementById("mnp-nav");
  var burger = document.querySelector(".mnp-burger");
  var menu = document.getElementById("mnp-menu");
  if (nav) {
    var onScroll = function () { nav.classList.toggle("scrolled", window.scrollY > 8); };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }
  if (burger && menu) {
    var setOpen = function (open) {
      burger.setAttribute("aria-expanded", String(open));
      document.body.classList.toggle("mnp-menu-open", open);
    };
    burger.addEventListener("click", function () {
      setOpen(burger.getAttribute("aria-expanded") !== "true");
    });
    menu.addEventListener("click", function (e) { if (e.target.closest("a")) setOpen(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") setOpen(false); });
    window.addEventListener("resize", function () { if (window.innerWidth > 1100) setOpen(false); });
  }

  /* ---------- reveal on scroll ---------- */
  var revealEls = document.querySelectorAll("[data-reveal]");
  if (reduce || !("IntersectionObserver" in window)) {
    revealEls.forEach(function (el) { el.classList.add("is-visible"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-visible"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    revealEls.forEach(function (el) { io.observe(el); });
  }

  /* ---------- 3D tilt ---------- */
  if (finePointer && !reduce) {
    document.querySelectorAll("[data-tilt]").forEach(function (el) {
      var max = parseFloat(el.getAttribute("data-tilt")) || 8;
      var raf = null;
      el.addEventListener("pointermove", function (e) {
        var r = el.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5;
        var y = (e.clientY - r.top) / r.height - 0.5;
        if (raf) cancelAnimationFrame(raf);
        raf = requestAnimationFrame(function () {
          el.style.transform = "perspective(900px) rotateX(" + (-y * max).toFixed(2) + "deg) rotateY(" + (x * max).toFixed(2) + "deg) translateZ(0)";
          el.style.setProperty("--mx", ((x + 0.5) * 100).toFixed(1) + "%");
          el.style.setProperty("--my", ((y + 0.5) * 100).toFixed(1) + "%");
        });
      });
      el.addEventListener("pointerleave", function () {
        if (raf) cancelAnimationFrame(raf);
        el.style.transform = "";
      });
    });
  }

  /* ---------- 3D point sphere ---------- */
  var canvas = document.getElementById("mnp-sphere");
  if (canvas && canvas.getContext) {
    var ctx = canvas.getContext("2d");
    var N = window.innerWidth < 640 ? 260 : 520;
    var pts = [];
    var golden = Math.PI * (3 - Math.sqrt(5));
    for (var i = 0; i < N; i++) {
      var y = 1 - (i / (N - 1)) * 2, rad = Math.sqrt(1 - y * y), th = golden * i;
      pts.push([Math.cos(th) * rad, y, Math.sin(th) * rad]);
    }
    var rotY = 0, rotX = 0.35, targetX = 0.35, targetY = 0, running = true, w = 0, h = 0, dpr = 1;
    var resize = function () {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = canvas.clientWidth; h = canvas.clientHeight;
      canvas.width = w * dpr; canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();
    window.addEventListener("resize", resize);
    if (finePointer && !reduce) {
      window.addEventListener("pointermove", function (e) {
        targetY = (e.clientX / window.innerWidth - 0.5) * 0.8;
        targetX = 0.35 + (e.clientY / window.innerHeight - 0.5) * 0.5;
      }, { passive: true });
    }
    var color = function () {
      return getComputedStyle(document.documentElement).getPropertyValue("--mnp-sphere").trim() || "129,140,248";
    };
    var rgb = color();
    new MutationObserver(function () { rgb = color(); }).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });

    var draw = function () {
      ctx.clearRect(0, 0, w, h);
      var R = Math.min(w, h) * 0.42, cx = w / 2, cy = h / 2;
      var cyR = Math.cos(rotY), syR = Math.sin(rotY), cxR = Math.cos(rotX), sxR = Math.sin(rotX);
      for (var k = 0; k < pts.length; k++) {
        var p = pts[k];
        var x1 = p[0] * cyR - p[2] * syR, z1 = p[0] * syR + p[2] * cyR;
        var y2 = p[1] * cxR - z1 * sxR, z2 = p[1] * sxR + z1 * cxR;
        var depth = (z2 + 1) / 2;               // 0 (back) .. 1 (front)
        var persp = 1 / (1.9 - z2 * 0.6);
        var sx = cx + x1 * R * persp * 1.3, sy = cy + y2 * R * persp * 1.3;
        ctx.beginPath();
        ctx.fillStyle = "rgba(" + rgb + "," + (0.12 + depth * 0.75).toFixed(3) + ")";
        ctx.arc(sx, sy, 0.6 + depth * 1.7, 0, 6.2832);
        ctx.fill();
      }
    };
    var spin = 0, offY = 0;
    var loop = function () {
      if (!running) return;
      spin += 0.0026;                         // constant slow spin
      offY += (targetY - offY) * 0.05;         // eased pointer parallax
      rotX += (targetX - rotX) * 0.05;
      rotY = spin + offY;
      draw();
      requestAnimationFrame(loop);
    };
    if (reduce) {
      draw();
    } else {
      if ("IntersectionObserver" in window) {
        new IntersectionObserver(function (entries) {
          var vis = entries[0].isIntersecting;
          if (vis && !running) { running = true; requestAnimationFrame(loop); }
          running = vis;
        }).observe(canvas);
      }
      requestAnimationFrame(loop);
    }
  }
})();
