from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
import requests
import json

from client.repository import Repository


class MemoTab(TabbedPanelItem):
    """메모 탭"""

    def __init__(self, repository: Repository, **kwargs):
        super().__init__(**kwargs)
        self.repository = repository

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

        memos = self.repository.get_all_notes()
        for memo in memos:
            self.add_memo_card(memo["name"], memo["content"])

    def add_memo_card(self, name, content):
        """메모 카드 추가"""
        card = Button(text=name, size_hint_y=None, height=50)
        card.bind(on_press=lambda instance: self.show_popup(name, content))
        self.memo_container.add_widget(card)

    def add_new_memo(self, instance):
        """새 메모 추가"""
        popup_content = MemoView(
            note_url=self.note_url, repository=self.repository, parent_tab=self
        )
        popup = Popup(
            title="새 메모 추가",
            content=popup_content,
            size_hint=(0.8, 0.8),
        )
        popup_content.popup = popup
        popup.open()

    def show_popup(self, name, content):
        """팝업으로 메모 내용 보기"""
        popup = Popup(title=name, content=Label(text=content), size_hint=(0.8, 0.8))
        popup.open()


class MemoView(BoxLayout):
    """메모 추가/수정 뷰"""

    def __init__(self, note_url, repository: Repository, parent_tab, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.note_url = note_url
        self.repository = repository
        self.parent_tab = parent_tab
        self.popup = None  # 부모 팝업을 참조하기 위해 설정

        # 입력 필드
        self.name_input = TextInput(hint_text="제목", size_hint_y=None, height=50)
        self.content_input = TextInput(
            hint_text="내용", multiline=True, size_hint_y=None, height=200
        )
        self.tags_input = TextInput(
            hint_text="태그 (쉼표로 구분)", multiline=True, size_hint_y=None, height=50
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
        self.add_widget(self.tags_input)
        self.add_widget(button_layout)

    def save_memo(self, instance):
        """새 메모 저장"""
        name = self.name_input.text
        content = self.content_input.text
        tags = self.tags_input.text

        if not name.strip() or not content.strip():
            print("제목과 내용을 입력하세요!")
            return

        # 서버로 데이터 전송
        try:
            self.repository.new_note(
                **{
                    "name": name,
                    "type": "memo",
                    "content": content,
                    "tags": [tag.strip() for tag in tags.split(",")],
                }
            )
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
