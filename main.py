import os, sys
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty, DictProperty, StringProperty
from kivy.core.text import LabelBase

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.shlokas import ALL_SHLOKAS
from utils.exporter import export_to_txt

FONT_PATH = os.path.join('android','app','src','main','assets','fonts','NotoSerifDevanagari-Regular.ttf')

if os.path.exists(FONT_PATH):
    LabelBase.register(name="DevFont", fn_regular=FONT_PATH)
    print("✅ Sanskrit Font Loaded")
else:
    print("❌ Font missing:", FONT_PATH)


def flatten(all_sec):
    result = []
    for sec in all_sec:
        if isinstance(sec, list):
            sec = sec[0]
        title = sec.get("title", "")
        for s in sec.get("shlokas", []):
            result.append({
                "section": title,
                "problem": s.get("problem", ""),
                "sloka": s.get("reference", ""),
                "text": s.get("text", ""),
                "meaning": s.get("meaning", ""),
                "example": s.get("example", "")
            })
    return result


class MainScreen(BoxLayout):

    sections = ListProperty([])
    selected = DictProperty({})
    status_text = StringProperty("")

    def __init__(self, **kw):
        super().__init__(**kw)
        self.sections = flatten(ALL_SHLOKAS)
        self.load_list()

    def load_list(self):
        # Requires a RecycleView with id 'rv' and a Label with id 'content_label' in kv
        self.ids.rv.data = [
            {"text": f"{x['problem']} ({x['sloka']})", "index": i}
            for i, x in enumerate(self.sections)
        ]
        if self.sections:
            self.show(0)

    def on_select_problem(self, i):
        self.show(i)

    def show(self, i):
        d = self.sections[i]
        self.ids.content_label.text = (
            f"📖 {d['section']}\n\n"
            f"📜 {d['sloka']}\n\n"
            f"{d['text']}\n\n"
            f"Meaning: {d['meaning']}\n\n"
            f"Example: {d['example']}"
        )

    def export_all(self):
        p = export_to_txt(self.sections)
        self.status_text = f"Saved: {p}"


class GitaApp(App):
    def build(self):
        self.title = "Bhagavad Gita Solutions"
        return MainScreen()


if __name__ == "__main__":
    GitaApp().run()
