// Turkish or English: the visitor's choice (remembered), else the browser's language.
(function () {
  var root = document.documentElement;
  var saved = null;
  try { saved = localStorage.getItem("kutcode-lang"); } catch (e) {}
  var lang = saved || ((navigator.language || "tr").toLowerCase().indexOf("tr") === 0 ? "tr" : "en");
  function set(next) {
    lang = next;
    root.setAttribute("data-lang", next);
    root.setAttribute("lang", next);
    var title = root.getAttribute("data-title-" + next);
    if (title) document.title = title;
    try { localStorage.setItem("kutcode-lang", next); } catch (e) {}
  }
  set(lang);
  document.addEventListener("click", function (event) {
    var button = event.target.closest("[data-set]");
    if (button) set(button.getAttribute("data-set"));
  });
  var year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();
})();
