/*
  TIME-SWAP APP — FULL JS
  Handles:
   - Page detection
   - Time wheel interaction
   - Exchange submit
   - Gallery API pagination
   - Stats + heatmap */

document.addEventListener("DOMContentLoaded", () => {
    const page = document.body.dataset.page;

    if (page === "exchange") {
        initTimeWheel();
        initExchangeSubmit();
    }

    if (page === "gallery") {
        initGallery();
    }

    if (page === "stats") {
        initStats();
    }
});

/*  TIME WHEEL (EXCHANGE PAGE) */
function initTimeWheel() {
    const wheel = document.getElementById("time-wheel");
    const knob = document.getElementById("time-knob");
    const display = document.getElementById("time-display-text");
    const hiddenInput = document.getElementById("time_value");

    if (!wheel || !knob || !display || !hiddenInput) return;

    let dragging = false;

    function minutesToTime(minutes) {
        let h = Math.floor(minutes / 60);
        let m = minutes % 60;
        return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
    }

    function updateKnob(deg) {
        const rect = wheel.getBoundingClientRect();
        const r = rect.width / 2;
        const knobR = knob.offsetWidth / 2;
        const rad = deg * Math.PI / 180;
        const radius = r - knobR - 5;

        let x = r + radius * Math.cos(rad);
        let y = r + radius * Math.sin(rad);

        knob.style.left = `${x - knobR}px`;
        knob.style.top = `${y - knobR}px`;
    }

    function angleFromEvent(e) {
        const rect = wheel.getBoundingClientRect();
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;
        const x = e.clientX - cx;
        const y = e.clientY - cy;
        let deg = Math.atan2(y, x) * 180 / Math.PI;
        return (deg + 360) % 360;
    }

    function setTime(deg) {
        let minutes = Math.round((deg / 360) * 1440);
        let timeStr = minutesToTime(minutes);
        display.textContent = timeStr;
        hiddenInput.value = timeStr;
        updateKnob(deg);
    }

    // Start drag
    wheel.addEventListener("mousedown", (e) => {
        dragging = true;
        setTime(angleFromEvent(e));
    });
    wheel.addEventListener("touchstart", (e) => {
        dragging = true;
        setTime(angleFromEvent(e.touches[0]));
    });

    // Move
    document.addEventListener("mousemove", (e) => {
        if (!dragging) return;
        setTime(angleFromEvent(e));
    });
    document.addEventListener("touchmove", (e) => {
        if (!dragging) return;
        setTime(angleFromEvent(e.touches[0]));
    });

    // Stop
    document.addEventListener("mouseup", () => dragging = false);
    document.addEventListener("touchend", () => dragging = false);

    // Default time (05:30 AM)
    const defaultMinutes = 330;
    const defaultDeg = (defaultMinutes / 1440) * 360;
    setTime(defaultDeg);
}

/*  EXCHANGE SUBMIT */
function initExchangeSubmit() {
    const form = document.getElementById("exchange-form");
    if (!form) return;

    form.addEventListener("submit", () => {
        // Optional: show a loader
        // Later you can add a cool animation overlay
    });
}

/*  GALLERY (PAGINATION + API) */
let galleryOffset = 0;
const GALLERY_LIMIT = 9;

function initGallery() {
    loadGallery(true);

    const loadMoreBtn = document.getElementById("gallery-load-more-btn");
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener("click", () => {
            loadGallery(false);
        });
    }
}

async function loadGallery(reset) {
    const grid = document.getElementById("gallery-grid");
    if (!grid) return;

    if (reset) {
        galleryOffset = 0;
        grid.innerHTML = "";
    }

    try {
        const res = await fetch(`/api/moments?offset=${galleryOffset}&limit=${GALLERY_LIMIT}`);
        const data = await res.json();

        if (!Array.isArray(data) || data.length === 0) {
            if (reset) {
                grid.innerHTML = `<p style="color:#aaa;">No moments yet. Share the first one!</p>`;
            }
            return;
        }

        data.forEach(moment => {
            grid.appendChild(makeCard(moment));
        });

        galleryOffset += data.length;

    } catch (err) {
        console.warn("Gallery load error:", err);
    }
}

function makeCard(moment) {
    const div = document.createElement("div");
    div.className = "moment-card";

    div.innerHTML = `
        <div class="moment-header">
            <span>${moment.time_value}</span>
            <span>${moment.mood ? moment.mood : "Unknown"}</span>
        </div>
        <div class="moment-text">
            ${moment.text}
        </div>
    `;

    return div;
}

/* STATS + HEATMAP */
async function initStats() {
    try {
        const res = await fetch("/api/stats");
        const data = await res.json();
        fillStats(data);
        fillHeatmap(data.hour_counts);
    } catch (err) {
        console.warn("Stats load error:", err);
    }
}

function fillStats(data) {
    document.getElementById("stat-user-moments").textContent = data.user_moments;
    document.getElementById("stat-user-received").textContent = data.user_received;
    document.getElementById("stat-total-moments").textContent = data.total_moments;
    document.getElementById("stat-streak").textContent = data.streak;
}

function fillHeatmap(hourCounts) {
    const grid = document.getElementById("heatmap-grid");
    if (!grid) return;

    grid.innerHTML = "";
    let max = 0;

    for (let hour in hourCounts) {
        if (hourCounts[hour] > max) max = hourCounts[hour];
    }
    max = max || 1;

    for (let i = 0; i < 24; i++) {
        const cell = document.createElement("div");
        cell.className = "heatmap-cell";

        const count = hourCounts[i] || 0;
        const opacity = 0.1 + (count / max) * 0.9;

        cell.style.background = `rgba(255, 78, 205, ${opacity})`;
        cell.title = `${String(i).padStart(2, "0")}:00 — ${count} moments`;

        grid.appendChild(cell);
    }
}
function Areyousure(){
    if(!confirm("Are you sure you want to Signout?")){
        return false;
    }
    else{
        return true;
    }
}