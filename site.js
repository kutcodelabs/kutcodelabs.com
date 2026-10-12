// The home page's moving parts: the header over the hero, the game picker, things easing in as they
// scroll into view, and the games list that swaps the big picture beside it.
(function () {
  var root = document.documentElement;
  root.classList.add("js");
  function all(selector) { return Array.prototype.slice.call(document.querySelectorAll(selector)); }

  // The header sits clear over the hero, then turns white once the page moves.
  var top = document.querySelector(".top.over");
  function onScroll() { if (top) top.classList.toggle("scrolled", window.scrollY > 24); }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // Hero: a game every few seconds; a thumbnail jumps to its game and restarts the timer.
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

  // Games: whichever entry is in the middle of the screen lights up and takes the big picture.
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
