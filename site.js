// The site's moving parts: the header (its strip folds on scroll, its menu on small screens), the endless
// picture columns, the slideshow, things easing in as they scroll into view, and the games list.
(function () {
  var root = document.documentElement;
  function all(selector) { return Array.prototype.slice.call(document.querySelectorAll(selector)); }

  // Each mosaic column gets a second copy of its tiles, so sliding it by half loops without a seam.
  all(".grid .col").forEach(function (col) {
    Array.prototype.slice.call(col.children).forEach(function (cell) { col.appendChild(cell.cloneNode(true)); });
  });
  root.classList.add("js");

  // Header: the top strip folds away once the page moves.
  var hdr = document.querySelector(".hdr");
  function onScroll() { if (hdr) hdr.classList.toggle("scrolled", window.scrollY > 24); }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // Menu on small screens: the button opens it; Escape, a click outside or picking a link closes it.
  var menuBtn = document.querySelector(".menu-btn");
  var panel = document.querySelector(".panel");
  function setMenu(open, focus) {
    if (!hdr || !menuBtn) return;
    hdr.setAttribute("data-open", open ? "true" : "false");
    menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
    if (open && focus && panel) { var first = panel.querySelector("a"); if (first) first.focus(); }
  }
  if (menuBtn) {
    menuBtn.addEventListener("click", function (e) {
      // A click with no pointer position came from the keyboard.
      setMenu(hdr.getAttribute("data-open") !== "true", e.detail === 0);
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false); });
    document.addEventListener("click", function (e) { if (hdr && !hdr.contains(e.target)) setMenu(false); });
    if (panel) panel.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
  }

  // Slideshow (MotionArea page): a game every few seconds; a thumbnail jumps to its game.
  var slides = all(".slide"), picks = all(".pick button"), current = 0, timer = null;
  var EVERY = 3500;
  root.style.setProperty("--every", EVERY + "ms");
  function show(next) {
    [slides, picks].forEach(function (list) {
      if (list[current]) list[current].classList.remove("on");
      if (list[next]) { void list[next].offsetWidth; list[next].classList.add("on"); }
    });
    picks.forEach(function (p, i) { p.setAttribute("aria-selected", i === next ? "true" : "false"); });
    current = next;
  }
  function start() {
    clearInterval(timer);
    timer = setInterval(function () { if (!document.hidden) show((current + 1) % slides.length); }, EVERY);
  }
  if (slides.length > 1) {
    picks.forEach(function (p, i) { p.addEventListener("click", function () { show(i); start(); }); });
    show(0);
    start();
    window.addEventListener("load", function () {
      slides.forEach(function (slide) { new Image().src = slide.style.backgroundImage.slice(5, -2); });
    });
  }

  // Ease things in as they arrive.
  var reveal = all("[data-reveal]");
  if ("IntersectionObserver" in window) {
    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); seen.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -8% 0px" });
    reveal.forEach(function (el) { seen.observe(el); });
  } else {
    reveal.forEach(function (el) { el.classList.add("in"); });
  }

  // Games (MotionArea page): whichever entry is in the middle of the screen takes the big picture.
  var games = all(".g"), shots = all(".stage img"), num = document.querySelector(".stage-num");
  var stage = document.querySelector(".stage");
  function pickGame(i) {
    games.forEach(function (g, k) { g.classList.toggle("on", k === i); });
    shots.forEach(function (s, k) { s.classList.toggle("on", k === i); });
    if (num) num.textContent = (i < 9 ? "0" : "") + (i + 1);
    if (stage) stage.style.setProperty("--accent", games[i].style.getPropertyValue("--accent"));
  }
  if ("IntersectionObserver" in window && games.length) {
    var middle = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) pickGame(games.indexOf(e.target)); });
    }, { rootMargin: "-48% 0px -48% 0px" });
    games.forEach(function (g) { middle.observe(g); });
    pickGame(0);
  }
})();
