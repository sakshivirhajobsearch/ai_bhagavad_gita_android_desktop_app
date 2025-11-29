import os
import webbrowser
from data.shlokas import ALL_SHLOKAS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_HTML = os.path.join(
    BASE_DIR,
    "android", "app", "src", "main", "assets", "html", "gita_shlokas.html"
)

SHLOKAS_PER_PAGE = 2
FRAME_HEIGHT_PX = 480  # fixed frame height (pixels)


# ------------------------
# Utility: flatten sections
# ------------------------
def flatten_sections(all_sections):
    flat = []
    for sec in all_sections:
        if isinstance(sec, list):
            sec = sec[0]
        section_title = sec.get("title", "")
        for s in sec.get("shlokas", []):
            flat.append({
                "section": section_title,
                "problem": s.get("problem", ""),
                "reference": s.get("reference", ""),
                "text": s.get("text", ""),
                "meaning": s.get("meaning", ""),
                "example": s.get("example", "")
            })
    print("✔ Total Shlokas Flattened:", len(flat))
    return flat


# ------------------------
# Utility: JS escape text
# ------------------------
def js_escape(text):
    if text is None:
        return ""
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("</", "<\\/")
        .replace("\r", "")
    )


# ------------------------
# Utility: normalize empty example/meaning
# ------------------------
def clean_text(t):
    if not t or str(t).strip() == "":
        return "—"
    return str(t).strip()


# ------------------------
# Generate HTML
# ------------------------
def generate_html(flat_data):
    js_entries = []
    for i, s in enumerate(flat_data, start=1):
        # ensure example/meaning default to visible placeholder
        meaning = clean_text(s.get("meaning", ""))
        example = clean_text(s.get("example", ""))

        js_entries.append(
f"""        {{
            id: {i},
            section: `{js_escape(s.get('section', ''))}`,
            problem: `{js_escape(s.get('problem', ''))}`,
            reference: `{js_escape(s.get('reference', ''))}`,
            text: `{js_escape(s.get('text', ''))}`,
            meaning: `{js_escape(meaning)}`,
            example: `{js_escape(example)}`
        }}"""
        )

    js_array = ",\n".join(js_entries)

    # Note: Use double braces {{ }} in the Python f-string so that JS template strings like ${{
    # s.text }} are preserved correctly in the generated HTML. CSS blocks are also doubled.
    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Bhagwat Geeta by Anurag Vasu Bharti</title>

<style>
body {{
  margin: 0;
  padding: 12px;
  font-family: Arial, sans-serif;
  background: #ff9800;
}}

h1 {{
  text-align:center;
  font-size:24px;
  margin: 6px 0;
}}

h3 {{
  text-align:center;
  font-size:18px;
  margin: 0 0 6px 0;
}}

hr {{
  border: none;
  border-bottom: 2px solid black;
  margin: 6px 0;
}}

.frame {{
  background: white;
  border: 2px solid black;
  border-radius: 12px;
  padding: 12px;
  margin-top: 12px;
  height: {FRAME_HEIGHT_PX}px;
  overflow-y: auto;
}}

.frame.highlight {{
  background: #e7f9e6; /* light green */
  box-shadow: 0 0 12px rgba(0, 128, 64, 0.12);
  border-color: #8fd19b;
}}

button {{
  padding: 7px 14px;
  border: none;
  border-radius: 14px;
  margin: 3px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
}}

.green {{ background:#2e7d32; color:white; }}
.red   {{ background:#b71c1c; color:white; }}
.blue  {{ background:#1565c0; color:white; }}

.small-btn {{
  padding:5px 10px;
  font-size:13px;
}}

pre {{
  white-space: pre-wrap;
  font-size: 16px;
  margin-top: 8px;
}}

.nav {{
  display:flex;
  justify-content: space-between;
  font-weight:bold;
  margin-top:14px;
}}
.controls-row {{
  text-align:center;
  margin: 8px 0;
}}

.voice-controls {{
  display:inline-block;
  margin-left:14px;
  vertical-align: middle;
}}

.toggle {{
  margin: 0 6px;
  padding:6px 10px;
  border-radius:10px;
  border:1px solid rgba(0,0,0,0.12);
  background: white;
  cursor:pointer;
}}
.selected {{
  background:#1976d2; color:white;
  border-color:#115293;
}}
.speed-selected {{
  background:#388e3c; color:white;
  border-color:#2e7d32;
}}
</style>
</head>
<body>

<h1>AI Bhagwat Geeta by Anurag Vasu Bharti</h1>
<hr>
<h3>📘 भगवद गीता में अपनी समस्याओं का समाधान खोजें</h3>
<hr>

<div class="controls-row">
  <button class="green" onclick="startReadingAll()">Start</button>
  <button class="red" onclick="stopReading()">Stop</button>
  <button class="green" onclick="resumeReading()">Resume</button>
  <button class="green" onclick="readRandom()">Random</button>
  <button class="red" onclick="exitApp()">Exit</button>

  <span class="voice-controls" id="voiceControls">
    <!-- Voice toggle buttons inserted by JS -->
  </span>
</div>

<hr>

<div id="content"></div>

<div class="nav">
  <button onclick="prevPage()">⬅ Previous</button>
  <span id="pageInfo"></span>
  <button onclick="nextPage()">Next ➡</button>
</div>

<script>
/* -------------------------
   Data
   ------------------------- */
const PER_PAGE = {SHLOKAS_PER_PAGE};
let page = 0;

let reading = false;
let autoIndex = 0;
let readTimer = null;

let selectedGender = localStorage.getItem('gita_voice_gender') || 'female'; // 'female'|'male'
let selectedSpeed = localStorage.getItem('gita_voice_speed') || 'slow'; // 'slow'|'medium'|'very_slow'

const SHLOKAS = [
{js_array}
];

/* -------------------------
   Voice selection & TTS
   ------------------------- */

let browserVoice = null;

function loadVoices() {{
    let vlist = speechSynthesis.getVoices();
    if (!vlist || vlist.length === 0) {{
        return;
    }}

    // Prefer Hindi / Indian voices when female requested
    if (selectedGender === 'female') {{
        browserVoice = vlist.find(v => (v.lang && v.lang.toLowerCase().includes('hi')) && v.name.toLowerCase().includes('female'))
                      || vlist.find(v => (v.lang && v.lang.toLowerCase().includes('hi')))
                      || vlist.find(v => v.name.toLowerCase().includes('google hindi female'))
                      || vlist.find(v => v.lang && v.lang.toLowerCase().includes('en-in'))
                      || vlist[0];
    }} else {{
        browserVoice = vlist.find(v => (v.lang && v.lang.toLowerCase().includes('hi')) && v.name.toLowerCase().includes('male'))
                      || vlist.find(v => (v.lang && v.lang.toLowerCase().includes('hi')))
                      || vlist.find(v => v.name.toLowerCase().includes('male'))
                      || vlist.find(v => v.lang && v.lang.toLowerCase().includes('en-in'))
                      || vlist[0];
    }}
}}

speechSynthesis.onvoiceschanged = function() {{ loadVoices(); }};

/* speed multipliers */
function speedRateFromSelection() {{
    if (selectedSpeed === 'very_slow') return 0.71;
    if (selectedSpeed === 'slow') return 0.82;
    return 0.95; // medium
}}

/* speak function: Android TTS fallback then browser TTS */
function speak(text) {{
    try {{
        if (typeof Android !== 'undefined' && Android.speak) {{
            // Android native TTS: pass (text, gender, speed)
            try {{
                Android.speak(text, selectedGender, selectedSpeed);
                return;
            }} catch(e) {{
                // fallback to browser if Android speak exists but fails
            }}
        }}
    }} catch(e) {{
        // ignore Android access errors
    }}

    if (!window.speechSynthesis) return;

    if (!browserVoice) loadVoices();

    const u = new SpeechSynthesisUtterance(text);
    u.rate = speedRateFromSelection();
    u.pitch = (selectedGender === 'female') ? 1.05 : 0.95;
    if (browserVoice) u.voice = browserVoice;
    // Prefer Hindi or en-IN language tag if voice doesn't provide
    u.lang = (browserVoice && browserVoice.lang) ? browserVoice.lang : (selectedGender === 'female' ? 'hi-IN' : 'en-IN');

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(u);
}}

function stopSpeaking() {{
    try {{
        if (typeof Android !== 'undefined' && Android.stopSpeak) {{
            Android.stopSpeak();
            return;
        }}
    }} catch(e) {{}}
    if (window.speechSynthesis) window.speechSynthesis.cancel();
}}

/* -------------------------
   UI: voice buttons (top bar)
   ------------------------- */
function renderVoiceControls() {{
    const container = document.getElementById('voiceControls');
    container.innerHTML = '';

    // Gender toggles
    const femaleBtn = document.createElement('button');
    femaleBtn.innerText = '♀ Female';
    femaleBtn.className = 'toggle' + (selectedGender === 'female' ? ' selected' : '');
    femaleBtn.onclick = () => {{
        selectedGender = 'female';
        localStorage.setItem('gita_voice_gender', selectedGender);
        loadVoices();
        renderVoiceControls();
    }};
    container.appendChild(femaleBtn);

    const maleBtn = document.createElement('button');
    maleBtn.innerText = '♂ Male';
    maleBtn.className = 'toggle' + (selectedGender === 'male' ? ' selected' : '');
    maleBtn.onclick = () => {{
        selectedGender = 'male';
        localStorage.setItem('gita_voice_gender', selectedGender);
        loadVoices();
        renderVoiceControls();
    }};
    container.appendChild(maleBtn);

    // Speed toggles
    const speeds = [
        {{ key: 'very_slow', label: 'Very Slow' }},
        {{ key: 'slow', label: 'Slow' }},
        {{ key: 'medium', label: 'Medium' }}
    ];

    speeds.forEach(s => {{
        const b = document.createElement('button');
        b.innerText = s.label;
        b.className = 'toggle' + (selectedSpeed === s.key ? ' speed-selected' : '');
        b.onclick = () => {{
            selectedSpeed = s.key;
            localStorage.setItem('gita_voice_speed', selectedSpeed);
            renderVoiceControls();
        }};
        container.appendChild(b);
    }});
}}

renderVoiceControls();
loadVoices();

/* -------------------------
   Highlight helper
   ------------------------- */
function clearHighlights() {{
    document.querySelectorAll('.frame.highlight').forEach(el => el.classList.remove('highlight'));
}}

function highlightFrame(i) {{
    clearHighlights();
    const el = document.getElementById('shlok_' + i);
    if (el) el.classList.add('highlight');
}}

/* -------------------------
   Individual shlok control
   ------------------------- */
function readSingle(i) {{
    stopReading();
    highlightFrame(i);
    const s = SHLOKAS[i];
    speak(s.text + "\\nअर्थ: " + (s.meaning || '—') + "\\nउदाहरण: " + (s.example || '—'));
}}

function stopSingle(i) {{
    stopSpeaking();
    clearHighlights();
}}

/* -------------------------
   Render page content
   ------------------------- */
function render() {{
    const start = page * PER_PAGE;
    const end = Math.min(start + PER_PAGE, SHLOKAS.length);

    let html = '';
    for (let i = start; i < end; i++) {{
        const s = SHLOKAS[i];

        // using JS template markers ${{...}} so Python f-string doesn't evaluate them
        html += `
        <div class="frame" id="shlok_${{i}}">

            <button class="blue small-btn" onclick="readSingle(${{i}})">▶ Start This Shlok</button>
            <button class="red small-btn" onclick="stopSingle(${{i}})">■ Stop</button>

            <h4>📗 अनुभाग: ${{s.section}}</h4>
            <b>समस्या:</b> ${{s.problem}}<br>
            <b>${{s.reference}}</b><br><br>

            <pre>${{s.text}}</pre>

            <b>अर्थ:</b> ${{s.meaning}}<br><br>
            <b>उदाहरण:</b> ${{s.example}}
        </div>`;
    }}

    document.getElementById('content').innerHTML = html;
    document.getElementById('pageInfo').innerText = 'Page ' + (page + 1) + ' / ' + Math.ceil(SHLOKAS.length / PER_PAGE);
}}

/* -------------------------
   Navigation
   ------------------------- */
function nextPage() {{
    page = (page + 1) % Math.ceil(SHLOKAS.length / PER_PAGE);
    render();
}}
function prevPage() {{
    page = (page - 1 + Math.ceil(SHLOKAS.length / PER_PAGE)) % Math.ceil(SHLOKAS.length / PER_PAGE);
    render();
}}

/* -------------------------
   Sequential reading controls
   ------------------------- */
function startReadingAll() {{
    stopReading();
    reading = true;
    autoIndex = 0;
    readNext();
}}

function readNext() {{
    if (!reading) return;
    if (autoIndex >= SHLOKAS.length) {{
        reading = false;
        clearHighlights();
        return;
    }}
    highlightFrame(autoIndex);
    const s = SHLOKAS[autoIndex];
    speak(s.text + "\\nअर्थ: " + (s.meaning || '—') + "\\nउदाहरण: " + (s.example || '—'));
    readTimer = setTimeout(() => {{
        autoIndex++;
        readNext();
    }}, 12000);
}}

function stopReading() {{
    reading = false;
    clearTimeout(readTimer);
    stopSpeaking();
    clearHighlights();
}}

function resumeReading() {{
    if (!reading) {{
        reading = true;
        readNext();
    }}
}}

function readRandom() {{
    stopReading();
    const idx = Math.floor(Math.random() * SHLOKAS.length);
    readSingle(idx);
}}

/* -------------------------
   Exit / utility
   ------------------------- */
function exitApp() {{
    try {{
        if (typeof Android !== 'undefined' && Android.exitApp) {{
            Android.exitApp();
            return;
        }}
    }} catch(e) {{ }}
    window.close();
}}

/* -------------------------
   Init
   ------------------------- */
render();

</script>
</body>
</html>
"""
    return html


# ------------------------
# Main
# ------------------------
def main():
    print("🔢 Current Sections Loaded:", len(ALL_SHLOKAS))
    flat = flatten_sections(ALL_SHLOKAS)

    print("🔹 Generating HTML...")
    html = generate_html(flat)

    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print("✔ HTML Generated Successfully:")
    print(OUTPUT_HTML)

    # auto open
    try:
        webbrowser.open("file://" + OUTPUT_HTML)
    except:
        pass


if __name__ == "__main__":
    main()
