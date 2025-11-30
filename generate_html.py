import os
import webbrowser
from data.shlokas import ALL_SHLOKAS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_HTML = os.path.join(
    BASE_DIR,
    "android", "app", "src", "main", "assets", "html", "gita_shlokas.html"
)

SHLOKAS_PER_PAGE = 2


# ---------------------------------------------------------
# FLATTEN SECTIONS (YOUR CURRENT FORMAT)
# ---------------------------------------------------------
def flatten_sections(all_sections):
    flat = []
    for sec in all_sections:
        if not isinstance(sec, dict):
            continue

        for title, shlok_list in sec.items():
            for s in shlok_list:
                chapter = s.get("chapter", "")
                verse = s.get("verse", "")
                reference = f"अध्याय {chapter} • श्लोक {verse}"

                flat.append({
                    "section": title,
                    "problem": title,
                    "reference": reference,
                    "text": s.get("sanskrit", ""),
                    "meaning": s.get("hindi_arth", ""),
                    "example": s.get("udaharan", "")
                })
    return flat


def js_escape(t):
    if t is None:
        return ""
    return (
        str(t)
        .replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("</", "<\\u002F")
        .replace("\r", "")
    )


def clean_text_for_example(t):
    if t is None:
        return "—"

    txt = str(t).strip()
    if txt == "" or txt == "-" or txt == "—":
        return "—"

    cleaned = " ".join(line.strip() for line in txt.splitlines() if line.strip())
    return cleaned if cleaned else "—"


# ---------------------------------------------------------
# SAFE HTML GENERATOR (NO F-STRINGS BREAKING)
# ---------------------------------------------------------
def generate_html(flat):

    js_entries = []

    for i, s in enumerate(flat):
        meaning = clean_text_for_example(s["meaning"])
        example = clean_text_for_example(s["example"])

        entry = (
            "        {\n"
            f"            id: {i},\n"
            f"            section: `{js_escape(s['section'])}`,\n"
            f"            problem: `{js_escape(s['problem'])}`,\n"
            f"            reference: `{js_escape(s['reference'])}`,\n"
            f"            text: `{js_escape(s['text'])}`,\n"
            f"            meaning: `{js_escape(meaning)}`,\n"
            f"            example: `{js_escape(example)}`\n"
            "        }"
        )
        js_entries.append(entry)

    js_array = ",\n".join(js_entries)

    # ---------------------------------------------------------
    # HTML TEMPLATE
    # ---------------------------------------------------------
    html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>AI Bhagwat Geeta by Anurag Vasu Bharti</title>
<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
body { margin:0; padding:12px; font-family:Arial; background:#ff9800; }
.title-block { text-align:center; width:100%; }
h1 { font-size:24px; margin:6px 0; }
h3 { font-size:21px; margin:0 0 6px 0; }
hr { border:none; border-bottom:2px solid black; margin:6px 0; }
.container { display:flex; flex-direction:column; min-height:calc(100vh - 140px); }
.content-wrap { overflow:auto; padding-bottom:12px; }
.frame {
  background:white; border:2px solid black; border-radius:12px;
  padding:12px; margin-top:12px; min-height:160px;
}
.frame.highlight {
  background:#e7f9e6; border-color:#8fd19b;
  box-shadow:0 0 12px rgba(0,128,64,0.25);
}
button {
  padding:7px 14px; border:none; border-radius:14px;
  margin:3px; font-size:14px; font-weight:bold; cursor:pointer;
}
.green { background:#2e7d32; color:white; }
.red { background:#b71c1c; color:white; }
.blue { background:#1565c0; color:white; }
.small-btn { padding:5px 10px; font-size:13px; }
pre { white-space:pre-wrap; font-size:16px; margin-top:8px; }
.controls-row { text-align:center; margin:8px 0; display:flex; flex-wrap:wrap; justify-content:center; align-items:center; gap:6px; }
.voice-controls { display:inline-block; margin-left:14px; }
.toggle {
  margin:0 6px; padding:6px 10px; border-radius:10px;
  background:white; border:1px solid rgba(0,0,0,0.12); cursor:pointer;
}
.selected { background:#1976d2; color:white; }
.speed-selected { background:#388e3c; color:white; }
.nav {
  display:flex; justify-content:space-between; font-weight:bold;
  margin-top:12px; position:sticky; bottom:0; padding-top:10px;
}
</style>
</head>
<body>

<div class="title-block">
  <h1>AI Bhagwat Geeta by Anurag Vasu Bharti</h1>
  <hr>
  <h3>📘 भगवद गीता में अपनी समस्याओं का समाधान खोजें</h3>
  <hr>
</div>

<div class="controls-row">
  <button class="green" onclick="startReadingAll()">Start</button>
  <button class="green" onclick="nextButtonPressed()">Next</button>
  <button class="red" onclick="stopReading()">Stop</button>
  <button class="green" onclick="resumeReading()">Resume</button>
  <button class="green" onclick="readRandom()">Random</button>
  <button class="red" onclick="exitApp()">Exit</button>

  <span style="width:12px;"></span>

  <button id="femaleBtn" class="toggle">♀ Female</button>
  <button id="maleBtn" class="toggle">Male</button>

  <span style="width:12px;"></span>

  <button id="verySlowBtn" class="toggle">Very Slow</button>
  <button id="slowBtn" class="toggle">Slow</button>
  <button id="mediumBtn" class="toggle">Medium</button>

  <span id="voiceControls" class="voice-controls"></span>
</div>

<div class="container">
  <div class="content-wrap" id="contentWrap"><div id="content"></div></div>
  <div class="nav">
    <button onclick="prevPage()">⬅ Previous</button>
    <span id="pageInfo"></span>
    <button onclick="nextPage()">Next ➡</button>
  </div>
</div>

<script>

const PER_PAGE = __PER_PAGE__;

const SHLOKAS = [
__JS_ARRAY__
];

let page = 0;
let reading = false;
let autoIndex = 0;
let readTimer = null;

let selectedGender = localStorage.getItem('gita_voice_gender') || 'female';
let selectedSpeed  = localStorage.getItem('gita_voice_speed')  || 'slow';
let browserVoice = null;

// ---------- VOICE LOADING (improved heuristics) ----------
function loadVoices() {
    const list = speechSynthesis.getVoices();
    if (!list.length) return;

    // Normalize names for matching
    const lname = (s) => (s || "").toLowerCase();

    // prefer exact Hindi language matches
    const hindiVoices = list.filter(v => lname(v.lang || "").includes('hi') || lname(v.name || "").includes('hi'));

    // helper for checking common male name tokens
    const maleTokens = ['male','kumar','ravi','deepak','arun','raj','vijay','sachin','rahul','ajay','amit'];
    const femaleTokens = ['female','woman','female','smt','sushma','seema','neha','priya','anita','anjali','lata'];

    function findVoice(preferMale){
        if (hindiVoices.length){
            // try name tokens
            for (let v of hindiVoices){
                const nm = lname(v.name || "");
                if (preferMale){
                    for (let t of maleTokens) if (nm.includes(t)) return v;
                } else {
                    for (let t of femaleTokens) if (nm.includes(t)) return v;
                }
            }
            // try gender words
            for (let v of hindiVoices){
                const nm = lname(v.name || "");
                if (!preferMale && (nm.includes('female') || nm.includes('woman'))) return v;
                if (preferMale && (nm.includes('male') || nm.includes('man'))) return v;
            }
            // fallback to any hindi voice
            return hindiVoices[0];
        }
        // fallback global search
        if (preferMale){
            return list.find(v => maleTokens.some(t => lname(v.name||"").includes(t))) || list[0];
        } else {
            return list.find(v => femaleTokens.some(t => lname(v.name||"").includes(t))) || list[0];
        }
    }

    if (selectedGender === 'female'){
        browserVoice = findVoice(false);
    } else {
        browserVoice = findVoice(true);
    }
}
speechSynthesis.onvoiceschanged = loadVoices;
loadVoices();

// ---------- Helpers ----------
function speedRate() {
    if (selectedSpeed === 'very_slow') return 0.72;
    if (selectedSpeed === 'slow') return 0.82;
    return 0.95;
}

function androidSpeakIfAvailable(text){
    try {
        if (typeof Android !== "undefined" && Android && Android.speak) {
            // Android API: Android.speak(text, gender, speed)
            Android.speak(text, selectedGender, selectedSpeed);
            return true;
        }
    } catch(e) {}
    return false;
}

function speak(text){
    // M3 priority:
    // 1) Android.speak(text, gender, speed)
    // 2) Browser selected voice (male/female heuristics)
    // 3) Any available voice
    if (androidSpeakIfAvailable(text)) return;

    try {
        speechSynthesis.cancel();
    } catch(e){}

    let u = new SpeechSynthesisUtterance(text);
    u.rate = speedRate();
    u.pitch = (selectedGender === 'female') ? 1.05 : 0.95;
    u.lang = browserVoice?.lang || 'hi-IN';
    if (browserVoice) {
        u.voice = browserVoice;
    }
    speechSynthesis.speak(u);
}

function stopTTS(){
    try { if (typeof Android !== "undefined" && Android && Android.stopSpeak) Android.stopSpeak(); } catch(e){}
    try { speechSynthesis.cancel(); } catch(e){}
}

// ---------- Highlighting & rendering ----------
function clearHighlights(){
    document.querySelectorAll(".frame.highlight").forEach(e=>e.classList.remove("highlight"));
}
function highlightFrame(i){
    clearHighlights();
    const el=document.getElementById("shlok_"+i);
    if(el){
        el.classList.add("highlight");
        el.scrollIntoView({behavior:'smooth',block:'center'});
    }
}

function render(){
    const start = page * PER_PAGE;
    const end = Math.min(start + PER_PAGE, SHLOKAS.length);
    let html = "";

    for (let i = start; i < end; i++){
        let s = SHLOKAS[i];
        html += `
            <div class="frame" id="shlok_${i}">
                <div style="font-weight:bold; margin-bottom:6px;">
                    ${i+1})
                    <button class="blue small-btn" onclick="readSingle(${i})">▶ Start This Shlok</button>
                    <button class="red small-btn" onclick="stopReading()">■ Stop</button>
                </div>

                <h4>📗 अनुभाग: ${s.section}</h4>
                <b>समस्या:</b> ${s.problem}<br><br>

                <b>${s.reference}</b><br><br>

                <b>संस्कृत:</b><br>
                <pre>${s.text}</pre>

                <b>हिंदी अर्थ:</b><br>
                ${s.meaning}<br><br>

                <b>उदाहरण:</b><br>
                ${s.example}
            </div>
        `;
    }

    document.getElementById("content").innerHTML = html;
    document.getElementById("pageInfo").innerText =
        "Page "+(page+1)+" / "+Math.ceil(SHLOKAS.length/PER_PAGE);
}

// ---------- Reading controls ----------

function startReadingAll(){
    stopReading();
    reading = true;
    autoIndex = 0;
    readNext(); // begins sequential read
}

function readNext(){
    if (!reading) return;

    if (autoIndex >= SHLOKAS.length){
        reading = false;
        clearHighlights();
        return;
    }

    // Auto page change
    let requiredPage = Math.floor(autoIndex / PER_PAGE);
    if (requiredPage !== page){
        page = requiredPage;
        render();
        setTimeout(()=>highlightFrame(autoIndex), 200);
    } else {
        highlightFrame(autoIndex);
    }

    const s = SHLOKAS[autoIndex];
    const text = s.text + "\\n\\nअर्थ:\\n" + s.meaning + "\\n\\nउदाहरण:\\n" + s.example;
    speak(text);

    // schedule next
    clearTimeout(readTimer);
    readTimer = setTimeout(() => {
        autoIndex++;
        readNext();
    }, 14000);
}

function stopReading(){
    reading = false;
    clearTimeout(readTimer);
    stopTTS();
    clearHighlights();
}

function resumeReading(){
    if (!reading){
        reading = true;
        // continue from current autoIndex (do not reset)
        readNext();
    }
}

// Next button behavior (Option B):
// If reading is true -> jump to next shlok immediately and continue sequential reading.
// If reading is false -> move to next and read it once.
function nextButtonPressed(){
    if (reading){
        // jump to next immediately and continue
        clearTimeout(readTimer);
        autoIndex++;
        if (autoIndex >= SHLOKAS.length) autoIndex = 0;
        readNext();
    } else {
        // not in sequential mode: read next once (and remain not reading)
        let nextIdx = autoIndex + 1;
        if (nextIdx >= SHLOKAS.length) nextIdx = 0;
        readSingle(nextIdx);
        autoIndex = nextIdx; // update pointer
    }
}

function readRandom(){
    // Read only one random shlok; do not enable sequential reading.
    stopReading();
    const i = Math.floor(Math.random() * SHLOKAS.length);

    // jump to page and highlight
    let requiredPage = Math.floor(i / PER_PAGE);
    if (requiredPage !== page){
        page = requiredPage;
        render();
        setTimeout(()=>highlightFrame(i), 200);
    } else {
        highlightFrame(i);
    }

    const s = SHLOKAS[i];
    const text = s.text + "\\n\\nअर्थ:\\n" + s.meaning + "\\n\\nउदाहरण:\\n" + s.example;
    speak(text);
    autoIndex = i; // keep pointer at current
}

function readSingle(i){
    stopReading();

    let requiredPage = Math.floor(i / PER_PAGE);
    if (requiredPage !== page){
        page = requiredPage;
        render();
        setTimeout(()=>highlightFrame(i), 200);
    } else {
        highlightFrame(i);
    }

    const s = SHLOKAS[i];
    const text = s.text + "\\n\\nअर्थ:\\n" + s.meaning + "\\n\\nउदाहरण:\\n" + s.example;
    speak(text);
    autoIndex = i;
}

// ---------- Pagination ----------
function nextPage(){
    page = (page + 1) % Math.ceil(SHLOKAS.length / PER_PAGE);
    render();
}
function prevPage(){
    page = (page - 1 + Math.ceil(SHLOKAS.length / PER_PAGE)) % Math.ceil(SHLOKAS.length / PER_PAGE);
    render();
}

// ---------- Voice UI wiring ----------
function setGender(g){
    selectedGender = g;
    localStorage.setItem('gita_voice_gender', g);
    loadVoices();
    renderVoiceButtons();
}

function setSpeed(s){
    selectedSpeed = s;
    localStorage.setItem('gita_voice_speed', s);
    renderVoiceButtons();
}

function renderVoiceButtons(){
    // Gender buttons
    const f = document.getElementById('femaleBtn');
    const m = document.getElementById('maleBtn');
    f.className = 'toggle' + (selectedGender === 'female' ? ' selected' : '');
    m.className = 'toggle' + (selectedGender === 'male' ? ' selected' : '');

    // Speed buttons
    document.getElementById('verySlowBtn').className = 'toggle' + (selectedSpeed === 'very_slow' ? ' speed-selected' : '');
    document.getElementById('slowBtn').className = 'toggle' + (selectedSpeed === 'slow' ? ' speed-selected' : '');
    document.getElementById('mediumBtn').className = 'toggle' + (selectedSpeed === 'medium' ? ' speed-selected' : '');
}

document.getElementById && (function attachVoiceUI(){
    try {
        document.getElementById('femaleBtn').onclick = function(){ setGender('female'); };
        document.getElementById('maleBtn').onclick = function(){ setGender('male'); };
        document.getElementById('verySlowBtn').onclick = function(){ setSpeed('very_slow'); };
        document.getElementById('slowBtn').onclick = function(){ setSpeed('slow'); };
        document.getElementById('mediumBtn').onclick = function(){ setSpeed('medium'); };
    } catch(e){}
})();

// initial render + voice buttons
render();
renderVoiceButtons();

function exitApp(){
    try { if (typeof Android !== "undefined" && Android && Android.exitApp) Android.exitApp(); } catch(e){}
    try { window.close(); } catch(e){}
}

</script>
</body>
</html>
"""

    # Replace placeholders
    html = html.replace("__PER_PAGE__", str(SHLOKAS_PER_PAGE))
    html = html.replace("__JS_ARRAY__", js_array)

    return html


# ---------------------------------------------------------
# WRITE HTML
# ---------------------------------------------------------
def main():
    flat = flatten_sections(ALL_SHLOKAS)
    html = generate_html(flat)

    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print("✔ HTML Generated:", OUTPUT_HTML)

    try:
        # safe file URL and open in new tab
        file_url = "file:///" + OUTPUT_HTML.replace("\\", "/")
        webbrowser.open_new_tab(file_url)
        print("✔ HTML opened in browser:", file_url)
    except Exception as e:
        print("⚠ Could not auto-open browser:", e)


if __name__ == "__main__":
    main()
