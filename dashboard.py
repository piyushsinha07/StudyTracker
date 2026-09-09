from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView

from database import (
    get_pending_tasks, get_setting, get_today_study_seconds,
    get_today_water, get_water_goal, add_water_glass, remove_water_glass,
    get_streak,
)
from navigation import Navigation
from ui_style import StyledCard, PrimaryButton, SecondaryButton, section_label, title_label, subtitle_label
from theme import get_colors

def fmt(seconds):
    seconds = int(seconds or 0)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    return f"{h}h {m:02d}m" if h else f"{m}m"

class Dashboard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(7),
                         padding=[dp(18), dp(10), dp(18), dp(8)], **kwargs)
        self._build()

    def _build(self):
        self.add_widget(Navigation.top_bar(self, "Study Tracker"))

        scroll = ScrollView(bar_width=dp(3), do_scroll_x=False)
        self.content = BoxLayout(orientation="vertical", spacing=dp(9),
                                 padding=[0, dp(2), 0, dp(10)], size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter("height"))

        self.content.add_widget(title_label("Good Evening", 24))
        self.content.add_widget(subtitle_label("Keep going. You are doing great."))

        self.goal_card = StyledCard(orientation="vertical", padding=dp(14),
                                    spacing=dp(3), size_hint_y=None, height=dp(135))
        self.goal_title = Label(text="TODAY'S STUDY GOAL", font_size="10sp",
                                bold=True, color=get_colors()["accent"], halign="left")
        self.goal_card.add_widget(self.goal_title)
        self.study_time = Label(text="0m", font_size="30sp", bold=True,
                                color=get_colors()["text"], halign="left")
        self.goal_card.add_widget(self.study_time)
        self.goal_detail = Label(text="Goal: 4h 00m", font_size="10sp",
                                 color=get_colors()["muted"], halign="left")
        self.goal_card.add_widget(self.goal_detail)
        self.goal_progress = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(7))
        self.goal_card.add_widget(self.goal_progress)
        self.content.add_widget(self.goal_card)

        self.content.add_widget(section_label("Quick Overview"))
        row = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(92))

        self.water_card = StyledCard(orientation="vertical", padding=dp(11))
        self.water_label = Label(text="0 / 8", font_size="19sp", bold=True, color=get_colors()["text"])
        self.water_card.add_widget(Label(text="WATER", font_size="9sp", bold=True, color=get_colors()["accent"]))
        self.water_card.add_widget(self.water_label)
        water_actions = BoxLayout(spacing=dp(5), size_hint_y=None, height=dp(28))
        minus = SecondaryButton(text="-", font_size="14sp")
        plus = SecondaryButton(text="+", font_size="14sp")
        minus.bind(on_release=lambda *_: self.decrease_water())
        plus.bind(on_release=lambda *_: self.increase_water())
        water_actions.add_widget(minus)
        water_actions.add_widget(plus)
        self.water_card.add_widget(water_actions)
        row.add_widget(self.water_card)

        self.streak_card = StyledCard(orientation="vertical", padding=dp(11))
        self.streak_label = Label(text="0 days", font_size="19sp", bold=True, color=get_colors()["text"])
        self.streak_card.add_widget(Label(text="STREAK", font_size="9sp", bold=True, color=get_colors()["accent"]))
        self.streak_card.add_widget(self.streak_label)
        self.streak_card.add_widget(Label(text="Keep it going", font_size="10sp", color=get_colors()["muted"]))
        row.add_widget(self.streak_card)
        self.content.add_widget(row)

        self.content.add_widget(section_label("Today's Tasks"))
        self.tasks_card = StyledCard(orientation="vertical", padding=dp(12),
                                     spacing=dp(4), size_hint_y=None)
        self.content.add_widget(self.tasks_card)

        start = PrimaryButton(text="START STUDYING", size_hint_y=None, height=dp(48))
        start.bind(on_release=lambda *_: Navigation.change_screen(self, "timer"))
        self.content.add_widget(start)

        scroll.add_widget(self.content)
        self.add_widget(scroll)
        self.add_widget(Navigation.bottom_nav(self))
        self.refresh()

    def refresh(self, *_):
        today = get_today_study_seconds()
        try:
            goal = int(get_setting("daily_goal", "14400"))
        except Exception:
            goal = 14400
        self.study_time.text = fmt(today)
        self.goal_detail.text = f"Goal: {fmt(goal)}"
        self.goal_progress.value = min(100, (today / goal * 100) if goal else 0)

        water = get_today_water()
        water_goal = get_water_goal()
        self.water_label.text = f"{water} / {water_goal}"
        self.streak_label.text = f"{get_streak()} days"

        tasks = get_pending_tasks()
        self.tasks_card.clear_widgets()
        self.tasks_card.height = max(dp(58), dp(30) + len(tasks[:4]) * dp(28))
        if not tasks:
            self.tasks_card.add_widget(Label(text="No pending tasks. Nice work.",
                                             font_size="11sp", color=get_colors()["success"]))
        else:
            for task in tasks[:4]:
                self.tasks_card.add_widget(Label(text=f"•  {task['title']}",
                                                 font_size="11sp", color=get_colors()["text"],
                                                 halign="left"))

    def increase_water(self):
        add_water_glass()
        self.refresh()

    def decrease_water(self):
        remove_water_glass()
        self.refresh()
