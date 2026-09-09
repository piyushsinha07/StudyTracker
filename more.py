from kivy.metrics import dp

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView

from kivy.graphics import Color, RoundedRectangle, Line

from kivy.app import App

from database import (
    get_setting,
    set_setting,
    get_water_goal,
    set_water_goal
)

from theme import get_colors


# =========================================================
# SETTING CARD
# =========================================================

class SettingCard(BoxLayout):

    def __init__(
        self,
        title,
        value,
        callback,
        **kwargs
    ):

        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(64),
            padding=[
                dp(12),
                dp(7)
            ],
            spacing=dp(5),
            **kwargs
        )


        self.callback = callback

        c = get_colors()


        # -------------------------------------------------
        # BACKGROUND
        # -------------------------------------------------

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


        # -------------------------------------------------
        # BORDER
        # -------------------------------------------------

        with self.canvas.after:

            Color(
                c["accent"][0],
                c["accent"][1],
                c["accent"][2],
                0.30
            )

            self.border = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    dp(14)
                ),
                width=1
            )


        self.bind(
            pos=self.update_graphics,
            size=self.update_graphics
        )


        # -------------------------------------------------
        # TEXT
        # -------------------------------------------------

        text_box = BoxLayout(
            orientation="vertical",
            spacing=dp(1)
        )


        title_label = Label(
            text=title,
            font_size=12,
            bold=True,
            color=c["text"],
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(27)
        )


        title_label.bind(
            size=lambda obj, value:
            setattr(
                obj,
                "text_size",
                value
            )
        )


        value_label = Label(
            text=value,
            font_size=9,
            color=c["muted"],
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(20)
        )


        value_label.bind(
            size=lambda obj, value:
            setattr(
                obj,
                "text_size",
                value
            )
        )


        text_box.add_widget(
            title_label
        )


        text_box.add_widget(
            value_label
        )


        self.add_widget(
            text_box
        )


        # -------------------------------------------------
        # SPACE
        # -------------------------------------------------

        self.add_widget(
            BoxLayout(
                size_hint_x=1
            )
        )


        # -------------------------------------------------
        # ARROW
        # -------------------------------------------------

        arrow = Label(
            text=">",
            font_size=17,
            bold=True,
            color=c["accent"],
            size_hint_x=None,
            width=dp(25)
        )


        self.add_widget(
            arrow
        )


    def update_graphics(self, *args):

        self.bg.pos = self.pos

        self.bg.size = self.size

        self.border.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(14)
        )


    def on_touch_down(self, touch):

        if self.collide_point(
            *touch.pos
        ):

            if self.callback:

                self.callback()

            return True


        return super().on_touch_down(
            touch
        )


# =========================================================
# MORE PAGE
# =========================================================

class MorePage(BoxLayout):

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

        self.build()


    # =====================================================
    # BUILD
    # =====================================================

    def build(self):

        self.clear_widgets()

        c = get_colors()


        # =================================================
        # HEADER
        # =================================================

        header = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(67)
        )


        title = Label(
            text="More & Settings",
            font_size=23,
            bold=True,
            color=c["text"],
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(38)
        )


        title.bind(
            size=lambda obj, value:
            setattr(
                obj,
                "text_size",
                value
            )
        )


        header.add_widget(
            title
        )


        subtitle = Label(
            text="Manage your goals and app preferences",
            font_size=10,
            color=c["muted"],
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(23)
        )


        subtitle.bind(
            size=lambda obj, value:
            setattr(
                obj,
                "text_size",
                value
            )
        )


        header.add_widget(
            subtitle
        )


        self.add_widget(
            header
        )


        # =================================================
        # SCROLL
        # =================================================

        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(3)
        )


        self.content = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=[
                0,
                dp(3),
                0,
                dp(12)
            ],
            size_hint_y=None
        )


        self.content.bind(
            minimum_height=
            self.content.setter(
                "height"
            )
        )


        scroll.add_widget(
            self.content
        )


        self.add_widget(
            scroll
        )


        # =================================================
        # PROFILE
        # =================================================

        self.add_section(
            "PROFILE"
        )


        self.add_card(
            "Profile",
            "View your daily study progress",
            self.open_profile
        )


        # =================================================
        # GOALS
        # =================================================

        self.add_section(
            "GOALS"
        )


        self.add_card(
            "Study Goal",
            self.get_goal_text(),
            self.study_goal_popup
        )


        self.add_card(
            "Water Goal",
            f"{get_water_goal()} glasses per day",
            self.water_goal_popup
        )


        # =================================================
        # APPEARANCE
        # =================================================

        self.add_section(
            "APPEARANCE"
        )


        appearance = get_setting(
            "appearance",
            "DARK"
        )


        self.add_card(
            "Appearance",
            appearance.title(),
            self.toggle_appearance
        )


        theme = get_setting(
            "theme",
            "OCEAN"
        )


        self.add_card(
            "Theme",
            theme.title(),
            self.change_theme
        )


        eye = get_setting(
            "eye_comfort",
            "OFF"
        )


        self.add_card(
            "Eye Comfort",
            eye,
            self.toggle_eye
        )


        # =================================================
        # REMINDERS
        # =================================================

        self.add_section(
            "REMINDERS"
        )


        reminder = get_setting(
            "water_reminder",
            "OFF"
        )


        self.add_card(
            "Water Reminder",
            reminder,
            self.toggle_reminder
        )


        self.content.add_widget(
            BoxLayout(
                size_hint_y=None,
                height=dp(10)
            )
        )


        # =================================================
        # BACK HOME
        # =================================================

        back = Button(
            text="Back to Home",
            font_size=14,
            bold=True,
            background_normal="",
            background_color=c["accent"],
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(45)
        )


        back.bind(
            on_release=lambda *_:
            self.navigate("home")
        )


        self.add_widget(
            back
        )


    # =====================================================
    # SECTION
    # =====================================================

    def add_section(self, text):

        c = get_colors()


        label = Label(
            text=text,
            font_size=9,
            bold=True,
            color=c["accent"],
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(21)
        )


        label.bind(
            size=lambda obj, value:
            setattr(
                obj,
                "text_size",
                value
            )
        )


        self.content.add_widget(
            label
        )


    # =====================================================
    # CARD
    # =====================================================

    def add_card(
        self,
        title,
        value,
        callback
    ):

        self.content.add_widget(
            SettingCard(
                title=title,
                value=value,
                callback=callback
            )
        )


    # =====================================================
    # PROFILE
    # =====================================================

    def open_profile(self):

        self.navigate(
            "profile"
        )


    # =====================================================
    # STUDY GOAL TEXT
    # =====================================================

    def get_goal_text(self):

        try:

            seconds = int(
                get_setting(
                    "daily_goal",
                    "14400"
                )
            )

        except Exception:

            seconds = 14400


        hours = seconds // 3600

        minutes = (
            seconds % 3600
        ) // 60


        return (
            f"{hours} hr "
            f"{minutes:02d} min per day"
        )


    # =====================================================
    # STUDY GOAL POPUP
    # =====================================================

    def study_goal_popup(self):

        c = get_colors()


        try:

            current_seconds = int(
                get_setting(
                    "daily_goal",
                    "14400"
                )
            )

        except Exception:

            current_seconds = 14400


        current_hours = (
            current_seconds // 3600
        )


        current_minutes = (
            current_seconds % 3600
        ) // 60


        box = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(9)
        )


        description = Label(
            text=(
                "Set your daily study target.\n"
                "Choose hours and minutes."
            ),
            font_size=10,
            color=c["muted"],
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(40)
        )


        description.bind(
            size=lambda obj, value:
            setattr(
                obj,
                "text_size",
                value
            )
        )


        box.add_widget(
            description
        )


        # -------------------------------------------------
        # INPUTS
        # -------------------------------------------------

        row = BoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(68)
        )


        hours_box = BoxLayout(
            orientation="vertical",
            spacing=dp(3)
        )


        hours_box.add_widget(
            Label(
                text="Hours",
                font_size=9,
                color=c["muted"],
                size_hint_y=None,
                height=dp(18)
            )
        )


        hours_input = TextInput(
            text=str(current_hours),
            hint_text="0",
            input_filter="int",
            multiline=False,
            font_size=16,
            background_normal="",
            background_color=c["card2"],
            foreground_color=c["text"],
            cursor_color=c["accent"],
            padding=[
                dp(10),
                dp(10)
            ]
        )


        hours_box.add_widget(
            hours_input
        )


        minutes_box = BoxLayout(
            orientation="vertical",
            spacing=dp(3)
        )


        minutes_box.add_widget(
            Label(
                text="Minutes",
                font_size=9,
                color=c["muted"],
                size_hint_y=None,
                height=dp(18)
            )
        )


        minutes_input = TextInput(
            text=str(current_minutes),
            hint_text="0",
            input_filter="int",
            multiline=False,
            font_size=16,
            background_normal="",
            background_color=c["card2"],
            foreground_color=c["text"],
            cursor_color=c["accent"],
            padding=[
                dp(10),
                dp(10)
            ]
        )


        minutes_box.add_widget(
            minutes_input
        )


        row.add_widget(
            hours_box
        )


        row.add_widget(
            minutes_box
        )


        box.add_widget(
            row
        )


        box.add_widget(
            Label(
                text="Example: 2 hours 30 minutes",
                font_size=9,
                color=c["muted"],
                size_hint_y=None,
                height=dp(22)
            )
        )


        # -------------------------------------------------
        # BUTTONS
        # -------------------------------------------------

        buttons = BoxLayout(
            spacing=dp(8),
            size_hint_y=None,
            height=dp(46)
        )


        cancel = Button(
            text="Cancel",
            font_size=13,
            background_normal="",
            background_color=c["card"],
            color=c["text"]
        )


        save = Button(
            text="Save Goal",
            font_size=13,
            bold=True,
            background_normal="",
            background_color=c["accent"],
            color=(1, 1, 1, 1)
        )


        buttons.add_widget(
            cancel
        )


        buttons.add_widget(
            save
        )


        box.add_widget(
            buttons
        )


        popup = Popup(
            title="Daily Study Goal",
            content=box,
            size_hint=(
                0.88,
                None
            ),
            height=dp(305),
            separator_color=c["accent"],
            auto_dismiss=False
        )


        cancel.bind(
            on_release=popup.dismiss
        )


        def save_goal(*args):

            try:

                hours = int(
                    hours_input.text
                    or "0"
                )


                minutes = int(
                    minutes_input.text
                    or "0"
                )


                if hours < 0:
                    return


                if minutes < 0:
                    return


                hours += minutes // 60

                minutes = minutes % 60


                total_seconds = (
                    hours * 3600
                    +
                    minutes * 60
                )


                if total_seconds <= 0:

                    return


                set_setting(
                    "daily_goal",
                    str(total_seconds)
                )


                popup.dismiss()


                # Refresh entire app

                app = App.get_running_app()

                app.refresh_theme()


            except ValueError:

                return


        save.bind(
            on_release=save_goal
        )


        popup.open()

        hours_input.focus = True


    # =====================================================
    # WATER GOAL
    # =====================================================

    def water_goal_popup(self):

        c = get_colors()


        box = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10)
        )


        box.add_widget(
            Label(
                text="Set your daily water target.",
                font_size=10,
                color=c["muted"],
                size_hint_y=None,
                height=dp(28)
            )
        )


        input_box = TextInput(
            text=str(
                get_water_goal()
            ),
            hint_text="Glasses",
            input_filter="int",
            multiline=False,
            font_size=16,
            background_normal="",
            background_color=c["card2"],
            foreground_color=c["text"],
            cursor_color=c["accent"],
            size_hint_y=None,
            height=dp(45)
        )


        box.add_widget(
            input_box
        )


        buttons = BoxLayout(
            spacing=dp(8),
            size_hint_y=None,
            height=dp(45)
        )


        cancel = Button(
            text="Cancel",
            background_normal="",
            background_color=c["card"],
            color=c["text"]
        )


        save = Button(
            text="Save",
            background_normal="",
            background_color=c["accent"],
            color=(1, 1, 1, 1)
        )


        buttons.add_widget(
            cancel
        )


        buttons.add_widget(
            save
        )


        box.add_widget(
            buttons
        )


        popup = Popup(
            title="Water Goal",
            content=box,
            size_hint=(
                0.86,
                None
            ),
            height=dp(235),
            separator_color=c["accent"]
        )


        cancel.bind(
            on_release=popup.dismiss
        )


        def save_water(*args):

            try:

                value = int(
                    input_box.text
                )


                if value <= 0:
                    return


                set_water_goal(
                    value
                )


                popup.dismiss()


                self.build()


            except ValueError:

                return


        save.bind(
            on_release=save_water
        )


        popup.open()


    # =====================================================
    # APPEARANCE
    # =====================================================

    def toggle_appearance(self):

        current = get_setting(
            "appearance",
            "DARK"
        )


        if current == "DARK":

            new_value = "LIGHT"

        else:

            new_value = "DARK"


        set_setting(
            "appearance",
            new_value
        )


        app = App.get_running_app()

        app.refresh_theme()


    # =====================================================
    # THEME
    # =====================================================

    def change_theme(self):

        themes = [
            "OCEAN",
            "FOREST",
            "SUNSET",
            "LAVENDER",
            "SAKURA",
            "COFFEE",
            "MIDNIGHT",
            "MINIMAL"
        ]


        current = get_setting(
            "theme",
            "OCEAN"
        )


        try:

            index = themes.index(
                current
            )

        except ValueError:

            index = 0


        next_theme = themes[
            (index + 1)
            %
            len(themes)
        ]


        set_setting(
            "theme",
            next_theme
        )


        app = App.get_running_app()

        app.refresh_theme()


    # =====================================================
    # EYE COMFORT
    # =====================================================

    def toggle_eye(self):

        current = get_setting(
            "eye_comfort",
            "OFF"
        )


        if current == "ON":

            value = "OFF"

        else:

            value = "ON"


        set_setting(
            "eye_comfort",
            value
        )


        self.build()


    # =====================================================
    # WATER REMINDER
    # =====================================================

    def toggle_reminder(self):

        current = get_setting(
            "water_reminder",
            "OFF"
        )


        if current == "ON":

            value = "OFF"

        else:

            value = "ON"


        set_setting(
            "water_reminder",
            value
        )


        self.build()


# =========================================================
# COMPATIBILITY
# =========================================================

MoreScreen = MorePage