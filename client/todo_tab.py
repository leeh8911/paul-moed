from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
import requests
import logging


class TodoTab(TabbedPanelItem):
    """할 일 탭"""

    def __init__(self, note_url, **kwargs):
        super().__init__(**kwargs)
        self.note_url = note_url
        self.text = "할 일"

        # 메인 레이아웃
        layout = BoxLayout(orientation="vertical")

        # ScrollView 및 섹션 컨테이너
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.section_container = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.section_container.bind(
            minimum_height=self.section_container.setter("height")
        )
        self.scroll_view.add_widget(self.section_container)
        layout.add_widget(self.scroll_view)

        # 상단 버튼: Done 보기/숨기기 & 할 일 추가
        button_layout = BoxLayout(size_hint_y=None, height=50)

        # Done 상태 보기/숨기기 토글 버튼
        self.done_toggle = ToggleButton(text="Done 보기")
        self.done_toggle.bind(on_press=self.toggle_done_visibility)
        button_layout.add_widget(self.done_toggle)

        # 할 일 추가 버튼
        add_button = Button(text="할 일 추가")
        add_button.bind(on_press=self.open_add_task_popup)
        button_layout.add_widget(add_button)

        layout.add_widget(button_layout)

        self.add_widget(layout)

        # 데이터 로드
        self.show_done = False  # 기본적으로 done 상태 숨김
        self.load_tasks()

    def load_tasks(self):
        """서버에서 할 일 데이터 로드"""
        try:
            response = requests.get(f"{self.note_url}/filter?type=task")
            if response.status_code == 200:
                tasks = response.json()
                logging.info(f"TodoTab - number of tasks: {len(tasks)}")
                self.populate_tasks(tasks)
            else:
                print("할 일 데이터 로드 실패")
        except requests.exceptions.ConnectionError:
            print("서버에 연결할 수 없습니다.")

    def populate_tasks(self, tasks):
        """할 일 섹션 및 태스크 데이터 표시"""
        self.section_container.clear_widgets()  # 기존 위젯 초기화
        tasks_by_tag = {}

        # 태그별로 데이터 분류
        for task in tasks:
            if not self.show_done and task["done"]:
                continue  # done 상태 숨기기
            for tag in task["tags"]:
                if tag not in tasks_by_tag:
                    tasks_by_tag[tag] = []
                tasks_by_tag[tag].append(task)

        # 태그별 섹션 추가
        for tag, tasks in tasks_by_tag.items():
            section = TodoSection(tag, tasks, self.note_url, self)
            self.section_container.add_widget(section)

        # Done 섹션 추가
        if self.show_done:
            done_tasks = [task for task in tasks if task["done"]]
            if done_tasks:
                done_section = TodoSection("Done", done_tasks, self.note_url, self)
                self.section_container.add_widget(done_section)

    def toggle_done_visibility(self, instance):
        """Done 상태 표시/숨기기 토글"""
        self.show_done = not self.show_done
        self.load_tasks()

    def open_add_task_popup(self, instance):
        """할 일 추가 팝업 열기"""
        popup_layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        # 사용자 입력 필드
        name_input = TextInput(hint_text="제목")
        content_input = TextInput(hint_text="내용")
        tags_input = TextInput(hint_text="태그 (쉼표로 구분)")
        popup_layout.add_widget(Label(text="할 일 추가"))
        popup_layout.add_widget(name_input)
        popup_layout.add_widget(content_input)
        popup_layout.add_widget(tags_input)

        # 하단 버튼 레이아웃
        button_layout = BoxLayout(size_hint_y=None, height=50)
        cancel_button = Button(text="취소")
        save_button = Button(text="저장")
        button_layout.add_widget(cancel_button)
        button_layout.add_widget(save_button)

        popup_layout.add_widget(button_layout)

        popup = Popup(title="할 일 추가", content=popup_layout, size_hint=(0.8, 0.5))

        # 버튼 동작
        cancel_button.bind(on_press=popup.dismiss)
        save_button.bind(
            on_press=lambda x: self.add_task(
                name_input.text, content_input.text, tags_input.text, popup
            )
        )

        popup.open()

    def add_task(self, name: str, content: str, tags: str, popup):
        """새 할 일 서버에 저장"""
        if not name:
            print("할 일 제목은 필수입니다.")
            return

        task_data = {
            "name": name,
            "type": "task",
            "content": content,
            "tags": [tag.strip() for tag in tags.split(",")],
            "done": False,
        }
        try:
            response = requests.post(f"{self.note_url}", json=task_data)
            if response.status_code == 201:
                print("새 할 일 추가 성공")
                self.load_tasks()  # 데이터 새로고침
            else:
                print("새 할 일 추가 실패")
        except requests.exceptions.ConnectionError:
            print("서버에 연결할 수 없습니다.")
        finally:
            popup.dismiss()


class TodoSection(BoxLayout):
    """태그별 할 일 섹션"""

    def __init__(self, tag, tasks, note_url, parent_tab, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.note_url = note_url
        self.parent_tab = parent_tab

        # 섹션 타이틀
        title = Label(text=f"[b]{tag}[/b]", size_hint_y=None, height=30, markup=True)
        self.add_widget(title)

        # 태스크 리스트
        for task in tasks:
            self.add_widget(TaskItem(task, note_url, parent_tab))


class TaskItem(BoxLayout):
    """할 일 항목"""

    def __init__(self, task, note_url, parent_tab, **kwargs):
        super().__init__(
            orientation="horizontal", size_hint_y=None, height=50, **kwargs
        )
        self.note_url = note_url
        self.parent_tab = parent_tab
        self.task = task

        # 체크박스
        self.checkbox = CheckBox(active=task["done"])
        self.checkbox.bind(active=self.update_task_status)
        self.add_widget(self.checkbox)

        # 태스크 제목
        self.label = Label(
            text=task["name"], halign="left", valign="middle", size_hint_x=0.8
        )
        self.label.bind(size=self.label.setter("text_size"))  # 텍스트 래핑
        self.add_widget(self.label)

    def update_task_status(self, instance, value):
        """태스크 상태 업데이트"""
        self.task["done"] = value
        try:
            response = requests.put(
                f"{self.note_url}/{self.task['id']}", json=self.task
            )
            if response.status_code == 200:
                print(f"Task '{self.task['name']}' 상태 업데이트 완료.")
                self.parent_tab.load_tasks()
            else:
                print("Task 상태 업데이트 실패.")
        except requests.exceptions.ConnectionError:
            print("서버에 연결할 수 없습니다.")
