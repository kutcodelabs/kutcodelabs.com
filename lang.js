// Turkish or English.
// Pages that exist in both languages at their own addresses (/ and /en/) say which one they are
// (data-fixed-lang); the TR/EN buttons then go to the other address, and a visitor who once picked the
// other language is taken there. Pages kept in both languages at one address (the privacy policy) show
// the visitor's choice, else the browser's language, and point the menu at that language's pages.
(function () {
  var root = document.documentElement;
  var fixed = root.getAttribute("data-fixed-lang");
  var saved = null;
  try { saved = localStorage.getItem("kutcode-lang"); } catch (e) {}
  function remember(l) { try { localStorage.setItem("kutcode-lang", l); } catch (e) {} }
  // The other language's address on this same site (the tags hold full addresses).
  function other(l) {
    var link = document.querySelector('link[rel="alternate"][hreflang="' + l + '"]');
    return link ? link.getAttribute("href").replace(/^https?:\/\/[^/]+/, "") : null;
  }

  if (fixed && saved && saved !== fixed && other(saved)) {
    location.replace(other(saved) + location.hash);
    return;
  }

  var lang = fixed || saved || ((navigator.language || "tr").toLowerCase().indexOf("tr") === 0 ? "tr" : "en");
  function set(next) {
    lang = next;
    root.setAttribute("data-lang", next);
    root.setAttribute("lang", next);
    var title = root.getAttribute("data-title-" + next);
    if (title) document.title = title;
    if (fixed) return;
    // The menu leads to the pages in the language being read.
    Array.prototype.forEach.call(document.querySelectorAll("a[href^='/']"), function (a) {
      var href = a.getAttribute("data-href") || a.getAttribute("href");
      if (!/^\/(#|motionarea\/(#|$)|$)/.test(href)) return;
      a.setAttribute("data-href", href);
      a.setAttribute("href", next === "en" ? "/en" + href : href);
    });
  }
  set(lang);

  document.addEventListener("click", function (event) {
    var button = event.target.closest("[data-set]");
    if (!button) return;
    var next = button.getAttribute("data-set");
    remember(next);
    if (!fixed) { set(next); return; }
    if (next !== fixed && other(next)) location.href = other(next) + location.hash;
  });
  var year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();
})();
