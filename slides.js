// The home page's hero: the six games one after another (every few seconds, paused while the tab is hidden),
// the game's name and a dot for each in the corner.
(function () {
  var slides = document.querySelectorAll(".slide");
  var names = document.querySelectorAll(".now-name");
  var dots = document.querySelectorAll(".now-dots i");
  if (slides.length < 2) return;
  var current = 0;
  function show(next) {
    [slides, names, dots].forEach(function (list) {
      if (list[current]) list[current].classList.remove("on");
      if (list[next]) {
        // Restart the slow zoom from the beginning each time.
        if (list === slides) { void list[next].offsetWidth; }
        list[next].classList.add("on");
      }
    });
    current = next;
  }
  // Load the rest once the first is showing, so the first paint is quick.
  window.addEventListener("load", function () {
    slides.forEach(function (slide) { new Image().src = slide.style.backgroundImage.slice(5, -2); });
  });
  setInterval(function () {
    if (!document.hidden) show((current + 1) % slides.length);
  }, 3500);
})();
