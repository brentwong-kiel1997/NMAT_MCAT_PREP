(function () {
  const LANG_KEY = "gabay_lang";

  function currentLang() {
    return localStorage.getItem(LANG_KEY) || "zh";
  }

  function applyLang(lang) {
    const resolved = lang === "en" ? "en" : "zh";
    localStorage.setItem(LANG_KEY, resolved);
    document.documentElement.lang = resolved === "en" ? "en" : "zh-CN";
    document.documentElement.dataset.lang = resolved;
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

  function readJson(el) {
    if (!el) return null;
    try {
      return JSON.parse(el.textContent || "null");
    } catch (_) {
      return null;
    }
  }

  function mountProgress(root) {
    if (!root || root.dataset.ready === "1") return;
    root.dataset.ready = "1";
    const key = root.dataset.progressKey || "gabay_progress";
    const subject = root.dataset.progressSubject || "";
    const checks = Array.from(document.querySelectorAll(".progress-check"));
    if (!checks.length) return;

    let saved = {};
    try {
      saved = JSON.parse(localStorage.getItem(key) || "{}") || {};
    } catch (_) {
      saved = {};
    }

    const countEl = root.querySelector(".progress-count");
    const totalEl = root.querySelector(".progress-total");
    const fill = root.querySelector(".progress-fill");
    if (totalEl) totalEl.textContent = String(checks.length);

    function persist() {
      localStorage.setItem(key, JSON.stringify(saved));
    }

    function refresh() {
      let n = 0;
      checks.forEach((box) => {
        const id = box.dataset.chapterId;
        const on = !!saved[id];
        box.checked = on;
        const item = box.closest(".chapter-item");
        if (item) item.classList.toggle("is-done", on);
        if (on) n += 1;
      });
      if (countEl) countEl.textContent = String(n);
      if (fill) fill.style.width = checks.length ? `${(100 * n) / checks.length}%` : "0%";
    }

    async function syncFromServer() {
      if (!subject) return;
      try {
        const res = await fetch(
          "/api/progress/?subject_slug=" + encodeURIComponent(subject),
          { credentials: "same-origin" }
        );
        const data = await res.json();
        if (!data.ok || !data.done) return;
        saved = Object.assign({}, saved, data.done);
        persist();
        refresh();
      } catch (_) {}
    }

    async function pushChapter(id, done) {
      if (!subject) return;
      try {
        await fetch("/api/progress/update/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken(),
          },
          credentials: "same-origin",
          body: JSON.stringify({
            subject_slug: subject,
            chapter_id: id,
            done: !!done,
          }),
        });
      } catch (_) {}
    }

    checks.forEach((box) => {
      box.addEventListener("change", () => {
        const id = box.dataset.chapterId;
        if (box.checked) saved[id] = 1;
        else delete saved[id];
        persist();
        refresh();
        pushChapter(id, box.checked);
      });
    });

    const reset = root.querySelector(".progress-reset");
    if (reset) {
      reset.addEventListener("click", () => {
        const ids = Object.keys(saved);
        saved = {};
        persist();
        refresh();
        ids.forEach((id) => pushChapter(id, false));
      });
    }
    refresh();
    syncFromServer();
  }

  function mountFlashcards(panel) {
    if (!panel || panel.dataset.ready === "1") return;
    panel.dataset.ready = "1";
    const cards = readJson(panel.querySelector(".flash-data")) || [];
    if (!cards.length) return;

    let i = 0;
    let flipped = false;
    const chapterEl = panel.querySelector(".flash-chapter");
    const indexEl = panel.querySelector(".flash-index");
    const cardBtn = panel.querySelector(".flash-card");

    function paint() {
      const c = cards[i];
      if (chapterEl) chapterEl.textContent = c.chapter || "";
      const zhFront = panel.querySelector(".flash-front.only-zh");
      const enFront = panel.querySelector(".flash-front.only-en");
      const zhBack = panel.querySelector(".flash-back.only-zh");
      const enBack = panel.querySelector(".flash-back.only-en");
      if (zhFront) {
        zhFront.textContent = "点按翻转 · 回忆要点";
        zhFront.hidden = flipped;
      }
      if (enFront) {
        enFront.textContent = "Tap to flip · recall the point";
        enFront.hidden = flipped;
      }
      if (zhBack) {
        zhBack.textContent = c.zh || "";
        zhBack.hidden = !flipped;
      }
      if (enBack) {
        enBack.textContent = c.en || "";
        enBack.hidden = !flipped;
      }
      if (indexEl) indexEl.textContent = String(i + 1);
      if (cardBtn) cardBtn.classList.toggle("is-flipped", flipped);
    }

    function go(delta) {
      i = (i + delta + cards.length) % cards.length;
      flipped = false;
      paint();
    }

    cardBtn && cardBtn.addEventListener("click", () => {
      flipped = !flipped;
      paint();
    });
    panel.querySelector(".flash-flip")?.addEventListener("click", () => {
      flipped = !flipped;
      paint();
    });
    panel.querySelector(".flash-prev")?.addEventListener("click", () => go(-1));
    panel.querySelector(".flash-next")?.addEventListener("click", () => go(1));
    document.addEventListener("gabay:lang", paint);
    paint();
  }

  function mountPractice(root) {
    if (!root || root.dataset.ready === "1") return;
    root.dataset.ready = "1";
    const items = readJson(root.querySelector(".practice-data")) || [];
    if (!items.length) return;

    const key = root.dataset.practiceKey || "gabay_practice";
    let state = { i: 0, score: 0, answered: {} };
    try {
      state = Object.assign(state, JSON.parse(localStorage.getItem(key) || "{}"));
    } catch (_) {}

    const posEl = root.querySelector(".practice-pos");
    const scoreEl = root.querySelector(".practice-score");
    const chapterEl = root.querySelector(".practice-chapter");
    const qZh = root.querySelector(".practice-q.only-zh");
    const qEn = root.querySelector(".practice-q.only-en");
    const choicesEl = root.querySelector(".practice-choices");
    const feedback = root.querySelector(".practice-feedback");
    const verdict = root.querySelector(".practice-verdict");
    const explainZh = root.querySelector(".practice-explain.only-zh");
    const explainEn = root.querySelector(".practice-explain.only-en");

    function save() {
      localStorage.setItem(
        key,
        JSON.stringify({ i: state.i, score: state.score, answered: state.answered })
      );
    }

    function showFeedback(item, pick) {
      const ok = pick === item.answer;
      feedback.hidden = false;
      verdict.textContent =
        currentLang() === "en"
          ? ok
            ? `Correct · ${item.answer}`
            : `Incorrect · answer ${item.answer}`
          : ok
            ? `正确 · ${item.answer}`
            : `不对 · 答案 ${item.answer}`;
      verdict.className = "practice-verdict " + (ok ? "is-ok" : "is-bad");
      if (explainZh) explainZh.textContent = item.explain_zh || "";
      if (explainEn) explainEn.textContent = item.explain_en || "";
    }

    function paint() {
      const item = items[state.i];
      if (posEl) posEl.textContent = String(state.i + 1);
      if (scoreEl) scoreEl.textContent = String(state.score);
      if (chapterEl) chapterEl.textContent = item.chapter || "";
      if (qZh) qZh.textContent = item.q_zh || "";
      if (qEn) qEn.textContent = item.q_en || "";
      choicesEl.innerHTML = "";
      const prior = state.answered[item.id];
      ["A", "B", "C", "D"].forEach((letter) => {
        const choice = item.choices[letter];
        if (!choice) return;
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "practice-choice";
        btn.dataset.letter = letter;
        btn.innerHTML =
          `<strong>${letter}</strong> ` +
          `<span class="only-zh">${choice.zh}</span><span class="only-en">${choice.en}</span>`;
        if (prior) {
          btn.disabled = true;
          if (letter === item.answer) btn.classList.add("is-correct");
          if (letter === prior && prior !== item.answer) btn.classList.add("is-wrong");
        } else {
          btn.addEventListener("click", () => {
            if (state.answered[item.id]) return;
            state.answered[item.id] = letter;
            if (letter === item.answer) state.score += 1;
            save();
            paint();
            const subject = root.dataset.practiceSubject || "";
            if (subject) {
              fetch("/api/practice/attempt/", {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                  "X-CSRFToken": csrfToken(),
                },
                credentials: "same-origin",
                body: JSON.stringify({
                  subject_slug: subject,
                  question_id: item.id,
                  chosen: letter,
                }),
              }).catch(() => {});
            }
          });
        }
        choicesEl.appendChild(btn);
      });
      if (prior) showFeedback(item, prior);
      else {
        feedback.hidden = true;
      }
    }

    root.querySelector(".practice-prev")?.addEventListener("click", () => {
      state.i = Math.max(0, state.i - 1);
      save();
      paint();
    });
    root.querySelector(".practice-next")?.addEventListener("click", () => {
      state.i = Math.min(items.length - 1, state.i + 1);
      save();
      paint();
    });
    document.addEventListener("gabay:lang", paint);
    paint();
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

    let lastMode = null;
    let lastAssistant = "";

    function addBubble(role, text) {
      const div = document.createElement("div");
      div.className = `tutor-bubble ${role}`;
      div.textContent = text;
      log.appendChild(div);
      log.scrollTop = log.scrollHeight;
      if (role === "assistant") lastAssistant = text;
    }

    addBubble(
      "system",
      currentLang() === "en"
        ? `Ready for ${ctx.label}. Pick a chapter, ask, explain, or quiz.`
        : `已加载：${ctx.label}。可选章节后提问、讲解或出题。`
    );

    function looksLikeAnswer(msg) {
      return /^[ABCDabcd]([\s.、:：).-]|$)/.test((msg || "").trim());
    }

    async function run(mode, message) {
      let effectiveMode = mode;
      if (mode === "ask" && lastMode === "quiz" && looksLikeAnswer(message)) {
        effectiveMode = "grade";
        message = `上一题内容：\n${lastAssistant}\n\n我的答案：${message}`;
      }

      addBubble(
        "user",
        message ||
          (mode === "explain"
            ? currentLang() === "en"
              ? "Explain this chapter"
              : "讲解章节"
            : mode === "quiz"
              ? currentLang() === "en"
                ? "Quiz me"
                : "出一题"
              : message)
      );
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
            mode: effectiveMode,
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
        lastMode = effectiveMode === "grade" ? "ask" : effectiveMode;
        try {
          const key = "gabay_study_count";
          localStorage.setItem(key, String(Number(localStorage.getItem(key) || 0) + 1));
        } catch (_) {}
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
    document.querySelectorAll("[data-progress-root]").forEach(mountProgress);
    document.querySelectorAll("[data-flashcards]").forEach(mountFlashcards);
    document.querySelectorAll("[data-practice]").forEach(mountPractice);
  });
})();
