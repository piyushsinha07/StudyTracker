from datetime import datetime
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from database import (
    get_today_study_seconds, get_week_study_seconds,
    get_water_goal, get_today_water, get_streak,
    get_task_count, get_subjects, get_subject_study_seconds, get_recent_sessions
)
from navigation import Navigation
from ui_style import (
    StyledCard, section_label, title_label, subtitle_label
)
from theme import get_colors

def fmt(sec):
    sec = int(sec or 0)
    h = sec // 3600
    m = (sec % 3600) // 60
    return f"{h}h {m:02d}m" if h else f"{m}m"

class StatsPage(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            spacing=dp(7),
            padding=[dp(18), dp(10), dp(18), dp(8)],
            **kwargs
        )
        self.navigate = lambda name: None
        self.build()

    def build(self):
        self.clear_widgets()
        self.add_widget(Navigation.top_bar(self, "Statistics"))

        header = BoxLayout(
            orientation="vertical", size_hint_y=None, height=dp(58)
        )
        header.add_widget(title_label("Statistics", 23))
        header.add_widget(subtitle_label("Understand your study habits and consistency"))
        self.add_widget(header)

        scroll = ScrollView(bar_width=dp(2), do_scroll_x=False)
        self.box = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=[0, dp(2), 0, dp(12)],
            size_hint_y=None
        )
        self.box.bind(minimum_height=self.box.setter("height"))
        scroll.add_widget(self.box)
        self.add_widget(scroll)

        self.add_widget(Navigation.bottom_nav(self))
        self.refresh()

    def refresh(self):
        self.box.clear_widgets()

        total_tasks, done_tasks = get_task_count()

        self.box.add_widget(section_label("Overview"))

        row1 = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(92)
        )
        row1.add_widget(self.metric_card("TODAY", fmt(get_today_study_seconds()), "study time", get_colors()["accent"]))
        row1.add_widget(self.metric_card("THIS WEEK", fmt(get_week_study_seconds()), "last 7 days", get_colors()["accent"]))
        self.box.add_widget(row1)

        row2 = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(92)
        )
        row2.add_widget(self.metric_card(
            "WATER",
            f"{get_today_water()} / {get_water_goal()}",
            "glasses today",
            get_colors()["success"]
        ))
        row2.add_widget(self.metric_card(
            "STREAK",
            f"{get_streak()} days",
            "current streak",
            get_colors()["accent"]
        ))
        self.box.add_widget(row2)

        task_card = StyledCard(
            orientation="horizontal",
            padding=dp(13),
            size_hint_y=None,
            height=dp(66)
        )
        task_card.add_widget(Label(
            text="TASKS",
            color=get_colors()["accent"], font_size="9sp", bold=True,
            size_hint_x=None, width=dp(60)
        ))
        task_card.add_widget(Label(
            text=f"{done_tasks} / {total_tasks} completed",
            color=get_colors()["text"], font_size="15sp", bold=True,
            halign="left"
        ))
        self.box.add_widget(task_card)

        self.box.add_widget(section_label("Subject Breakdown"))

        subjects = [
            {"name": s["name"], "seconds": get_subject_study_seconds(s["id"])}
            for s in get_subjects()
        ]
        subjects = [s for s in subjects if s["seconds"] > 0]
        if not subjects:
            self.add_empty("No subject data yet.")
        else:
            for row in subjects:
                card = StyledCard(
                    orientation="horizontal",
                    padding=[dp(13), dp(7)],
                    size_hint_y=None,
                    height=dp(55)
                )
                card.add_widget(Label(
                    text=row["name"],
                    color=get_colors()["text"], font_size="12sp", bold=True,
                    halign="left"
                ))
                card.add_widget(Label(
                    text=fmt(row["seconds"]),
                    color=get_colors()["accent"], font_size="12sp", bold=True,
                    halign="right"
                ))
                self.box.add_widget(card)

        self.box.add_widget(section_label("Recent History"))

        sessions = get_recent_sessions(8)
        if not sessions:
            self.add_empty("No study sessions recorded yet.")
        else:
            for row in sessions:
                name = row["subject_name"] or "General"
                try:
                    when = datetime.fromisoformat(row["started_at"]).strftime("%d %b, %H:%M")
                except Exception:
                    when = row["started_at"][:16]
                card = StyledCard(
                    orientation="horizontal",
                    padding=[dp(13), dp(7)],
                    size_hint_y=None,
                    height=dp(58)
                )
                info = BoxLayout(orientation="vertical")
                info.add_widget(Label(
                    text=name, color=get_colors()["text"], font_size="11sp", bold=True
                ))
                info.add_widget(Label(
                    text=when, color=get_colors()["muted"], font_size="9sp"
                ))
                card.add_widget(info)
                card.add_widget(Label(
                    text=fmt(row["duration_seconds"]),
                    color=get_colors()["success"], font_size="11sp", bold=True,
                    halign="right"
                ))
                self.box.add_widget(card)

    def metric_card(self, title, value, note, accent):
        card = StyledCard(
            orientation="vertical",
            padding=[dp(12), dp(8)]
        )
        card.add_widget(Label(
            text=title, color=accent, font_size="8sp", bold=True
        ))
        card.add_widget(Label(
            text=value, color=get_colors()["text"], font_size="19sp", bold=True
        ))
        card.add_widget(Label(
            text=note, color=get_colors()["muted"], font_size="9sp"
        ))
        return card

    def add_empty(self, text):
        card = StyledCard(
            orientation="vertical",
            padding=dp(12),
            size_hint_y=None,
            height=dp(60)
        )
        card.add_widget(Label(text=text, color=get_colors()["muted"], font_size="10sp"))
        self.box.add_widget(card)

StatsScreen = StatsPage
