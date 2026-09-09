from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from kivy.graphics import Color, RoundedRectangle

from database import (
    get_setting,
    get_today_study_seconds,
    get_week_study_seconds,
    get_streak,
    get_tasks,
    get_subjects,
    get_recent_sessions
)

from theme import get_colors
from navigation import Navigation


# =========================================================
# PROFILE CARD
# =========================================================

class ProfileCard(BoxLayout):

    def __init__(self, **kwargs):

        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            padding=dp(12),
            spacing=dp(5),
            **kwargs
        )

        self.bind(
            minimum_height=self.setter("height")
        )

        c = get_colors()

        with self.canvas.before:

            Color(
                c["card2"][0],
                c["card2"][1],
                c["card2"][2],
                1
            )

            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(14)]
            )

        self.bind(
            pos=self.update_graphics,
            size=self.update_graphics
        )

    def update_graphics(self, *args):

        self.bg.pos = self.pos
        self.bg.size = self.size


# =========================================================
# PROFILE PAGE
# =========================================================

class ProfilePage(BoxLayout):

    def __init__(self, **kwargs):

        super().__init__(
            orientation="vertical",
            spacing=dp(6),
            padding=[
                dp(10),
                dp(7),
                dp(10),
                dp(7)
            ],
            **kwargs
        )

        self.navigate = lambda name: None

        self.previous_screen = "home"

        self.build()


    # =====================================================
    # BUILD
    # =====================================================

    def build(self):

        self.clear_widgets()

        c = get_colors()

        # =================================================
        # TOP BAR
        # =================================================

        self.add_widget(
            Navigation.top_bar(
                "Profile",
                self.navigate
            )
        )


        # =================================================
        # CONTENT
        # =================================================

        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(3)
        )

        self.content = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=[
                0,
                dp(4),
                0,
                dp(10)
            ],
            size_hint_y=None
        )

        self.content.bind(
            minimum_height=
            self.content.setter("height")
        )

        scroll.add_widget(
            self.content
        )

        self.add_widget(
            scroll
        )


        # =================================================
        # BACK BUTTON
        # =================================================

        back = Button(
            text="Back",
            font_size=14,
            bold=True,
            background_normal="",
            background_color=c["accent"],
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(45)
        )

        back.bind(
            on_release=self.go_back
        )

        self.add_widget(
            back
        )


        self.refresh()


    # =====================================================
    # REFRESH
    # =====================================================

    def refresh(self):

        self.refresh_profile()


    # =====================================================
    # BACK
    # =====================================================

    def go_back(self, *args):

        if self.previous_screen:

            self.navigate(
                self.previous_screen
            )

        else:

            self.navigate(
                "home"
            )


    # =====================================================
    # LABEL
    # =====================================================

    def make_label(
        self,
        text,
        size=12,
        color=None,
        bold=False,
        height=25
    ):

        c = get_colors()

        if color is None:

            color = c["text"]

        label = Label(
            text=str(text),
            font_size=size,
            color=color,
            bold=bold,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(height)
        )

        label.bind(
            size=lambda obj, value:
            setattr(
                obj,
                "text_size",
                value
            )
        )

        return label


    # =====================================================
    # FORMAT TIME
    # =====================================================

    def format_time(self, seconds):

        seconds = int(seconds)

        hours = seconds // 3600

        minutes = (
            seconds % 3600
        ) // 60

        if hours > 0:

            return f"{hours}h {minutes}m"

        return f"{minutes}m"


    # =====================================================
    # PROFILE CONTENT
    # =====================================================

    def refresh_profile(self):

        self.content.clear_widgets()

        c = get_colors()


        # =================================================
        # HEADER
        # =================================================

        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(65)
        )

        header.add_widget(
            self.make_label(
                "Your Profile",
                23,
                c["text"],
                True,
                35
            )
        )

        header.add_widget(
            self.make_label(
                "Track your study progress",
                11,
                c["muted"],
                False,
                23
            )
        )

        self.content.add_widget(
            header
        )


        # =================================================
        # TODAY'S PROGRESS
        # =================================================

        today_seconds = (
            get_today_study_seconds()
        )

        try:

            daily_goal = int(
                get_setting(
                    "daily_goal",
                    "14400"
                )
            )

        except Exception:

            daily_goal = 14400

        if daily_goal <= 0:

            daily_goal = 1

        percentage = (
            today_seconds /
            daily_goal
        ) * 100

        percentage = min(
            100,
            percentage
        )


        today_card = ProfileCard()


        today_card.add_widget(
            self.make_label(
                "TODAY'S PROGRESS",
                10,
                c["accent"],
                True,
                22
            )
        )


        time_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48)
        )


        time_box = BoxLayout(
            orientation="vertical"
        )


        time_box.add_widget(
            self.make_label(
                self.format_time(
                    today_seconds
                ),
                25,
                c["text"],
                True,
                30
            )
        )


        time_box.add_widget(
            self.make_label(
                "Goal: " +
                self.format_time(
                    daily_goal
                ),
                9,
                c["muted"],
                False,
                18
            )
        )


        time_row.add_widget(
            time_box
        )


        time_row.add_widget(
            self.make_label(
                f"{int(percentage)}%",
                22,
                c["accent"],
                True,
                40
            )
        )


        today_card.add_widget(
            time_row
        )


        # -------------------------------------------------
        # TODAY PROGRESS BAR
        # -------------------------------------------------

        progress = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(9)
        )


        with progress.canvas.before:

            Color(
                c["card"][0],
                c["card"][1],
                c["card"][2],
                1
            )

            progress_bg = RoundedRectangle(
                pos=progress.pos,
                size=progress.size,
                radius=[dp(5)]
            )


        fill = BoxLayout(
            size_hint_x=max(
                0.01,
                percentage / 100
            )
        )


        with fill.canvas.before:

            Color(
                c["accent"][0],
                c["accent"][1],
                c["accent"][2],
                1
            )

            fill_bg = RoundedRectangle(
                pos=fill.pos,
                size=fill.size,
                radius=[dp(5)]
            )


        progress.add_widget(
            fill
        )


        progress.bind(
            pos=lambda obj, value:
            setattr(
                progress_bg,
                "pos",
                value
            ),
            size=lambda obj, value:
            setattr(
                progress_bg,
                "size",
                value
            )
        )


        fill.bind(
            pos=lambda obj, value:
            setattr(
                fill_bg,
                "pos",
                value
            ),
            size=lambda obj, value:
            setattr(
                fill_bg,
                "size",
                value
            )
        )


        today_card.add_widget(
            progress
        )


        # -------------------------------------------------
        # REMAINING
        # -------------------------------------------------

        if today_seconds >= daily_goal:

            message = "Daily goal completed"

        else:

            remaining = (
                daily_goal -
                today_seconds
            )

            message = (
                self.format_time(
                    remaining
                )
                +
                " remaining"
            )


        today_card.add_widget(
            self.make_label(
                message,
                9,
                c["muted"],
                False,
                20
            )
        )


        self.content.add_widget(
            today_card
        )


        # =================================================
        # STUDY STATISTICS
        # =================================================

        statistics = ProfileCard()


        statistics.add_widget(
            self.make_label(
                "STUDY STATISTICS",
                10,
                c["accent"],
                True,
                22
            )
        )


        stats_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(60)
        )


        stats_row.add_widget(
            self.stat_box(
                "STREAK",
                str(
                    get_streak()
                ) + " days"
            )
        )


        stats_row.add_widget(
            self.stat_box(
                "THIS WEEK",
                self.format_time(
                    get_week_study_seconds()
                )
            )
        )


        stats_row.add_widget(
            self.stat_box(
                "SESSIONS",
                str(
                    self.get_session_count()
                )
            )
        )


        statistics.add_widget(
            stats_row
        )


        self.content.add_widget(
            statistics
        )


        # =================================================
        # 7 DAY PROGRESS
        # =================================================

        week_card = ProfileCard()


        week_card.add_widget(
            self.make_label(
                "7-DAY PROGRESS",
                10,
                c["accent"],
                True,
                22
            )
        )


        days = self.get_last_7_days()


        maximum = max(
            [
                seconds
                for _, seconds in days
            ]
            + [1]
        )


        for day_name, seconds in days:

            row = BoxLayout(
                orientation="horizontal",
                spacing=dp(6),
                size_hint_y=None,
                height=dp(28)
            )


            # -------------------------------------------------
            # DAY NAME
            # -------------------------------------------------

            day_label = self.make_label(
                day_name,
                9,
                c["muted"],
                False,
                25
            )

            day_label.size_hint_x = None
            day_label.width = dp(28)

            row.add_widget(
                day_label
            )


            # -------------------------------------------------
            # CALCULATE RATIO
            # -------------------------------------------------

            ratio = (
                seconds /
                maximum
            )

            ratio = max(
                0,
                min(
                    1,
                    ratio
                )
            )


            # -------------------------------------------------
            # FIXED PROGRESS BAR
            # -------------------------------------------------

            bar_area = Widget(
                size_hint_x=1,
                size_hint_y=None,
                height=dp(8)
            )


            # Background

            with bar_area.canvas.before:

                Color(
                    c["card"][0],
                    c["card"][1],
                    c["card"][2],
                    1
                )

                bar_background = RoundedRectangle(
                    pos=bar_area.pos,
                    size=bar_area.size,
                    radius=[dp(4)]
                )


            # Fill

            with bar_area.canvas:

                Color(
                    c["accent"][0],
                    c["accent"][1],
                    c["accent"][2],
                    1
                )

                bar_fill = RoundedRectangle(
                    pos=bar_area.pos,
                    size=(
                        0,
                        bar_area.height
                    ),
                    radius=[dp(4)]
                )


            # -------------------------------------------------
            # IMPORTANT:
            # Capture ratio for THIS row.
            # This prevents every bar from using
            # the last day's ratio.
            # -------------------------------------------------

            def update_bar(
                instance,
                bg=bar_background,
                fill=bar_fill,
                value=ratio
            ):

                bg.pos = instance.pos

                bg.size = instance.size


                fill.pos = instance.pos

                fill.size = (
                    instance.width * value,
                    instance.height
                )


            bar_area.bind(
                pos=update_bar,
                size=update_bar
            )


            row.add_widget(
                bar_area
            )


            # -------------------------------------------------
            # TIME
            # -------------------------------------------------

            time_label = self.make_label(
                self.format_time(
                    seconds
                ),
                9,
                c["text"],
                False,
                25
            )

            time_label.size_hint_x = None
            time_label.width = dp(38)


            row.add_widget(
                time_label
            )


            week_card.add_widget(
                row
            )


        self.content.add_widget(
            week_card
        )


        # =================================================
        # SUBJECT PROGRESS
        # =================================================

        subject_card = ProfileCard()


        subject_card.add_widget(
            self.make_label(
                "SUBJECT PROGRESS",
                10,
                c["accent"],
                True,
                22
            )
        )


        subjects = get_subjects()


        if subjects:

            subject_data = []


            for subject in subjects:

                total = self.get_subject_time(
                    subject["id"]
                )


                subject_data.append(
                    (
                        subject["name"],
                        total
                    )
                )


            subject_data.sort(
                key=lambda item: item[1],
                reverse=True
            )


            for name, seconds in subject_data:

                row = BoxLayout(
                    orientation="horizontal",
                    size_hint_y=None,
                    height=dp(30)
                )


                row.add_widget(
                    self.make_label(
                        name,
                        10,
                        c["text"],
                        False,
                        28
                    )
                )


                row.add_widget(
                    self.make_label(
                        self.format_time(
                            seconds
                        ),
                        10,
                        c["muted"],
                        False,
                        28
                    )
                )


                subject_card.add_widget(
                    row
                )


        else:

            subject_card.add_widget(
                self.make_label(
                    "No subjects yet",
                    10,
                    c["muted"],
                    False,
                    25
                )
            )


        self.content.add_widget(
            subject_card
        )


        # =================================================
        # TASK PROGRESS
        # =================================================

        task_card = ProfileCard()


        task_card.add_widget(
            self.make_label(
                "TASK PROGRESS",
                10,
                c["accent"],
                True,
                22
            )
        )


        tasks = get_tasks()


        total_tasks = len(tasks)


        completed_tasks = sum(
            1
            for task in tasks
            if bool(
                task["completed"]
            )
        )


        pending_tasks = (
            total_tasks -
            completed_tasks
        )


        task_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(55)
        )


        task_row.add_widget(
            self.stat_box(
                "TOTAL",
                str(total_tasks)
            )
        )


        task_row.add_widget(
            self.stat_box(
                "COMPLETED",
                str(completed_tasks)
            )
        )


        task_row.add_widget(
            self.stat_box(
                "PENDING",
                str(pending_tasks)
            )
        )


        task_card.add_widget(
            task_row
        )


        self.content.add_widget(
            task_card
        )


        # -------------------------------------------------
        # BOTTOM PADDING
        # -------------------------------------------------

        self.content.add_widget(
            BoxLayout(
                size_hint_y=None,
                height=dp(12)
            )
        )


    # =====================================================
    # STAT BOX
    # =====================================================

    def stat_box(
        self,
        title,
        value
    ):

        c = get_colors()


        box = BoxLayout(
            orientation="vertical"
        )


        box.add_widget(
            self.make_label(
                title,
                8,
                c["muted"],
                True,
                18
            )
        )


        box.add_widget(
            self.make_label(
                value,
                14,
                c["text"],
                True,
                25
            )
        )


        return box


    # =====================================================
    # SUBJECT STUDY TIME
    # =====================================================

    def get_subject_time(
        self,
        subject_id
    ):

        sessions = get_recent_sessions(
            1000
        )


        total = 0


        for session in sessions:

            try:

                if session["subject_id"] == subject_id:

                    total += int(
                        session[
                            "duration_seconds"
                        ]
                    )

            except Exception:

                pass


        return total


    # =====================================================
    # LAST 7 DAYS
    # =====================================================

    def get_last_7_days(self):

        from datetime import (
            datetime,
            date,
            timedelta
        )


        sessions = get_recent_sessions(
            1000
        )


        today = date.today()


        result = []


        for i in range(
            6,
            -1,
            -1
        ):

            current_date = (
                today -
                timedelta(days=i)
            )


            total = 0


            for session in sessions:

                try:

                    started = datetime.fromisoformat(
                        session["started_at"]
                    )


                    if started.date() == current_date:

                        total += int(
                            session[
                                "duration_seconds"
                            ]
                        )

                except Exception:

                    pass


            result.append(
                (
                    current_date.strftime(
                        "%a"
                    ),
                    total
                )
            )


        return result


    # =====================================================
    # SESSION COUNT
    # =====================================================

    def get_session_count(self):

        sessions = get_recent_sessions(
            1000
        )

        return len(sessions)


# =========================================================
# COMPATIBILITY
# =========================================================

ProfileScreen = ProfilePage