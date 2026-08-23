(function () {
  const LANG_KEY = "gabay_lang";

  function currentLang() {
    return localStorage.getItem(LANG_KEY) || "zh";
  }

  function applyLang(lang) {
    const resolved = lang === "en" ? "en" : "zh";
    localStorage.setItem(LANG_KEY, resolved);
    document.documentElement.lang = resolved === "en" ? "en" : "zh-CN";
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const zh = el.getAttribute("data-zh");
      const en = el.getAttribute("data-en");
      if (zh == null || en == null) return;
      el.textContent = resolved === "en" ? en : zh;
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
      const zh = el.getAttribute("data-zh-ph");
      const en = el.getAttribute("data-en-ph");
      if (zh == null || en == null) return;
      el.setAttribute("placeholder", resolved === "en" ? en : zh);
    });
    document.querySelectorAll(".lang-toggle button").forEach((btn) => {
      btn.classList.toggle("is-active", btn.dataset.lang === resolved);
    });
    document.dispatchEvent(new CustomEvent("gabay:lang", { detail: { lang: resolved } }));
  }

  function mountLangToggle(host) {
    if (!host || host.querySelector(".lang-toggle")) return;
    const wrap = document.createElement("div");
    wrap.className = "lang-toggle";
    wrap.innerHTML =
      '<button type="button" data-lang="zh">中文</button>' +
      '<button type="button" data-lang="en">EN</button>';
    wrap.addEventListener("click", (e) => {
      const btn = e.target.closest("button[data-lang]");
      if (!btn) return;
      applyLang(btn.dataset.lang);
    });
    host.appendChild(wrap);
  }

  function csrfToken() {
    const m = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : "";
  }

  function mountTutor(root) {
    if (!root || root.dataset.ready === "1") return;
    root.dataset.ready = "1";

    const ctx = {
      exam: root.dataset.exam || "",
      subject_slug: root.dataset.subject || "",
      section_slug: root.dataset.section || "",
      label: root.dataset.label || "Gabay",
      chapters: [],
    };
    const chaptersNode = document.getElementById("tutor-chapters");
    if (chaptersNode) {
      try {
        ctx.chapters = JSON.parse(chaptersNode.textContent || "[]");
      } catch (_) {
        ctx.chapters = [];
      }
    }

    const chapterOptions = ['<option value="">' + "整科 / Whole subject" + "</option>"]
      .concat(
        ctx.chapters.map(
          (c) => `<option value="${c.replace(/"/g, "&quot;")}">${c}</option>`
        )
      )
      .join("");

    root.innerHTML = `
      <div class="tutor-head">
        <div>
          <h2 data-i18n data-zh="MiniMax 学习教练" data-en="MiniMax Study Coach">MiniMax 学习教练</h2>
          <p data-i18n data-zh="基于当前科目大纲 · 模型 MiniMax-M3" data-en="Grounded in this subject's outline · MiniMax-M3">基于当前科目大纲 · 模型 MiniMax-M3</p>
        </div>
        <div class="lang-slot"></div>
      </div>
      <div class="tutor-controls">
        <select class="tutor-chapter" aria-label="chapter">${chapterOptions}</select>
        <button type="button" data-mode="explain" data-i18n data-zh="讲解章节" data-en="Explain">讲解章节</button>
        <button type="button" data-mode="quiz" data-i18n data-zh="出一题" data-en="Quiz me">出一题</button>
      </div>
      <div class="tutor-log" aria-live="polite"></div>
      <form class="tutor-form">
        <textarea class="tutor-input" rows="2" data-i18n-placeholder data-zh-ph="问这一科 / 这一章…" data-en-ph="Ask about this subject or chapter…" placeholder="问这一科 / 这一章…"></textarea>
        <button class="btn btn-primary" type="submit" data-i18n data-zh="发送" data-en="Send">发送</button>
      </form>
    `;

    mountLangToggle(root.querySelector(".lang-slot"));
    applyLang(currentLang());

    const log = root.querySelector(".tutor-log");
    const form = root.querySelector(".tutor-form");
    const input = root.querySelector(".tutor-input");
    const chapterSel = root.querySelector(".tutor-chapter");

    function addBubble(role, text) {
      const div = document.createElement("div");
      div.className = `tutor-bubble ${role}`;
      div.textContent = text;
      log.appendChild(div);
      log.scrollTop = log.scrollHeight;
    }

    addBubble(
      "system",
      currentLang() === "en"
        ? `Ready for ${ctx.label}. Pick a chapter, ask, explain, or quiz.`
        : `已加载：${ctx.label}。可选章节后提问、讲解或出题。`
    );

    async function run(mode, message) {
      addBubble("user", message || (mode === "explain" ? "讲解章节" : mode === "quiz" ? "出一题" : message));
      const pending = document.createElement("div");
      pending.className = "tutor-bubble system";
      pending.textContent = currentLang() === "en" ? "Thinking…" : "思考中…";
      log.appendChild(pending);
      log.scrollTop = log.scrollHeight;

      try {
        const res = await fetch("/api/study/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken(),
          },
          credentials: "same-origin",
          body: JSON.stringify({
            mode,
            message,
            exam: ctx.exam,
            subject_slug: ctx.subject_slug,
            section_slug: ctx.section_slug,
            chapter: chapterSel.value,
            lang: currentLang(),
          }),
        });
        const data = await res.json();
        pending.remove();
        if (!data.ok) {
          addBubble("system", data.error || "Request failed");
          return;
        }
        addBubble("assistant", data.answer);
      } catch (err) {
        pending.remove();
        addBubble("system", String(err));
      }
    }

    root.querySelectorAll(".tutor-controls button[data-mode]").forEach((btn) => {
      btn.addEventListener("click", () => run(btn.dataset.mode, ""));
    });

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const msg = input.value.trim();
      if (!msg) return;
      input.value = "";
      run("ask", msg);
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-lang-host]").forEach(mountLangToggle);
    applyLang(currentLang());
    document.querySelectorAll(".tutor[data-tutor]").forEach(mountTutor);
  });
})();
