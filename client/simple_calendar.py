from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from datetime import datetime, timedelta


class SimpleCalendar(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 7
        self.rows = 7
        self.current_date = datetime.now()
        self.build_calendar()

    def build_calendar(self):
        self.clear_widgets()

        # 달력 헤더 (요일)
        for day in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]:
            self.add_widget(Label(text=day))

        # 해당 월의 시작 날짜
        first_day = self.current_date.replace(day=1)
        start_offset = (
            first_day.weekday()
        )  # 월요일 기준, 일요일을 시작으로 계산하려면 +1 % 7

        # 이전 달 날짜 채우기
        prev_month_days = (first_day - timedelta(days=start_offset)).day
        for _ in range(start_offset):
            self.add_widget(Label(text=str(prev_month_days)))
            prev_month_days += 1

        # 현재 달 날짜 채우기
        days_in_month = (
            first_day.replace(month=first_day.month % 12 + 1) - timedelta(days=1)
        ).day
        for day in range(1, days_in_month + 1):
            self.add_widget(Button(text=str(day), on_press=self.on_date_select))

        # 다음 달 날짜 채우기
        remaining_days = self.cols * (self.rows - 1) - (start_offset + days_in_month)
        for day in range(1, remaining_days + 1):
            self.add_widget(Label(text=str(day)))

    def on_date_select(self, instance):
        print(f"Selected date: {self.current_date.replace(day=int(instance.text))}")
