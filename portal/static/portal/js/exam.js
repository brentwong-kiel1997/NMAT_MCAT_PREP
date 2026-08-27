/* Mock-exam take page: countdown, autosave, flag toggle.
 * The server owns the clock — data-remaining is the authoritative seconds
 * left for this block; this script only counts it down and reports state.
 */
(function () {
  "use strict";

  function readJson(el) {
    try { return JSON.parse(el.textContent); } catch (err) { return null; }
  }

  function csrfToken() {
    const m = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    if (m) return decodeURIComponent(m[1]);
    const input = document.querySelector(".csrf-slot input[name=csrfmiddlewaretoken]");
    return input ? input.value : "";
  }

  function fmt(seconds) {
    const s = Math.max(0, seconds | 0);
    const h = Math.floor(s / 3600);
    const m = Math.floor((s % 3600) / 60);
    const sec = s % 60;
    const pad = (n) => String(n).padStart(2, "0");
    return h > 0 ? `${pad(h)}:${pad(m)}:${pad(sec)}` : `${pad(m)}:${pad(sec)}`;
  }

  function mount(root) {
    if (root.dataset.ready === "1") return;
    root.dataset.ready = "1";

    const attemptId = parseInt(root.dataset.attempt, 10);
    const examId = root.dataset.examId;
    const blockId = root.dataset.block;
    const pos = parseInt(root.dataset.pos, 10);
    let remaining = parseInt(root.dataset.remaining, 10) || 0;
    const clock = document.getElementById("exam-clock");
    const savedNote = document.getElementById("exam-saved");
    const flagBtn = document.getElementById("exam-flag");
    let flagged = flagBtn ? flagBtn.classList.contains("is-flag-on") : false;
    let chosen = null;
    const selected = root.querySelector(".exam-choice.is-selected");
    if (selected) chosen = selected.dataset.letter;

    let deadlinePassed = false;

    // ---- countdown (monotonic from the server value; never reads the client clock)
    function tick() {
      if (deadlinePassed) return;
      remaining -= 1;
      if (clock) clock.textContent = fmt(remaining);
      if (remaining <= 60 && clock) clock.classList.add("is-low");
      if (remaining <= 0) {
        deadlinePassed = true;
        submitExam(true); // server finalizes regardless; this just speeds it up
      }
    }
    if (clock) {
      clock.textContent = fmt(remaining);
      setInterval(tick, 1000);
    }

    // ---- autosave
    let pending = null;
    let timer = null;
    function post(body) {
      return fetch("/exams/api/answer/", {
        method: "POST",
        credentials: "same-origin",
        keepalive: true,
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
        body: JSON.stringify(body),
      });
    }
    function flush(immediate) {
      if (!pending) return;
      const body = pending;
      pending = null;
      post(body).then((res) => {
        if (res.status === 409) {
          // server expired the block — go to the result page
          window.location.href = `/exams/result/${attemptId}/`;
          return;
        }
        if (savedNote && res.ok) {
          savedNote.textContent = "Saved";
          setTimeout(() => { savedNote.textContent = ""; }, 1500);
        }
      }).catch(() => {});
    }
    function queueSave() {
      pending = { attempt_id: attemptId, block_id: blockId, pos: pos,
                  chosen: chosen, flagged: flagged };
      if (timer) clearTimeout(timer);
      timer = setTimeout(() => flush(true), 600);
    }

    // ---- choice clicks
    root.querySelectorAll(".exam-choice").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (deadlinePassed) return;
        root.querySelectorAll(".exam-choice").forEach((b) => b.classList.remove("is-selected"));
        btn.classList.add("is-selected");
        chosen = btn.dataset.letter;
        queueSave();
      });
    });

    // ---- flag toggle
    if (flagBtn) {
      flagBtn.addEventListener("click", () => {
        if (deadlinePassed) return;
        flagged = !flagged;
        flagBtn.classList.toggle("is-flag-on", flagged);
        flagBtn.textContent = flagged ? "★ Flagged" : "☆ Flag for review";
        queueSave();
      });
    }

    // ---- submit
    function submitExam(auto) {
      if (!auto && !window.confirm("Submit the exam for scoring?")) return;
      fetch("/exams/api/submit/", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
        body: JSON.stringify({ attempt_id: attemptId }),
      }).then(() => {
        window.location.href = `/exams/result/${attemptId}/`;
      }).catch(() => {
        window.location.href = `/exams/result/${attemptId}/`;
      });
    }
    const submitForm = document.getElementById("exam-submit-form");
    if (submitForm) {
      submitForm.addEventListener("submit", (ev) => {
        ev.preventDefault();
        submitExam(false);
      });
    }

    // ---- flush pending save before leaving the page
    window.addEventListener("beforeunload", () => { if (pending) flush(true); });
    document.querySelectorAll(".exam-grid a, .exam-nav a, .exam-finish button")
      .forEach((a) => a.addEventListener("click", () => { if (pending) flush(true); }));
  }

  document.querySelectorAll("[data-exam]").forEach(mount);
})();
