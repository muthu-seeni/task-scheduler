// -------------------------------
// Speech Recognition
// -------------------------------
window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new window.SpeechRecognition();
recognition.lang = "en-US";
recognition.interimResults = false;

// -------------------------------
// DOM Elements
// -------------------------------
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

// -------------------------------
// Speech Handlers
// -------------------------------
function startRecognition(callback) {
    recognition.abort();
    recognition.start();
    recognition.onresult = (event) => callback(event.results[0][0].transcript);
}

if (micTitleBtn) micTitleBtn.addEventListener("click", () => startRecognition(text => { taskTitle.value = text; checkTaskListMode(); }));
if (micTimeBtn) micTimeBtn.addEventListener("click", () => startRecognition(text => { let t = convertSpeechToTime(text); if(t) taskTime.value = t; }));
if (micActionBtn) micActionBtn.addEventListener("click", () => startRecognition(text => {
    taskAction.value = taskAction.value ? taskAction.value + ", " + text : text;
    let t = convertSpeechToTime(text); 
    if(t && !taskTime.value) taskTime.value = t;
}));

function convertSpeechToTime(speech) {
    if (!speech) return null;
    const m = speech.match(/(\d{1,2})[:\s]?(\d{0,2})?\s*(am|pm)?/i);
    if (!m) return null;
    let h = parseInt(m[1]), min = m[2]?parseInt(m[2]):0;
    const p = m[3];
    if(p){ if(p.toLowerCase()==="pm" && h<12) h+=12; if(p.toLowerCase()==="am" && h===12) h=0; }
    return `${h.toString().padStart(2,"0")}:${min.toString().padStart(2,"0")}`;
}

// -------------------------------
// Task/Grocery List Modes
// -------------------------------
function isTaskListMode() { return taskTitle && taskTitle.value.toLowerCase() === "prepare task list"; }
function isGroceryListMode() { return taskTitle && taskTitle.value.toLowerCase() === "prepare grocery list"; }

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
// -------------------------------
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
// Edit Task
// -------------------------------
document.querySelectorAll(".edit-task").forEach(btn => {
    btn.addEventListener("click", () => {
        taskForm.action = "/tasks/edit/" + btn.dataset.id;
        taskSubmitBtn.textContent = "Save Task";
        formTitle.textContent = "✏️ Edit Task";
        document.getElementById("taskId").value = btn.dataset.id;
        taskTitle.value = btn.dataset.title;
        taskTime.value = btn.dataset.time;
        taskAction.value = btn.dataset.action;
        checkTaskListMode();
    });
});

// -------------------------------
// Notification toggles per task
// -------------------------------
window.taskNotifications = {};
document.querySelectorAll("#taskList li").forEach(li => {
    const btn = li.querySelector(".toggle-notif");
    const id = li.querySelector(".edit-task").dataset.id;
    window.taskNotifications[id] = btn.textContent==="🔔"; // restore previous state
    if(btn) btn.onclick = () => {
        const isOn = btn.textContent==="🔔";
        btn.textContent = isOn ? "🔕" : "🔔";
        window.taskNotifications[id] = !isOn;
    };
});

// -------------------------------
// Wrap text
// -------------------------------
if(taskAction) taskAction.style.whiteSpace = "pre-wrap";

// -------------------------------
// Desktop Notifications & SocketIO
// -------------------------------
let notificationsEnabled = true;
if(Notification.permission!=="granted") Notification.requestPermission();

setInterval(async()=>{
    if(!notificationsEnabled) return;
    try{
        const r = await fetch("/check_notifications");
        const t = await r.json();
        t.forEach(task=>{
            if(Notification.permission==="granted" && window.taskNotifications[task.id]!==false)
                new Notification(task.title,{body:task.body});
        });
    }catch(e){console.error(e);}
}, 5*60*1000);

checkTaskListMode();

const socket = io();
socket.on("task_notification", function(data) {
    if (Notification.permission === "granted" && window.taskNotifications[data.id]!==false) {
        new Notification(data.title, { body: data.body });
    }
});
