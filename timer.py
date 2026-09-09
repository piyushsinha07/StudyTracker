from time import monotonic
from datetime import datetime

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle

from database import (
    get_subjects,
    save_session,
    get_today_study_seconds
)

from navigation import Navigation

from ui_style import (
    StyledCard, PrimaryButton, SecondaryButton, DangerButton,
    section_label, title_label, subtitle_label, styled_input
)
from theme import get_colors


# =========================================================
# SUBJECT DROPDOWN OPTION
# =========================================================

class SubjectSpinnerOption(SpinnerOption):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Remove Kivy default background
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)

        # Text
        self.color = get_colors()["text"]
        self.font_size = "12sp"

        # Size
        self.size_hint_y = None
        self.height = dp(46)

        self.padding = [
            dp(14),
            dp(8)
        ]

        # -------------------------------------------------
        # OPTION BACKGROUND
        # -------------------------------------------------

        with self.canvas.before:

            c = get_colors()
            Color(
                c["card2"][0],
                c["card2"][1],
                c["card2"][2],
                1
            )

            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(10)]
            )

        # -------------------------------------------------
        # SEPARATOR LINE
        # -------------------------------------------------

        with self.canvas.after:

            Color(
                c["accent"][0],
                c["accent"][1],
                c["accent"][2],
                0.45
            )

            self.separator = RoundedRectangle(
                pos=(
                    self.x + dp(10),
                    self.y
                ),
                size=(
                    self.width - dp(20),
                    dp(1)
                ),
                radius=[dp(1)]
            )

        self.bind(
            pos=self.update_background,
            size=self.update_background
        )

    def update_background(self, *_):

        self.bg.pos = self.pos
        self.bg.size = self.size

        self.separator.pos = (
            self.x + dp(10),
            self.y
        )

        self.separator.size = (
            self.width - dp(20),
            dp(1)
        )


# =========================================================
# TIMER PAGE
# =========================================================

class TimerPage(BoxLayout):

    def __init__(self, **kwargs):

        super().__init__(
            orientation="vertical",
            spacing=dp(7),
            padding=[
                dp(18),
                dp(10),
                dp(18),
                dp(8)
            ],
            **kwargs
        )

        self.navigate = lambda name: None

        # -------------------------------------------------
        # TIMER STATE
        # -------------------------------------------------

        self.running = False
        self.paused = False

        # Actual elapsed study time
        self.elapsed = 0.0

        self.last_tick = 0.0

        self.start_time = None

        # Default duration = 25 minutes
        self.selected_minutes = 25

        self.build()


    # =====================================================
    # BUILD UI
    # =====================================================

    def build(self):

        self.clear_widgets()

        # -------------------------------------------------
        # TOP BAR
        # -------------------------------------------------

        self.add_widget(
            Navigation.top_bar(
                self,
                "Study Timer"
            )
        )

        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(58)
        )

        header.add_widget(
            title_label(
                "Study Timer",
                23
            )
        )

        header.add_widget(
            subtitle_label(
                "Focus on one task at a time"
            )
        )

        self.add_widget(header)

        # -------------------------------------------------
        # TIMER CARD
        # -------------------------------------------------

        timer_card = StyledCard(
            orientation="vertical",
            padding=[
                dp(15),
                dp(9)
            ],
            spacing=dp(2),
            size_hint_y=None,

            # Extra space for percentage
            height=dp(198)
        )

        # -------------------------------------------------
        # FOCUS SESSION
        # -------------------------------------------------

        timer_card.add_widget(
            Label(
                text="FOCUS SESSION",
                color=get_colors()["accent"],
                font_size="9sp",
                bold=True,
                size_hint_y=None,
                height=dp(20)
            )
        )

        # -------------------------------------------------
        # TIMER DISPLAY
        # -------------------------------------------------

        self.time_label = Label(
            text="25:00",
            font_size="43sp",
            bold=True,
            color=get_colors()["text"],
            size_hint_y=None,
            height=dp(62)
        )

        timer_card.add_widget(
            self.time_label
        )

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        self.status_label = Label(
            text="Ready to focus",
            color=get_colors()["muted"],
            font_size="10sp",
            size_hint_y=None,
            height=dp(21)
        )

        timer_card.add_widget(
            self.status_label
        )

        # -------------------------------------------------
        # PERCENTAGE
        # -------------------------------------------------

        self.percent_label = Label(
            text="0% COMPLETE",
            color=get_colors()["accent"],
            font_size="9sp",
            bold=True,
            size_hint_y=None,
            height=dp(20)
        )

        timer_card.add_widget(
            self.percent_label
        )

        # -------------------------------------------------
        # PROGRESS BAR
        # -------------------------------------------------

        self.progress = Widget(
            size_hint_y=None,
            height=dp(8)
        )

        with self.progress.canvas:

            # Background
            c = get_colors()
            Color(
                c["card2"][0],
                c["card2"][1],
                c["card2"][2],
                1
            )

            self.progress_bg = RoundedRectangle(
                pos=self.progress.pos,
                size=self.progress.size,
                radius=[dp(4)]
            )

            # Filled section
            Color(
                *get_colors()["accent"]
            )

            self.progress_fill = RoundedRectangle(
                pos=self.progress.pos,
                size=(
                    0,
                    dp(7)
                ),
                radius=[dp(4)]
            )

        self.progress.bind(
            pos=self.update_progress,
            size=self.update_progress
        )

        timer_card.add_widget(
            self.progress
        )

        self.add_widget(
            timer_card
        )

        # -------------------------------------------------
        # SESSION LENGTH
        # -------------------------------------------------

        self.add_widget(
            section_label(
                "SESSION LENGTH"
            )
        )

        duration = BoxLayout(
            spacing=dp(4),
            size_hint_y=None,
            height=dp(38)
        )

        durations = [
            5,
            10,
            15,
            25,
            30,
            45,
            60
        ]

        for minutes in durations:

            button = SecondaryButton(
                text=str(minutes),
                font_size="9sp"
            )

            button.bind(
                on_release=lambda _, m=minutes:
                self.set_duration(m)
            )

            duration.add_widget(
                button
            )

        # -------------------------------------------------
        # CUSTOM BUTTON
        # -------------------------------------------------

        custom = SecondaryButton(
            text="CUSTOM",
            font_size="8sp"
        )

        custom.bind(
            on_release=lambda *_:
            self.custom_duration()
        )

        duration.add_widget(
            custom
        )

        self.add_widget(
            duration
        )

        # -------------------------------------------------
        # SUBJECT
        # -------------------------------------------------

        self.add_widget(
            section_label(
                "SUBJECT"
            )
        )

        subjects = get_subjects()

        # Only names are displayed
        values = [
            subject["name"]
            for subject in subjects
        ]

        # -------------------------------------------------
        # SUBJECT SPINNER
        # -------------------------------------------------

        self.subject_spinner = Spinner(

            text=(
                values[0]
                if values
                else "No subject"
            ),

            values=values,

            option_cls=SubjectSpinnerOption,

            size_hint_y=None,

            height=dp(46),

            background_normal="",

            background_down="",

            background_color=(
                0,
                0,
                0,
                0
            ),

            color=get_colors()["text"],

            font_size="11sp",

            padding=[
                dp(14),
                dp(8)
            ]
        )

        # -------------------------------------------------
        # MAIN SPINNER BACKGROUND
        # -------------------------------------------------

        with self.subject_spinner.canvas.before:

            c = get_colors()
            Color(
                c["card2"][0],
                c["card2"][1],
                c["card2"][2],
                1
            )

            self.subject_spinner_bg = RoundedRectangle(
                pos=self.subject_spinner.pos,
                size=self.subject_spinner.size,
                radius=[
                    dp(12)
                ]
            )

        self.subject_spinner.bind(
            pos=lambda *_:
            self.update_spinner_background(),

            size=lambda *_:
            self.update_spinner_background()
        )

        self.add_widget(
            self.subject_spinner
        )

        # -------------------------------------------------
        # CONTROL BUTTONS
        # -------------------------------------------------

        controls = BoxLayout(
            spacing=dp(5),
            size_hint_y=None,
            height=dp(43)
        )

        self.start_btn = PrimaryButton(
            text="START",
            font_size="9sp"
        )

        self.pause_btn = SecondaryButton(
            text="PAUSE",
            font_size="9sp"
        )

        self.stop_btn = DangerButton(
            text="STOP",
            font_size="9sp"
        )

        self.reset_btn = SecondaryButton(
            text="RESET",
            font_size="9sp"
        )

        self.start_btn.bind(
            on_release=lambda *_:
            self.start()
        )

        self.pause_btn.bind(
            on_release=lambda *_:
            self.pause_resume()
        )

        self.stop_btn.bind(
            on_release=lambda *_:
            self.stop()
        )

        self.reset_btn.bind(
            on_release=lambda *_:
            self.reset()
        )

        controls.add_widget(
            self.start_btn
        )

        controls.add_widget(
            self.pause_btn
        )

        controls.add_widget(
            self.stop_btn
        )

        controls.add_widget(
            self.reset_btn
        )

        self.add_widget(
            controls
        )

        # -------------------------------------------------
        # TODAY'S STUDY
        # -------------------------------------------------

        self.today_card = StyledCard(
            orientation="vertical",
            padding=[
                dp(10),
                dp(5)
            ],
            size_hint_y=None,
            height=dp(55)
        )

        self.today_card.add_widget(
            Label(
                text="TODAY'S STUDY",
                color=get_colors()["accent"],
                font_size="8sp",
                bold=True
            )
        )

        self.today_label = Label(
            text=self.format_total(
                get_today_study_seconds()
            ),
            color=get_colors()["text"],
            font_size="16sp",
            bold=True
        )

        self.today_card.add_widget(
            self.today_label
        )

        self.add_widget(
            self.today_card
        )

        # Empty space
        self.add_widget(
            Widget()
        )

        # -------------------------------------------------
        # BOTTOM NAVIGATION
        # -------------------------------------------------

        self.add_widget(
            Navigation.bottom_nav(
                self
            )
        )

        self.refresh()


    # =====================================================
    # SPINNER BACKGROUND
    # =====================================================

    def update_spinner_background(self):

        self.subject_spinner_bg.pos = (
            self.subject_spinner.pos
        )

        self.subject_spinner_bg.size = (
            self.subject_spinner.size
        )


    # =====================================================
    # GET SUBJECT
    # =====================================================

    def get_subject_name(self):

        name = (
            self.subject_spinner.text
            .strip()
        )

        if not name:
            return None

        if name == "No subject":
            return None

        return name


    # =====================================================
    # REFRESH
    # =====================================================

    def refresh(self):

        if not self.running:

            subjects = get_subjects()

            values = [
                subject["name"]
                for subject in subjects
            ]

            current = ""

            if hasattr(
                self,
                "subject_spinner"
            ):

                current = (
                    self.subject_spinner.text
                )

            self.subject_spinner.values = values

            if current in values:

                self.subject_spinner.text = current

            elif values:

                self.subject_spinner.text = values[0]

            else:

                self.subject_spinner.text = "No subject"

        if hasattr(
            self,
            "today_label"
        ):

            self.today_label.text = (
                self.format_total(
                    get_today_study_seconds()
                )
            )


    # =====================================================
    # SET DURATION
    # =====================================================

    def set_duration(
        self,
        minutes
    ):

        if self.running:
            return

        self.selected_minutes = int(
            minutes
        )

        self.elapsed = 0

        self.update_timer_display()

        self.status_label.text = (
            f"Selected "
            f"{self.selected_minutes} minutes"
        )

        self.update_progress()


    # =====================================================
    # UPDATE TIMER DISPLAY
    # =====================================================

    def update_timer_display(self):

        total_seconds = (
            self.selected_minutes
            * 60
        )

        remaining = max(
            0,
            int(
                total_seconds
                - self.elapsed
            )
        )

        hours = remaining // 3600

        minutes = (
            remaining % 3600
        ) // 60

        seconds = remaining % 60

        # -------------------------------------------------
        # COUNTDOWN
        # -------------------------------------------------

        if hours > 0:

            self.time_label.text = (
                f"{hours:02d}:"
                f"{minutes:02d}:"
                f"{seconds:02d}"
            )

        else:

            self.time_label.text = (
                f"{minutes:02d}:"
                f"{seconds:02d}"
            )

        # -------------------------------------------------
        # PERCENTAGE
        # -------------------------------------------------

        if total_seconds > 0:

            percentage = int(
                (
                    self.elapsed
                    / total_seconds
                )
                * 100
            )

        else:

            percentage = 0

        percentage = max(
            0,
            min(
                100,
                percentage
            )
        )

        self.percent_label.text = (
            f"{percentage}% COMPLETE"
        )


    # =====================================================
    # CUSTOM DURATION
    # =====================================================

    def custom_duration(self):

        box = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10)
        )

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        box.add_widget(
            section_label(
                "CUSTOM SESSION"
            )
        )

        # -------------------------------------------------
        # HOURS + MINUTES
        # -------------------------------------------------

        time_row = BoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(44)
        )

        hours_field = styled_input(
            "Hours"
        )

        minutes_field = styled_input(
            "Minutes"
        )

        time_row.add_widget(
            hours_field
        )

        time_row.add_widget(
            minutes_field
        )

        box.add_widget(
            time_row
        )

        # -------------------------------------------------
        # EXAMPLE
        # -------------------------------------------------

        example = Label(
            text="Example: 1 hour 30 minutes",
            color=get_colors()["muted"],
            font_size="9sp",
            size_hint_y=None,
            height=dp(22)
        )

        box.add_widget(
            example
        )

        # -------------------------------------------------
        # BUTTONS
        # -------------------------------------------------

        actions = BoxLayout(
            spacing=dp(8),
            size_hint_y=None,
            height=dp(44)
        )

        cancel = SecondaryButton(
            text="CANCEL"
        )

        use = PrimaryButton(
            text="USE"
        )

        actions.add_widget(
            cancel
        )

        actions.add_widget(
            use
        )

        box.add_widget(
            actions
        )

        # -------------------------------------------------
        # POPUP
        # -------------------------------------------------

        popup = Popup(
            title="Custom Duration",
            content=box,
            size_hint=(
                0.86,
                None
            ),
            height=dp(275),
            separator_color=get_colors()["accent"]
        )

        cancel.bind(
            on_release=popup.dismiss
        )

        # -------------------------------------------------
        # APPLY
        # -------------------------------------------------

        def apply(*_):

            try:

                hours = int(
                    hours_field.text
                    or 0
                )

                minutes = int(
                    minutes_field.text
                    or 0
                )

            except (
                ValueError,
                TypeError
            ):

                return

            # Convert everything to minutes

            total_minutes = (
                hours * 60
                + minutes
            )

            # Don't allow zero

            if total_minutes <= 0:

                return

            self.set_duration(
                total_minutes
            )

            popup.dismiss()

        use.bind(
            on_release=apply
        )

        popup.open()


    # =====================================================
    # START
    # =====================================================

    def start(self):

        if self.running:
            return

        subject = (
            self.get_subject_name()
        )

        if subject is None:

            self.status_label.text = (
                "Please select a subject"
            )

            return

        self.running = True

        self.paused = False

        self.last_tick = monotonic()

        if self.start_time is None:

            self.start_time = (
                datetime.now()
            )

        self.status_label.text = (
            "Studying..."
        )

        self.start_btn.text = (
            "RUNNING"
        )

        Clock.unschedule(
            self.tick
        )

        Clock.schedule_interval(
            self.tick,
            0.2
        )


    # =====================================================
    # TIMER TICK
    # =====================================================

    def tick(
        self,
        dt
    ):

        if (
            not self.running
            or self.paused
        ):

            return

        now = monotonic()

        self.elapsed += (
            now
            - self.last_tick
        )

        self.last_tick = now

        total_duration = (
            self.selected_minutes
            * 60
        )

        # -------------------------------------------------
        # AUTOMATIC COMPLETION
        # -------------------------------------------------

        if self.elapsed >= total_duration:

            self.elapsed = float(
                total_duration
            )

            self.update_timer_display()

            self.update_progress()

            self.finish_session()

            return

        # Update countdown
        self.update_timer_display()

        # Update progress
        self.update_progress()


    # =====================================================
    # PROGRESS BAR
    # =====================================================

    def update_progress(
        self,
        *_args
    ):

        if not hasattr(
            self,
            "progress"
        ):

            return

        total = max(
            1,
            self.selected_minutes
            * 60
        )

        ratio = min(
            1,
            self.elapsed
            / total
        )

        # -------------------------------------------------
        # BACKGROUND
        # -------------------------------------------------

        self.progress_bg.pos = (
            self.progress.pos
        )

        self.progress_bg.size = (
            self.progress.size
        )

        # -------------------------------------------------
        # FILL
        # -------------------------------------------------

        self.progress_fill.pos = (
            self.progress.pos
        )

        self.progress_fill.size = (
            self.progress.width
            * ratio,
            dp(7)
        )


    # =====================================================
    # PAUSE / RESUME
    # =====================================================

    def pause_resume(self):

        if not self.running:
            return

        if self.paused:

            self.paused = False

            self.last_tick = monotonic()

            self.status_label.text = (
                "Studying..."
            )

            self.pause_btn.text = (
                "PAUSE"
            )

        else:

            self.paused = True

            self.status_label.text = (
                "Paused"
            )

            self.pause_btn.text = (
                "RESUME"
            )


    # =====================================================
    # SAVE SESSION
    # =====================================================

    def save_session_now(self):

        duration = int(
            self.elapsed
        )

        if (
            duration <= 0
            or self.start_time is None
        ):

            return duration

        subject_name = (
            self.get_subject_name()
        )

        if subject_name is not None:

            save_session(
                subject_name,
                duration,
                self.start_time.isoformat(
                    timespec="seconds"
                ),
                datetime.now().isoformat(
                    timespec="seconds"
                )
            )

        return duration


    # =====================================================
    # FINISH SESSION
    # =====================================================

    def finish_session(self):

        Clock.unschedule(
            self.tick
        )

        duration = (
            self.save_session_now()
        )

        self.running = False

        self.paused = False

        self.start_btn.text = (
            "START"
        )

        self.pause_btn.text = (
            "PAUSE"
        )

        self.start_time = None

        self.status_label.text = (
            f"Session complete • "
            f"{duration // 60} min saved"
        )

        self.today_label.text = (
            self.format_total(
                get_today_study_seconds()
            )
        )

        # Make sure final display is correct
        self.update_timer_display()

        self.update_progress()


    # =====================================================
    # STOP
    # =====================================================

    def stop(self):

        if not self.running:
            return

        Clock.unschedule(
            self.tick
        )

        duration = (
            self.save_session_now()
        )

        self.running = False

        self.paused = False

        self.status_label.text = (
            f"Saved {duration} seconds"
        )

        self.start_btn.text = (
            "START"
        )

        self.pause_btn.text = (
            "PAUSE"
        )

        self.start_time = None

        self.today_label.text = (
            self.format_total(
                get_today_study_seconds()
            )
        )


    # =====================================================
    # RESET
    # =====================================================

    def reset(self):

        Clock.unschedule(
            self.tick
        )

        self.running = False

        self.paused = False

        self.elapsed = 0

        self.start_time = None

        # Reset timer display
        self.update_timer_display()

        # Reset percentage
        self.percent_label.text = (
            "0% COMPLETE"
        )

        # Reset status
        self.status_label.text = (
            "Ready to focus"
        )

        self.start_btn.text = (
            "START"
        )

        self.pause_btn.text = (
            "PAUSE"
        )

        self.update_progress()


    # =====================================================
    # FORMAT TOTAL STUDY TIME
    # =====================================================

    @staticmethod
    def format_total(
        seconds
    ):

        seconds = int(
            seconds or 0
        )

        hours = (
            seconds
            // 3600
        )

        minutes = (
            seconds
            % 3600
        ) // 60

        if hours:

            return (
                f"{hours}h "
                f"{minutes:02d}m"
            )

        return f"{minutes}m"


# =========================================================
# COMPATIBILITY
# =========================================================

StudyTimerScreen = TimerPage