from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.tabbedpanel import TabbedPanel
from kivymd.uix.card import MDCard
import requests
import json


# Config 파일 읽기
with open("config/network_config.json", "r") as network_config_file:
    network_config = json.load(network_config_file)

with open("config/client_config.json", "r") as client_config_file:
    client_config = json.load(client_config_file)

# 네트워크 설정
server_url = f"{network_config['protocol']}://{network_config['host']}:{network_config['port']}/notes"


class NoteCard(MDCard):
    """
    카드 형태로 노트를 표시
    """

    def __init__(self, note, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = "10dp"
        self.size_hint = (1, None)
        self.height = "150dp"

        self.add_widget(
            Label(text=f"[b]{note['name']}[/b]", markup=True, font_size="18sp")
        )
        self.add_widget(
            Label(
                text=f"Type: {note['type']}", font_size="14sp", color=(0.5, 0.5, 0.5, 1)
            )
        )
        self.add_widget(
            Label(
                text=f"Tags: {', '.join(note['tags'])}",
                font_size="12sp",
                color=(0.3, 0.3, 0.3, 1),
            )
        )
        self.add_widget(Label(text=f"Content: {note['content']}", font_size="12sp"))


class NoteApp(App):
    """
    노트 관리 앱 메인 클래스
    """

    def build(self):
        self.title = "Note Manager"
        self.root = TabbedPanel(do_default_tab=False)

        # Tab 1: 노트 생성
        create_tab = BoxLayout(orientation="vertical", padding="10dp", spacing="10dp")
        self.create_inputs = {}
        create_tab.add_widget(
            Label(
                text="Create Note", font_size="20sp", size_hint=(1, None), height="40dp"
            )
        )

        fields = [
            ("type", "Type (e.g., memo, event, task)"),
            ("name", "Name"),
            ("content", "Content"),
            ("tags", "Tags (comma-separated)"),
        ]

        for field, placeholder in fields:
            self.create_inputs[field] = TextInput(
                hint_text=placeholder, multiline=False
            )
            create_tab.add_widget(self.create_inputs[field])

        create_button = Button(
            text="Create Note",
            size_hint=(1, None),
            height="40dp",
            on_press=self.create_note,
        )
        create_tab.add_widget(create_button)
        tab = TabbedPanel()
        tab.tab_text = "Create Note"
        tab.add_widget(create_tab)
        self.root.add_widget(tab)

        # Tab 2: 노트 조회
        view_tab = BoxLayout(orientation="vertical", padding="10dp", spacing="10dp")
        self.notes_container = GridLayout(cols=1, size_hint_y=None)
        self.notes_container.bind(minimum_height=self.notes_container.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.notes_container)
        view_tab.add_widget(scroll)

        refresh_button = Button(
            text="Refresh Notes",
            size_hint=(1, None),
            height="40dp",
            on_press=self.load_notes,
        )
        view_tab.add_widget(refresh_button)
        tab = TabbedPanel()
        tab.tab_text = "View Notes"
        tab.add_widget(view_tab)
        self.root.add_widget(tab)

        return self.root

    def create_note(self, instance):
        """
        노트 생성
        """
        data = {key: field.text for key, field in self.create_inputs.items()}
        data["tags"] = data["tags"].split(",") if data["tags"] else []

        if not data["type"] or not data["name"] or not data["content"]:
            return

        response = requests.post(server_url, json=data)
        if response.status_code == 201:
            for field in self.create_inputs.values():
                field.text = ""
            self.load_notes()  # 노트 리스트 갱신

    def load_notes(self, *args):
        """
        모든 노트를 로드
        """
        response = requests.get(server_url)
        if response.status_code == 200:
            notes = response.json()["notes"]
            self.notes_container.clear_widgets()
            for note in notes:
                self.notes_container.add_widget(NoteCard(note))


if __name__ == "__main__":
    NoteApp().run()
