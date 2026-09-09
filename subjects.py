from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView

from database import (
    get_subjects, add_subject, rename_subject,
    delete_subject, get_subject_by_name, get_subject_study_seconds
)
from navigation import Navigation
from ui_style import (
    StyledCard, PrimaryButton, SecondaryButton, DangerButton,
    section_label, title_label, subtitle_label, styled_input
)
from theme import get_colors

def fmt(seconds):
    seconds = int(seconds or 0)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    return f"{h}h {m:02d}m" if h else f"{m}m"

class SubjectsPage(BoxLayout):
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
        self.add_widget(Navigation.top_bar(self, "Subjects"))

        header = BoxLayout(
            orientation="vertical", size_hint_y=None, height=dp(58)
        )
        header.add_widget(title_label("Subjects", 23))
        header.add_widget(subtitle_label("Track your progress across every subject"))
        self.add_widget(header)

        add = PrimaryButton(
            text="+  ADD SUBJECT",
            font_size="10sp",
            size_hint_y=None,
            height=dp(45)
        )
        add.bind(on_release=lambda *_: self.show_subject_popup())
        self.add_widget(add)

        self.add_widget(section_label("Your Subjects"))

        scroll = ScrollView(bar_width=dp(2), do_scroll_x=False)
        self.box = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=[0, dp(3), 0, dp(12)],
            size_hint_y=None
        )
        self.box.bind(minimum_height=self.box.setter("height"))
        scroll.add_widget(self.box)
        self.add_widget(scroll)

        self.add_widget(Navigation.bottom_nav(self))
        self.refresh()

    def refresh(self):
        self.box.clear_widgets()
        rows = get_subjects()

        if not rows:
            empty = StyledCard(
                orientation="vertical",
                padding=dp(15),
                size_hint_y=None,
                height=dp(105)
            )
            empty.add_widget(Label(
                text="No subjects yet",
                color=get_colors()["text"], font_size="15sp", bold=True
            ))
            empty.add_widget(Label(
                text="Add a subject to start tracking study time.",
                color=get_colors()["muted"], font_size="10sp"
            ))
            self.box.add_widget(empty)
            return

        for subject in rows:
            self.add_subject_card(subject)

    def add_subject_card(self, subject):
        card = StyledCard(
            orientation="horizontal",
            padding=[dp(13), dp(9)],
            spacing=dp(8),
            size_hint_y=None,
            height=dp(78)
        )

        info = BoxLayout(orientation="vertical", spacing=dp(1))
        info.add_widget(Label(
            text=subject["name"],
            color=get_colors()["text"], font_size="15sp", bold=True,
            halign="left", valign="middle"
        ))
        info.add_widget(Label(
            text=f'{fmt(get_subject_study_seconds(subject["id"]))} studied',
            color=get_colors()["muted"], font_size="10sp",
            halign="left", valign="middle"
        ))
        card.add_widget(info)

        edit = SecondaryButton(
            text="EDIT", font_size="9sp",
            size_hint_x=None, width=dp(61)
        )
        edit.bind(
            on_release=lambda *_,
            sid=subject["id"]: self.show_subject_popup(sid)
        )
        card.add_widget(edit)

        delete = DangerButton(
            text="X", font_size="11sp",
            size_hint_x=None, width=dp(42)
        )
        delete.bind(
            on_release=lambda *_,
            sid=subject["id"]: self.confirm_delete(sid)
        )
        card.add_widget(delete)

        self.box.add_widget(card)

    def show_subject_popup(self, subject_id=None):
        editing = subject_id is not None
        current = next((x for x in get_subjects() if x["id"] == subject_id), None) if editing else None

        box = BoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(9)
        )
        box.add_widget(section_label("Subject Name"))

        field = styled_input(
            "e.g. Data Structures",
            current["name"] if current else ""
        )
        box.add_widget(field)

        message = Label(
            text="",
            color=get_colors()["danger"],
            font_size="10sp",
            size_hint_y=None,
            height=dp(22)
        )
        box.add_widget(message)

        actions = BoxLayout(
            spacing=dp(8),
            size_hint_y=None,
            height=dp(44)
        )
        cancel = SecondaryButton(text="CANCEL")
        save = PrimaryButton(text="SAVE")
        actions.add_widget(cancel)
        actions.add_widget(save)
        box.add_widget(actions)

        popup = Popup(
            title="Edit Subject" if editing else "Add Subject",
            content=box,
            size_hint=(0.88, None),
            height=dp(255),
            separator_color=get_colors()["accent"]
        )
        cancel.bind(on_release=popup.dismiss)

        def save_subject(*_):
            name = field.text.strip()
            if not name:
                message.text = "Enter a subject name."
                return

            if editing:
                rename_subject(subject_id, name)
            else:
                if add_subject(name) is None:
                    message.text = "That subject already exists."
                    return

            popup.dismiss()
            self.refresh()

        save.bind(on_release=save_subject)
        popup.open()

    def confirm_delete(self, subject_id):
        subject = next((x for x in get_subjects() if x["id"] == subject_id), None)
        if not subject:
            return

        box = BoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(10)
        )
        box.add_widget(Label(
            text=f'Delete "{subject["name"]}"?',
            color=get_colors()["text"], font_size="15sp", bold=True
        ))
        box.add_widget(Label(
            text="Its recorded study time will also be removed.",
            color=get_colors()["muted"], font_size="10sp"
        ))

        actions = BoxLayout(
            spacing=dp(8), size_hint_y=None, height=dp(44)
        )
        cancel = SecondaryButton(text="CANCEL")
        remove = DangerButton(text="DELETE")
        actions.add_widget(cancel)
        actions.add_widget(remove)
        box.add_widget(actions)

        popup = Popup(
            title="Delete Subject",
            content=box,
            size_hint=(0.88, None),
            height=dp(220),
            separator_color=get_colors()["danger"]
        )
        cancel.bind(on_release=popup.dismiss)

        def do_delete(*_):
            delete_subject(subject_id)
            popup.dismiss()
            self.refresh()

        remove.bind(on_release=do_delete)
        popup.open()

SubjectsScreen = SubjectsPage
