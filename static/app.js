let songs = [];
let selectedSongIds = [null, null, null];

document.addEventListener("DOMContentLoaded", () => {
  const ingestBtn = document.getElementById("ingestBtn");
  const tasteBtn = document.getElementById("tasteBtn");
  const statusEl = document.getElementById("status");
  const resultEl = document.getElementById("result");
  const ingestResultEl = document.getElementById("ingestResult");
  const themeToggle = document.getElementById("themeToggle");
  const combos = document.querySelectorAll(".combo");

  // ---------- Theme handling ----------
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "dark") {
    document.body.classList.add("dark-mode");
    if (themeToggle) themeToggle.checked = true;
  }

  if (themeToggle) {
    themeToggle.addEventListener("change", () => {
      if (themeToggle.checked) {
        document.body.classList.add("dark-mode");
        localStorage.setItem("theme", "dark");
      } else {
        document.body.classList.remove("dark-mode");
        localStorage.setItem("theme", "light");
      }
    });
  }

  // ---------- Helpers ----------
  function setStatus(msg, isError = false) {
    if (!statusEl) return;
    statusEl.textContent = msg || "";
    statusEl.style.color = isError ? "#dc2626" : "var(--muted)";
  }

  // ---------- Load songs ----------
  async function loadSongs() {
    try {
      const res = await fetch("/songs");
      if (!res.ok) {
        throw new Error("Failed to fetch /songs");
      }
      songs = await res.json();
      if (!Array.isArray(songs)) {
        songs = [];
      }
      if (songs.length === 0) {
        setStatus("Click Load music to ingest the songs into the app!", true);
      } else {
        setStatus(`Loaded ${songs.length} songs from the database.`);
      }
    } catch (err) {
      console.error(err);
      setStatus("Error loading songs from server.", true);
    }
  }

  // ---------- Combo dropdown logic ----------
  function renderDropdown(combo, filter = "") {
    const index = parseInt(combo.dataset.index, 10);
    const dropdown = combo.querySelector(".combo-dropdown");
    dropdown.innerHTML = "";

    const norm = filter.trim().toLowerCase();

    const matches = songs.filter((song) => {
      const label = `${song.artist || ""} ${song.title || ""} ${
        song.album || ""
      }`.toLowerCase();
      return !norm || label.includes(norm);
    });

    if (matches.length === 0) {
      dropdown.style.display = "none";
      return;
    }

    // Show ALL matches (no 50-item cap) so you can scroll through the full list
    matches.forEach((song) => {
      const opt = document.createElement("div");
      opt.className = "combo-option";
      // Show as Artist — Title
      opt.textContent = `${song.artist} — ${song.title}`;
      opt.addEventListener("click", () => {
        const input = combo.querySelector(".combo-input");
        input.value = opt.textContent;
        selectedSongIds[index] = song.item_id;
        dropdown.style.display = "none";
      });
      dropdown.appendChild(opt);
    });

    dropdown.style.display = "block";
  }

  combos.forEach((combo) => {
    const input = combo.querySelector(".combo-input");
    const dropdown = combo.querySelector(".combo-dropdown");

    input.addEventListener("input", () => {
      // Clear the selected id when user types
      const index = parseInt(combo.dataset.index, 10);
      selectedSongIds[index] = null;
      renderDropdown(combo, input.value);
    });

    input.addEventListener("focus", () => {
      renderDropdown(combo, input.value);
    });

    document.addEventListener("click", (e) => {
      if (!combo.contains(e.target)) {
        dropdown.style.display = "none";
      }
    });
  });

  // ---------- Ingest button ----------
  if (ingestBtn) {
    ingestBtn.addEventListener("click", async () => {
      setStatus("Ingesting songs into the database…");
      resultEl.innerHTML = "";
      if (ingestResultEl) ingestResultEl.textContent = "";

      try {
        const res = await fetch("/ingest", { method: "POST" });
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.error || "Ingest failed");
        }
        const inserted = data.inserted_songs ?? data.n ?? 0;
        if (ingestResultEl) {
          ingestResultEl.textContent = `Inserted ${inserted} songs.`;
        }
        setStatus("Ingest complete. Reloading songs…");
        await loadSongs();
      } catch (err) {
        console.error(err);
        setStatus("Ingest failed. Check server logs.", true);
      }
    });
  }

  // ---------- Recommend from 3 liked songs ----------
  if (tasteBtn) {
    tasteBtn.addEventListener("click", async () => {
      resultEl.innerHTML = "";
      setStatus("");

      const likes = selectedSongIds.filter((id) => id !== null);

      if (likes.length !== 3) {
        setStatus("Please select exactly 3 songs first.", true);
        return;
      }

      if (new Set(likes).size !== likes.length) {
        setStatus("Please choose 3 different songs (no duplicates).", true);
        return;
      }

      setStatus("Fetching recommendation…");

      try {
        const res = await fetch("/recommend_from_likes", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ likes }),
        });

        const data = await res.json();

        if (!res.ok) {
          setStatus(data.error || "Error fetching recommendation.", true);
          return;
        }

        setStatus("");

        const rec = data.recommendation || {};

        // Guard: if backend accidentally returns one of the liked songs
        if (likes.includes(rec.item_id)) {
          setStatus(
            "The recommender returned one of your liked songs. Try different picks.",
            true
          );
          return;
        }

        const score =
          typeof rec.score === "number" ? rec.score.toFixed(2) : "N/A";

        resultEl.innerHTML = `
          <div class="card">
            <div><strong>Recommended song:</strong> ${rec.artist} — ${
          rec.title
        }</div>
            <div class="muted" style="margin-top:4px;">
              <div><strong>Album:</strong> ${rec.album || "Unknown"}</div>
              <div><strong>Genre:</strong> ${rec.genre || "Unknown"}</div>
              <div><strong>Tags:</strong> ${rec.tags || "None"}</div>
              <div><strong>Description:</strong> ${
                rec.description || "No description."
              }</div>
              <div style="margin-top:4px;"><strong>Similarity score:</strong> ${score}</div>
            </div>
          </div>
        `;
      } catch (err) {
        console.error(err);
        setStatus("Network error while asking for a recommendation.", true);
      }
    });
  }

  // Initial load
  loadSongs();
});
