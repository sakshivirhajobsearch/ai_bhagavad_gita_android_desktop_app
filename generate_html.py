import os
from data.shlokas import ALL_SHLOKAS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------
# Single final output file
# ------------------------------------------
OUTPUT_HTML = os.path.join(
    BASE_DIR,
    "android", "app", "src", "main", "assets", "html", "gita_shlokas.html"
)

OLD_HTML_FILE = os.path.join(
    BASE_DIR,
    "android", "app", "src", "main", "assets", "html", "gita_problems.html"
)

SHLOKAS_PER_PAGE = 2


def flatten_sections(all_sections):
    flat = []

    for sec in all_sections:
        if isinstance(sec, list):
            sec = sec[0]

        title = sec.get("title", "")

        for s in sec.get("shlokas", []):
            flat.append({
                "section": title,
                "problem": s.get("problem", ""),
                "reference": s.get("reference", ""),
                "text": s.get("text", ""),
                "meaning": s.get("meaning", ""),
                "example": s.get("example", "")
            })

    print("✅ Total Shlokas Flattened:", len(flat))
    return flat


def js_escape(text):
    if not text:
        return ""
    return (
        text.replace("\\", "\\\\")
            .replace("`", "\\`")
            .replace("</", "<\\/")
    )


def generate_html(flat):

    js_items = []
    for i, s in enumerate(flat, start=1):
        js_items.append(
            "        {\n"
            f"            id: {i},\n"
            f"            section: `{js_escape(s['section'])}`,\n"
            f"            problem: `{js_escape(s['problem'])}`,\n"
            f"            reference: `{js_escape(s['reference'])}`,\n"
            f"            text: `{js_escape(s['text'])}`,\n"
            f"            meaning: `{js_escape(s['meaning'])}`,\n"
            f"            example: `{js_escape(s['example'])}`\n"
            "        }"
        )

    js_array = ",\n".join(js_items)

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI Bhagavad Gita by Anurag Vasu Bharti</title>

<style>
body {{
    background: #ff9800;
    font-family: Arial;
    padding: 10px;
}}
.frame {{
    background: white;
    padding: 12px;
    border: 2px solid black;
    border-radius: 10px;
    margin-bottom: 16px;
}}
button {{
    padding: 8px 16px;
    margin: 4px;
    border: none;
    border-radius: 16px;
    font-weight: bold;
}}
.green {{ background: green; color: white; }}
.red {{ background: red; color: white; }}
.blue {{ background: #007bff; color: white; }}
.nav {{
    display: flex;
    justify-content: space-between;
    margin-top: 12px;
}}
</style>
</head>

<body>

<h1 style="text-align:center;">AI Bhagwat Geeta by Anurag Vasu Bharti</h1>
<h3 style="text-align:center;">📘 भगवद गीता में अपनी समस्याओं का समाधान खोजें</h3>

<div style="text-align:center;">
    <button class="green" onclick="startAuto()">Start</button>
    <button class="red" onclick="stopAuto()">Stop</button>
    <button class="green" onclick="resumeAuto()">Resume</button>
    <button class="red" onclick="randomPage()">Random</button>
    <button class="blue" onclick="readShloka()">🔊 AI पढ़े</button>
    <button class="red" onclick="Android.exitApp()">Exit</button>
</div>

<hr/>

<div id="content"></div>

<div class="nav">
    <button onclick="prevPage()">⬅ पिछला</button>
    <span id="pageInfo"></span>
    <button onclick="nextPage()">अगला ➡</button>
</div>

<script>
const SHLOKAS = [
{js_array}
];

const PER_PAGE = {SHLOKAS_PER_PAGE};
let page = 0;
let autoTimer = null;

function render() {{
    const start = page * PER_PAGE;
    const end = Math.min(start + PER_PAGE, SHLOKAS.length);

    const c = document.getElementById("content");
    c.innerHTML = "";

    for (let i = start; i < end; i++) {{
        const s = SHLOKAS[i];

        c.innerHTML += `
        <div class="frame">
            <b>📗 अनुभाग:</b> ${{s.section}}<br><br>
            <b>🧩 समस्या:</b> ${{s.problem}}<br><br>
            <b>📌 संदर्भ:</b> ${{s.reference}}<br><br>

            <b>📜 संस्कृत श्लोक:</b>
            <pre>${{s.text}}</pre>

            <b>📝 अर्थ:</b><br>${{s.meaning}}<br><br>

            <b>🌿 उदाहरण:</b><br>${{s.example}}
        </div>`;
    }}

    document.getElementById("pageInfo").innerHTML =
        "Page " + (page + 1) + " / " + Math.ceil(SHLOKAS.length / PER_PAGE);
}}

function nextPage() {{
    page = (page + 1) % Math.ceil(SHLOKAS.length / PER_PAGE);
    render();
}}

function prevPage() {{
    page = (page - 1 + Math.ceil(SHLOKAS.length / PER_PAGE)) %
           Math.ceil(SHLOKAS.length / PER_PAGE);
    render();
}}

function randomPage() {{
    page = Math.floor(Math.random() * Math.ceil(SHLOKAS.length / PER_PAGE));
    render();
}}

function startAuto() {{
    stopAuto();
    autoTimer = setInterval(nextPage, 15000);
}}

function stopAuto() {{
    if (autoTimer) {{
        clearInterval(autoTimer);
        autoTimer = null;
    }}
}}

function resumeAuto() {{
    if (!autoTimer) startAuto();
}}

function readShloka() {{
    const s = SHLOKAS[page * PER_PAGE];

    let textToRead = 
        "समस्या: " + s.problem + ". " +
        "संदर्भ: " + s.reference + ". " +
        "श्लोक: " + s.text + ". " +
        "अर्थ: " + s.meaning + ". " +
        "उदाहरण: " + s.example;

    let msg = new SpeechSynthesisUtterance(textToRead);
    msg.lang = "hi-IN";
    speechSynthesis.speak(msg);
}}

render();
</script>

</body>
</html>
"""

    return html


def main():
    if os.path.exists(OLD_HTML_FILE):
        try:
            os.remove(OLD_HTML_FILE)
            print("🗑 Deleted old file:", OLD_HTML_FILE)
        except:
            pass

    flat = flatten_sections(ALL_SHLOKAS)
    html = generate_html(flat)

    os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ FINAL HTML GENERATED:")
    print(OUTPUT_HTML)


if __name__ == "__main__":
    main()
