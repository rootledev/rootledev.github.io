/* rootle site behavior: palette picker + copy buttons.
   Palettes are pure CSS (html[data-palette] blocks in site.css); this
   script only sets the attribute and persists the choice so docs pages
   pick it up too. No dependencies. */
(function () {
  var KEY = "rootle-palette";
  var DEFAULT = "hone";

  function apply(name) {
    if (name && name !== DEFAULT) {
      document.documentElement.setAttribute("data-palette", name);
    } else {
      document.documentElement.removeAttribute("data-palette");
    }
    var buttons = document.querySelectorAll("[data-set-palette]");
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].classList.toggle(
        "active",
        buttons[i].getAttribute("data-set-palette") === (name || DEFAULT)
      );
    }
    // Docs rail: name the active palette — a misclick on the unlabeled
    // dots is otherwise invisible ("why is the site golden?").
    var labels = document.querySelectorAll("[data-palette-name]");
    for (var j = 0; j < labels.length; j++) {
      labels[j].textContent = name === "paper-dark" ? "Paper Dark" : name || DEFAULT;
    }
    // Each app palette has its own recording; Hone is the canonical demo.
    var demo = document.querySelector("[data-demo-img]");
    if (demo) {
      var canonical = "./assets/demo.gif";
      var themed =
        name && name !== DEFAULT
          ? "./assets/img/demo-" + name + ".gif" : canonical;
      demo.onerror = function () {
        if (demo.getAttribute("src") !== canonical) demo.src = canonical;
      };
      if (demo.getAttribute("src") !== themed) demo.src = themed;
    }
  }

  var stored = null;
  try { stored = localStorage.getItem(KEY); } catch (e) { /* private mode */ }
  apply(stored);

  // ---- hero installer: one command box, method pills swap it ----
  var RELEASES = '<a href="https://github.com/rootledev/rootle/releases">tarballs \u2197</a>';
  var INSTALLS = {
    curl: {
      cmd: "curl -fsSL https://rootle.dev/install.sh | sh",
      note: "prebuilt binary \u00b7 x86_64 + arm64 \u00b7 " + RELEASES,
      update: "rootle self-update",
    },
    cargo: {
      cmd: "cargo install rootle --locked",
      note: "from crates.io \u2014 builds from source on Linux \u00b7 Rust 1.100+",
      update: "cargo install rootle --locked",
    },
    mise: {
      cmd: "mise use cargo:rootle",
      note: "pinned per-project via mise\u2019s cargo backend \u00b7 " + RELEASES,
      update: "mise up rootle",
    },
  };

  function setInstall(name) {
    var data = INSTALLS[name];
    if (!data) return;
    var pills = document.querySelectorAll("[data-install]");
    for (var i = 0; i < pills.length; i++) {
      var on = pills[i].getAttribute("data-install") === name;
      pills[i].classList.toggle("active", on);
      pills[i].setAttribute("aria-pressed", on ? "true" : "false");
    }
    var cmd = document.querySelector("[data-install-cmd]");
    if (cmd) cmd.textContent = data.cmd;
    var copy = document.querySelector("[data-install-copy]");
    if (copy) copy.setAttribute("data-copy", data.cmd);
    var note = document.querySelector("[data-install-note]");
    if (note) note.innerHTML = data.note;
    var upd = document.querySelector("[data-install-update]");
    if (upd) upd.textContent = data.update;
  }


  document.addEventListener("click", function (ev) {
    var target = ev.target;
    var pill = target.closest ? target.closest("[data-install]") : null;
    if (pill) {
      setInstall(pill.getAttribute("data-install"));
      return;
    }
    var pal = target.closest ? target.closest("[data-set-palette]") : null;
    if (pal) {
      var name = pal.getAttribute("data-set-palette");
      apply(name);
      try { localStorage.setItem(KEY, name === DEFAULT ? "" : name); } catch (e) {}
      return;
    }
    var copy = target.closest ? target.closest("[data-copy]") : null;
    if (copy) {
      var text = copy.getAttribute("data-copy");
      var done = function () {
        // Whole-command copy cards (install grid) carry a nested hint
        // span — flip that, not the command text itself.
        var labelEl = copy.querySelector("[data-copy-label]") || copy;
        var label = labelEl.textContent;
        labelEl.textContent = "copied";
        labelEl.classList.add("ok");
        setTimeout(function () {
          labelEl.textContent = label;
          labelEl.classList.remove("ok");
        }, 1200);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, done);
      } else {
        var ta = document.createElement("textarea");
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand("copy"); } catch (e) {}
        ta.remove();
        done();
      }
    }
  });
})();
