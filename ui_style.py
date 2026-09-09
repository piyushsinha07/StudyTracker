from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from theme import get_colors


# =========================================================
# CURRENT THEME COLORS
# =========================================================

def _colors():
    return get_colors()


# These names are refreshed whenever ui_style.py is reloaded.
c = _colors()

BG = c["bg"]
CARD = c["card"]
CARD_DARK = c["card2"]
TEXT = c["text"]
MUTED = c["muted"]
ACCENT = c["accent"]

# Some existing screens use these names.
ACCENT2 = c["accent"]
SUCCESS = c["success"]
DANGER = c["danger"]

# Border color follows the selected accent.
LINE = (
    ACCENT[0],
    ACCENT[1],
    ACCENT[2],
    0.45
)


# =========================================================
# STYLED CARD
# =========================================================

class StyledCard(BoxLayout):

    def __init__(self, card_color=None, radius=17, **kwargs):

        super().__init__(**kwargs)

        if card_color is None:
            card_color = get_colors()["card"]

        with self.canvas.before:

            Color(*card_color)

            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(radius)]
            )

            colors = get_colors()

            Color(
                colors["accent"][0],
                colors["accent"][1],
                colors["accent"][2],
                0.45
            )

            self.border = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    dp(radius)
                ),
                width=0.65
            )

        self.bind(
            pos=self._sync,
            size=self._sync
        )


    def _sync(self, *_):

        self.bg.pos = self.pos
        self.bg.size = self.size

        self.border.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(17)
        )


# =========================================================
# PRIMARY BUTTON
# =========================================================

class PrimaryButton(Button):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        colors = get_colors()

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.bold = True

        with self.canvas.before:

            Color(
                *colors["accent"]
            )

            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(14)]
            )

        self.bind(
            pos=self._sync,
            size=self._sync
        )


    def _sync(self, *_):

        self.bg.pos = self.pos
        self.bg.size = self.size


# =========================================================
# SECONDARY BUTTON
# =========================================================

class SecondaryButton(Button):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        colors = get_colors()

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = colors["text"]

        with self.canvas.before:

            Color(
                *colors["card2"]
            )

            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(13)]
            )

        self.bind(
            pos=self._sync,
            size=self._sync
        )


    def _sync(self, *_):

        self.bg.pos = self.pos
        self.bg.size = self.size


# =========================================================
# DANGER BUTTON
# =========================================================

class DangerButton(Button):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        colors = get_colors()

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.color = colors["text"]

        with self.canvas.before:

            Color(
                *colors["danger"]
            )

            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(13)]
            )

        self.bind(
            pos=self._sync,
            size=self._sync
        )


    def _sync(self, *_):

        self.bg.pos = self.pos
        self.bg.size = self.size


# =========================================================
# SECTION LABEL
# =========================================================

def section_label(text):

    colors = get_colors()

    return Label(
        text=text.upper(),
        font_size="9sp",
        bold=True,
        color=colors["accent"],
        halign="left",
        valign="middle",
        size_hint_y=None,
        height=dp(22),
    )


# =========================================================
# TITLE
# =========================================================

def title_label(text, size=23):

    colors = get_colors()

    return Label(
        text=text,
        font_size=f"{size}sp",
        bold=True,
        color=colors["text"],
        halign="left",
        valign="middle",
        size_hint_y=None,
        height=dp(34),
    )


# =========================================================
# SUBTITLE
# =========================================================

def subtitle_label(text):

    colors = get_colors()

    return Label(
        text=text,
        font_size="11sp",
        color=colors["muted"],
        halign="left",
        valign="middle",
        size_hint_y=None,
        height=dp(23),
    )


# =========================================================
# TEXT INPUT
# =========================================================

def styled_input(hint="", text=""):

    colors = get_colors()

    return TextInput(
        text=text,
        hint_text=hint,
        multiline=False,
        foreground_color=colors["text"],
        hint_text_color=colors["muted"],
        cursor_color=colors["accent"],
        background_normal="",
        background_active="",
        background_color=colors["card2"],
        padding=[
            dp(12),
            dp(10)
        ],
        size_hint_y=None,
        height=dp(44),
    )
