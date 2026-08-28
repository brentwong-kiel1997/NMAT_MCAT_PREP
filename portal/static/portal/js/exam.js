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

    // ---- countdown: anchored to a deadline, immune to interval drift and to
    // background-tab timer throttling (recomputed, never decremented)
    const deadlineMs = Date.now() + remaining * 1000;
    function tick() {
      if (deadlinePassed) return;
      remaining = Math.max(0, Math.round((deadlineMs - Date.now()) / 1000));
      if (clock) clock.textContent = fmt(remaining);
      if (remaining <= 60 && clock) clock.classList.add("is-low");
      if (remaining <= 0) {
        deadlinePassed = true;
        lockNav();
        // The server owns block closure: navigating re-runs maybe_finalize,
        // which closes ONLY this block. Never call the global submit here —
        // a multi-block exam must survive one block's clock running out.
        window.location.href = `/exams/${examId}/take/${attemptId}/`;
      }
    }
    if (clock) {
      clock.textContent = fmt(remaining);
      setInterval(tick, 1000);
      document.addEventListener("visibilitychange", () => {
        if (!document.hidden && !deadlinePassed) tick();
      });
    }
    function lockNav() {
      document.querySelectorAll(".exam-grid a, .exam-nav a").forEach((a) => {
        a.style.pointerEvents = "none";
        a.setAttribute("aria-disabled", "true");
      });
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
          // server says this save is no longer valid (block expired) —
          // navigate so the server can close the block properly
          window.location.href = `/exams/${examId}/take/${attemptId}/`;
          return;
        }
        if (savedNote) {
          savedNote.textContent = res.ok ? "Saved" : "Not saved — retrying";
          if (res.ok) setTimeout(() => { savedNote.textContent = ""; }, 1500);
        }
        if (!res.ok && body.chosen) { pending = body; setTimeout(() => flush(true), 2000); }
      }).catch(() => {
        if (savedNote) savedNote.textContent = "Offline — will retry";
        if (body.chosen) { pending = body; setTimeout(() => flush(true), 3000); }
      });
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
      // flush any debounced save first so the final choice is scored
      const flushFirst = pending
        ? post({ ...pending }).catch(() => {})
        : Promise.resolve();
      pending = null;
      flushFirst.then(() => fetch("/exams/api/submit/", {
        method: "POST",
        credentials: "same-origin",
        keepalive: true,
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken() },
        body: JSON.stringify({ attempt_id: attemptId }),
      })).then((res) => res.json().catch(() => ({})).then((data) => {
        if (data.error === "blocks-remaining" && data.next_block) {
          window.location.href = `/exams/${examId}/break/${attemptId}/${data.next_block}/`;
          return;
        }
        window.location.href = `/exams/result/${attemptId}/`;
      })).catch(() => {
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
    window.addEventListener("pagehide", () => { if (pending) flush(true); });
    document.querySelectorAll(".exam-grid a, .exam-nav a, .exam-finish button")
      .forEach((a) => a.addEventListener("click", () => { if (pending) flush(true); }));
  }

  document.querySelectorAll("[data-exam]").forEach(mount);
})();
