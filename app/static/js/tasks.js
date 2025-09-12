// tasks.js - single safe file, no redeclarations

// -------------------------------
// Speech Recognition (if available)
window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;
try { recognition = new window.SpeechRecognition(); recognition.lang = "en-US"; recognition.interimResults = false; } catch(e) { recognition = null; }

// -------------------------------
// DOM
const taskTitle = document.getElementById("taskTitle");
const taskTime = document.getElementById("taskTime");
const taskAction = document.getElementById("taskAction");
const micTitleBtn = document.getElementById("micTitleBtn");
const micTimeBtn = document.getElementById("micTimeBtn");
const micActionBtn = document.getElementById("micActionBtn");
const taskForm = document.getElementById("taskForm");
const formTitle = document.getElementById("formTitle");
const taskSubmitBtn = document.getElementById("taskSubmitBtn");
const actionButtonsContainer = document.getElementById("actionButtons");
const taskList = document.getElementById("taskList");

// -------------------------------
// Recognition helpers
function startRecognition(callback) {
    if (!recognition) return;
    try {
        recognition.abort();
        recognition.start();
        recognition.onresult = (event) => callback(event.results[0][0].transcript);
    } catch(e) { /* ignore */ }
}
if (micTitleBtn) micTitleBtn.addEventListener("click", () => startRecognition(text => { taskTitle.value = text; checkTaskListMode(); }));
if (micTimeBtn) micTimeBtn.addEventListener("click", () => startRecognition(text => { let t = convertSpeechToTime(text); if(t) taskTime.value = t; }));
if (micActionBtn) micActionBtn.addEventListener("click", () => startRecognition(text => {
    const titleVal = taskTitle.value.toLowerCase();
    if (titleVal.includes("grocery list")) {
        // Append for grocery list
        taskAction.value = taskAction.value ? taskAction.value + ", " + text : text;
    } else {
        // Overwrite for normal tasks
        taskAction.value = text;
    }
    let t = convertSpeechToTime(text);
    if(t && !taskTime.value) taskTime.value = t;
}));

function convertSpeechToTime(speech) {
    if (!speech) return null;
    const m = speech.match(/(\d{1,2})[:\s]?(\d{0,2})?\s*(am|pm)?/i);
    if (!m) return null;
    let h = parseInt(m[1]), min = m[2] ? parseInt(m[2]) : 0;
    const p = m[3];
    if (p) { if(p.toLowerCase() === "pm" && h < 12) h += 12; if(p.toLowerCase() === "am" && h === 12) h = 0; }
    return `${h.toString().padStart(2,"0")}:${min.toString().padStart(2,"0")}`;
}

// -------------------------------
// Edit / modes
function isTaskListMode() { return taskTitle && taskTitle.value && taskTitle.value.toLowerCase() === "prepare task list"; }
function isGroceryListMode() { return taskTitle && taskTitle.value && taskTitle.value.toLowerCase() === "prepare grocery list"; }

function checkTaskListMode() {
    if (!taskAction) return;
    if (isTaskListMode()) {
        taskAction.style.height = "120px";
        const items = document.querySelectorAll("#taskList li[data-type='task'] .task-action-text");
        taskAction.value = Array.from(items).map(i => i.textContent).join(", ");
    } else if (isGroceryListMode()) {
        taskAction.style.height = "120px";
        const items = document.querySelectorAll("#taskList li[data-type='grocery'] .task-action-text");
        taskAction.value = Array.from(items).map(i => i.textContent).join(", ");
    } else {
        taskAction.style.height = "auto";
    }
    addActionButtons();
}

// -------------------------------
// Print & WhatsApp Buttons
function addActionButtons() {
    if (!actionButtonsContainer || actionButtonsContainer.children.length) return;
    const printBtn = document.createElement("button");
    printBtn.type = "button";
    printBtn.className = "btn btn-sm btn-outline-success me-1";
    printBtn.innerHTML = '<i class="bi bi-printer"></i>';
    printBtn.onclick = () => printText(taskAction.value);

    const whatsappBtn = document.createElement("button");
    whatsappBtn.type = "button";
    whatsappBtn.className = "btn btn-sm btn-outline-success";
    whatsappBtn.innerHTML = '<i class="bi bi-whatsapp"></i>';
    whatsappBtn.onclick = () => navigator.clipboard.writeText(taskAction.value);

    actionButtonsContainer.appendChild(printBtn);
    actionButtonsContainer.appendChild(whatsappBtn);
}

function printText(text) {
    const w = window.open("", "_blank");
    w.document.write(`<pre style="white-space: pre-wrap; font-family: sans-serif;">${text}</pre>`);
    w.document.close(); w.print();
}

// -------------------------------
// Initialise edit buttons
function initEditButtons() {
    document.querySelectorAll(".edit-task").forEach(btn => {
        btn.removeEventListener("click", editClickHandler);
        btn.addEventListener("click", editClickHandler);
    });
}
function editClickHandler(e) {
    const btn = e.currentTarget;
    taskForm.action = "/tasks/edit/" + btn.dataset.id;
    taskSubmitBtn.textContent = "Save Task";
    formTitle.textContent = "✏️ Edit Task";
    document.getElementById("taskId").value = btn.dataset.id;
    taskTitle.value = btn.dataset.title || "";
    taskTime.value = btn.dataset.time || "";
    taskAction.value = btn.dataset.action || "";
    checkTaskListMode();
}

// -------------------------------
// Notification toggles (persisted)
function initToggleButtons() {
    document.querySelectorAll("#taskList li").forEach(li => {
        const btn = li.querySelector(".toggle-notif");
        const id = li.dataset.id;
        if (!id || !btn) return;

        // Get initial state from data-notify (string "true" or "false")
        const initial = li.dataset.notify === "true";
        btn.textContent = initial ? "🔔" : "🔕";
        window.taskNotifications = window.taskNotifications || {};
        window.taskNotifications[id] = initial;

        // attach handler
        btn.removeEventListener("click", toggleClickHandler);
        btn.addEventListener("click", toggleClickHandler);
    });
}

async function toggleClickHandler(e) {
    const btn = e.currentTarget;
    const li = btn.closest("li");
    const id = li.dataset.id;
    if (!id) return;

    // Optimistically flip in UI
    const isCurrentlyOn = btn.textContent === "🔔";
    btn.textContent = isCurrentlyOn ? "🔕" : "🔔";
    window.taskNotifications[id] = !isCurrentlyOn;

    // Fire server update (no body required)
    try {
        const res = await fetch(`/tasks/notify_toggle/${id}`, { method: "POST" });
        const j = await res.json();
        if (!j.success) {
            // revert on failure
            btn.textContent = isCurrentlyOn ? "🔔" : "🔕";
            window.taskNotifications[id] = isCurrentlyOn;
        } else {
            // update li dataset so persistence on reload is consistent
            li.dataset.notify = j.notify_enabled ? "true" : "false";
        }
    } catch (err) {
        // network error - revert
        btn.textContent = isCurrentlyOn ? "🔔" : "🔕";
        window.taskNotifications[id] = isCurrentlyOn;
    }
}

// -------------------------------
// Wrap text
if (taskAction) taskAction.style.whiteSpace = "pre-wrap";

// -------------------------------
// Notifications + Socket handling
window.notifiedTasks = window.notifiedTasks || new Set();
window.taskNotifications = window.taskNotifications || {}; // id -> boolean

// Use socket created in layout.html
if (typeof socket !== "undefined") {
    socket.on("task_notification", function(data) {
        // data must include id, title, body
        const id = String(data.id || "");
        const title = data.title || "Reminder";
        const body = data.body || "You have a task!";
        const key = id + "|" + title + "|" + body;

        // only show once per unique message
        if (window.notifiedTasks.has(key)) return;
        window.notifiedTasks.add(key);

        // ✅ Determine if notifications enabled
        const enabled = (id && window.taskNotifications[id] !== undefined) ? window.taskNotifications[id] : false;
        if (!enabled) return;

        // desktop notification
        if (Notification.permission === "granted") {
            new Notification(title, { body: body });
        }

        // play voice in browser if enabled
        try {
            const utter = new SpeechSynthesisUtterance(body);
            speechSynthesis.speak(utter);
        } catch(e) { /* ignore TTS errors */ }
    });
}

// ✅ Periodic check for missed notifications
setInterval(async () => {
    try {
        const r = await fetch("/check_notifications");
        const tasks = await r.json();
        tasks.forEach(task => {
            const id = String(task.id || "");
            const key = id + "|" + (task.title || "") + "|" + (task.body || "");
            if (!window.notifiedTasks.has(key)) {
                const enabled = (id && window.taskNotifications[id] !== undefined) ? window.taskNotifications[id] : false;
                if (!enabled) return;

                if (Notification.permission === "granted") {
                    new Notification(task.title, { body: task.body });
                }

                try {
                    if(enabled) {
                        const utter = new SpeechSynthesisUtterance(task.body);
                        speechSynthesis.speak(utter);
                    }
                } catch(e) {}
                window.notifiedTasks.add(key);
            }
        });
    } catch (e) { console.error(e); }
}, 5 * 60 * 1000);

// -------------------------------
// Init once
initEditButtons();
initToggleButtons();
checkTaskListMode();
addActionButtons();
