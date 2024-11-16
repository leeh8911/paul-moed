from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.config import Config
import requests
import json

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

        self.server_url = f"{network_config['protocol']}://{network_config['host']}:{network_config['port']}"  # 서버 주소
        self.note_url = f"{self.server_url}/notes"

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
            tab = MemoTab(self.note_url)
        elif name == "일정":
            tab = CalendarTab(self.note_url)
        elif name == "할 일":
            tab = TodoTab(self.note_url)
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


class MemoTab(TabbedPanelItem):
    """메모 탭"""

    def __init__(self, note_url, **kwargs):
        super().__init__(**kwargs)
        self.note_url = note_url

        layout = BoxLayout(orientation="vertical")

        # 상단 - 검색 바와 메모 추가 버튼
        search_add_bar = BoxLayout(size_hint_y=None, height=50)
        self.search_bar = TextInput(hint_text="검색", size_hint_x=0.8)
        self.add_button = Button(text="메모 추가", size_hint_x=0.2)
        self.add_button.bind(on_press=self.add_new_memo)
        search_add_bar.add_widget(self.search_bar)
        search_add_bar.add_widget(self.add_button)
        layout.add_widget(search_add_bar)

        # 하단 - 메모 리스트
        self.scroll_view = ScrollView()
        self.memo_container = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.memo_container.bind(minimum_height=self.memo_container.setter("height"))
        self.scroll_view.add_widget(self.memo_container)
        layout.add_widget(self.scroll_view)

        # 메모 데이터 로드
        self.load_memos()

        self.add_widget(layout)

    def load_memos(self):
        """서버에서 메모 데이터 로드"""
        try:
            response = requests.get(f"{self.note_url}")
            if response.status_code == 200:
                memos = response.json()
                for memo in memos:
                    self.add_memo_card(memo["title"], memo["content"])
        except requests.exceptions.ConnectionError:
            print("서버에 연결할 수 없습니다.")

    def add_memo_card(self, title, content):
        """메모 카드 추가"""
        card = Button(text=title, size_hint_y=None, height=50)
        card.bind(on_press=lambda instance: self.show_popup(title, content))
        self.memo_container.add_widget(card)

    def add_new_memo(self, instance):
        """새 메모 추가"""
        popup_content = MemoView(note_url=self.note_url, parent_tab=self)
        popup = Popup(
            title="새 메모 추가",
            content=popup_content,
            size_hint=(0.8, 0.8),
        )
        popup_content.popup = popup
        popup.open()

    def show_popup(self, title, content):
        """팝업으로 메모 내용 보기"""
        popup = Popup(title=title, content=Label(text=content), size_hint=(0.8, 0.8))
        popup.open()


class MemoView(BoxLayout):
    """메모 추가/수정 뷰"""

    def __init__(self, note_url, parent_tab, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.note_url = note_url
        self.parent_tab = parent_tab
        self.popup = None  # 부모 팝업을 참조하기 위해 설정

        # 입력 필드
        self.name_input = TextInput(hint_text="제목", size_hint_y=None, height=50)
        self.content_input = TextInput(
            hint_text="내용", multiline=True, size_hint_y=None, height=200
        )

        # 버튼 레이아웃
        button_layout = BoxLayout(size_hint_y=None, height=50)
        save_button = Button(text="저장")
        save_button.bind(on_press=self.save_memo)
        cancel_button = Button(text="취소")
        cancel_button.bind(on_press=lambda instance: self.popup.dismiss())

        button_layout.add_widget(save_button)
        button_layout.add_widget(cancel_button)

        # 메인 레이아웃에 추가
        self.add_widget(self.name_input)
        self.add_widget(self.content_input)
        self.add_widget(button_layout)

    def save_memo(self, instance):
        """새 메모 저장"""
        name = self.name_input.text
        content = self.content_input.text

        if not name.strip() or not content.strip():
            print("제목과 내용을 입력하세요!")
            return

        # 서버로 데이터 전송
        try:
            response = requests.post(
                f"{self.note_url}",
                json={"name": name, "type": "memo", "content": content},
            )
            if response.status_code == 201:
                print("메모가 저장되었습니다!")
                self.parent_tab.add_memo_card(name, content)
                self.popup.dismiss()
            else:
                print("메모 저장 실패!")
        except requests.exceptions.ConnectionError:
            print("서버에 연결할 수 없습니다!")


class CalendarTab(TabbedPanelItem):
    """일정 탭"""

    def __init__(self, note_url, **kwargs):
        super().__init__(**kwargs)
        self.note_url = note_url
        layout = BoxLayout()
        self.add_widget(layout)
        self.load_calendar()

    def load_calendar(self):
        """서버에서 일정 데이터 로드"""
        try:
            response = requests.get(f"{self.note_url}/events")
            if response.status_code == 200:
                events = response.json()
                # TODO: 달력 UI에 일정 추가
                print(events)
        except requests.exceptions.ConnectionError:
            print("서버에 연결할 수 없습니다.")


class TodoTab(TabbedPanelItem):
    """할 일 탭"""

    def __init__(self, note_url, **kwargs):
        super().__init__(**kwargs)
        self.note_url = note_url
        layout = BoxLayout()
        self.add_widget(layout)
        self.load_todos()

    def load_todos(self):
        """서버에서 할 일 데이터 로드"""
        try:
            response = requests.get(f"{self.note_url}/todos")
            if response.status_code == 200:
                todos = response.json()
                # TODO: 태그별 할 일 목록 추가
                print(todos)
        except requests.exceptions.ConnectionError:
            print("서버에 연결할 수 없습니다.")


if __name__ == "__main__":
    NoteApp().run()
