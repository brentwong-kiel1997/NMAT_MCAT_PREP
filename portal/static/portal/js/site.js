(function () {
  function csrfToken() {
    const m = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    if (m) return decodeURIComponent(m[1]);
    const input = document.querySelector(".csrf-slot input[name=csrfmiddlewaretoken], input[name=csrfmiddlewaretoken]");
    return input ? input.value : "";
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
      const prompt = panel.querySelector(".flash-prompt");
      const answer = panel.querySelector(".flash-answer");
      if (chapterEl) chapterEl.textContent = c.chapter || "";
      if (prompt) {
        prompt.textContent = "Tap to flip · recall the point";
        prompt.hidden = flipped;
      }
      if (answer) {
        answer.textContent = c.text || "";
        answer.hidden = !flipped;
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
      const saved = JSON.parse(localStorage.getItem(key) || "{}");
      state = Object.assign(state, saved);
      // guard against a stored cursor from a different (longer) item set
      if (items.length && state.i >= items.length) { state.i = 0; state.score = 0; state.answered = {}; }
    } catch (_) {}

    const posEl = root.querySelector(".practice-pos");
    const scoreEl = root.querySelector(".practice-score");
    const chapterEl = root.querySelector(".practice-chapter");
    const qEl = root.querySelector(".practice-q");
    const choicesEl = root.querySelector(".practice-choices");
    const feedback = root.querySelector(".practice-feedback");
    const verdict = root.querySelector(".practice-verdict");
    const explainEl = root.querySelector(".practice-explain");

    function save() {
      localStorage.setItem(
        key,
        JSON.stringify({ i: state.i, score: state.score, answered: state.answered })
      );
    }

    function showFeedback(item, pick) {
      const serverJudge = root.dataset.serverJudge === "1";
      let ok = pick === item.answer;
      let answerText = item.answer;
      let explainText = item.explain || "";
      if (serverJudge) {
        const fb = (state.serverFeedback || {})[item.id];
        if (!fb) { feedback.hidden = true; return; }  // grading in flight
        ok = fb.correct;
        answerText = fb.answer;
        explainText = fb.explain || "";
      }
      feedback.hidden = false;
      verdict.textContent = ok
        ? `Correct · ${answerText}`
        : `Incorrect · answer ${answerText}`;
      verdict.className = "practice-verdict " + (ok ? "is-ok" : "is-bad");
      if (explainEl) explainEl.textContent = explainText;
    }

    function paint() {
      const item = items[state.i];
      if (posEl) posEl.textContent = String(state.i + 1);
      if (scoreEl) scoreEl.textContent = String(state.score);
      if (chapterEl) chapterEl.textContent = item.chapter || "";
      if (qEl) qEl.textContent = item.q || "";
      // render figure if the item has one (drill/exam items carry an
      // absolute /content-images/... URL under `figure`)
      const figSrc = item.figure || item.figure_url || "";
      const figParent = qEl ? qEl.parentElement : null;
      let figEl = figParent ? figParent.querySelector(".practice-figure") : null;
      if (figEl) figEl.remove();
      if (figSrc && figParent) {
        const img = document.createElement("img");
        img.src = figSrc;
        img.alt = "Item figure";
        img.className = "practice-figure";
        img.style.maxWidth = "100%";
        figParent.insertBefore(img, qEl.nextSibling);
      }
      choicesEl.innerHTML = "";
      const prior = state.answered[item.id];
      ["A", "B", "C", "D"].forEach((letter) => {
        const choice = item.choices[letter];
        if (!choice) return;
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "practice-choice";
        btn.dataset.letter = letter;
        const strong = document.createElement("strong");
        strong.textContent = letter;
        btn.append(strong, ` ${choice}`);
        if (prior) {
          btn.disabled = true;
          if (letter === item.answer) btn.classList.add("is-correct");
          if (letter === prior && prior !== item.answer) btn.classList.add("is-wrong");
        } else {
          btn.addEventListener("click", () => {
            if (state.answered[item.id]) return;
            const serverJudge = root.dataset.serverJudge === "1";
            state.answered[item.id] = letter;
            if (!serverJudge && letter === item.answer) state.score += 1;
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
              })
                .then((res) => (res.ok ? res.json() : null))
                .then((data) => {
                  if (!serverJudge) { return; }
                  if (!data) {
                    delete state.answered[item.id];
                    save();
                    paint();
                    return;
                  }
                  state.serverFeedback = state.serverFeedback || {};
                  state.serverFeedback[item.id] = {
                    correct: !!data.correct,
                    answer: data.answer || "",
                    explain: data.explain || "",
                  };
                  if (data.correct) state.score += 1;
                  save();
                  paint();
                })
                .catch(() => {
                  if (serverJudge) {
                    delete state.answered[item.id];
                    save();
                    paint();
                  }
                });
            }
          });
        }
        choicesEl.appendChild(btn);
      });
      if (prior) showFeedback(item, prior);
      else {
        feedback.hidden = true;
      }
      const prev = root.querySelector(".practice-prev");
      const next = root.querySelector(".practice-next");
      if (prev) prev.disabled = state.i <= 0;
      if (next) next.disabled = state.i >= items.length - 1;
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
      coach: root.dataset.coach || "AI Study Coach",
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

    const chapterOptions = ['<option value="">Whole subject</option>']
      .concat(
        ctx.chapters.map(
          (c) => `<option value="${c.replace(/"/g, "&quot;")}">${c}</option>`
        )
      )
      .join("");

    root.innerHTML = `
      <div class="tutor-head">
        <div>
          <h2>${ctx.coach}</h2>
          <p>Grounded in this subject's outline</p>
        </div>
      </div>
      <div class="tutor-controls">
        <select class="tutor-chapter" aria-label="chapter">${chapterOptions}</select>
        <button type="button" data-mode="explain">Explain</button>
        <button type="button" data-mode="quiz">Quiz me</button>
      </div>
      <div class="tutor-log" aria-live="polite"></div>
      <form class="tutor-form">
        <textarea class="tutor-input" rows="2" placeholder="Ask about this subject or chapter…"></textarea>
        <button class="btn btn-primary" type="submit">Send</button>
      </form>
    `;

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
      `Ready for ${ctx.label}. Pick a chapter, ask, explain, or quiz.`
    );

    function looksLikeAnswer(msg) {
      return /^[ABCDabcd]([\s.、:：).-]|$)/.test((msg || "").trim());
    }

    async function run(mode, message) {
      let effectiveMode = mode;
      if (mode === "ask" && lastMode === "quiz" && looksLikeAnswer(message)) {
        effectiveMode = "grade";
        message = `Previous question:\n${lastAssistant}\n\nMy answer: ${message}`;
      }

      addBubble(
        "user",
        message ||
          (mode === "explain"
            ? "Explain this chapter"
            : mode === "quiz"
              ? "Quiz me"
              : message)
      );
      const pending = document.createElement("div");
      pending.className = "tutor-bubble system";
      pending.textContent = "Thinking…";
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
    document.querySelectorAll(".tutor[data-tutor]").forEach(mountTutor);
    document.querySelectorAll("[data-progress-root]").forEach(mountProgress);
    document.querySelectorAll("[data-flashcards]").forEach(mountFlashcards);
    document.querySelectorAll("[data-practice]").forEach(mountPractice);
  });
})();
