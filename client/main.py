from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.config import Config
import requests
import json

from client.memo_tab import MemoTab
from client.todo_tab import TodoTab
from client.repository import Repository

Config.set(
    "kivy",
    "default_font",
    [
        "Nanum Square Round",
        "client/assets/fonts/NanumSquareRoundR.ttf",
        "client/assets/fonts/NanumSquareRoundR.ttf",
        "client/assets/fonts/NanumSquareRoundEB.ttf",
        "client/assets/fonts/NanumSquareRoundEB.ttf",
    ],
)
Config.write()


class NoteApp(App):
    def build(self):

        with open("config/network_config.json", "r", encoding="utf-8") as f:
            network_config = json.load(f)

        self.repository: Repository = Repository(**network_config)

        root = BoxLayout(orientation="vertical")
        self.tab_panel = TabbedPanel()
        self.tab_panel.do_default_tab = False

        # 필터 패널 추가
        self.filter_panel = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=50
        )
        self.add_filter_controls()
        root.add_widget(self.filter_panel)

        # TabbedPanel 추가
        root.add_widget(self.tab_panel)
        return root

    def add_filter_controls(self):
        """필터 컨트롤(보기 버튼 및 체크박스) 추가"""
        self.view_button = Button(text="보기", size_hint=(None, 1), width=100)
        self.view_button.bind(on_press=self.toggle_filters)
        self.filter_panel.add_widget(self.view_button)

        self.filters = {}
        for item in ["메모", "일정", "할 일"]:
            box = BoxLayout(orientation="horizontal")
            checkbox = CheckBox(size_hint=(None, 1), size=(30, 30))
            checkbox.bind(
                active=lambda _, value, name=item: self.on_filter_toggle(name, value)
            )
            label = Label(text=item, size_hint=(None, 1), width=80)
            box.add_widget(checkbox)
            box.add_widget(label)
            box.size_hint_x = None
            box.width = 120
            self.filter_panel.add_widget(box)
            self.filters[item] = box
            box.opacity = 0
            box.disabled = True

    def toggle_filters(self, instance):
        """필터 컨트롤 표시/숨김"""
        for box in self.filters.values():
            if box.opacity == 0:
                box.opacity = 1
                box.disabled = False
            else:
                box.opacity = 0
                box.disabled = True

    def on_filter_toggle(self, name, value):
        """필터 활성화/비활성화 시 탭 추가/제거"""
        if value:
            self.add_tab(name)
        else:
            self.remove_tab(name)

    def add_tab(self, name):
        """탭 추가"""
        if name == "메모":
            tab = MemoTab(self.repository)
        elif name == "일정":
            tab = CalendarTab(self.repository)
        elif name == "할 일":
            tab = TodoTab(self.repository)
        else:
            return
        tab.text = name
        self.tab_panel.add_widget(tab)

    def remove_tab(self, name):
        """탭 제거"""
        for tab in self.tab_panel.tab_list:
            if tab.text == name:
                self.tab_panel.remove_widget(tab)
                break


class CalendarTab(TabbedPanelItem):
    """일정 탭"""

    def __init__(self, repository, **kwargs):
        super().__init__(**kwargs)
        self.repository = repository
        layout = BoxLayout()
        self.add_widget(layout)
        self.load_calendar()

    def load_calendar(self):
        """서버에서 일정 데이터 로드"""
        events = self.repository.filtered_notes(type="event")


if __name__ == "__main__":
    NoteApp().run()
