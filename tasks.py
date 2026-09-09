from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Line

from database import (
    add_task,
    get_tasks,
    toggle_task,
    delete_task
)

from navigation import Navigation

from ui_style import (
    PrimaryButton, SecondaryButton, DangerButton,
    section_label, title_label, subtitle_label, styled_input
)
from theme import get_colors


# =========================================================
# CHECKBOX
# =========================================================

class TaskCheckBox(CheckBox):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.size_hint = (None, None)
        self.size = (dp(30), dp(30))
        self.color = get_colors()["accent"]


# =========================================================
# TASK SECTION
# =========================================================

class TaskSection(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Transparent / dark background
        with self.canvas.before:

            c = get_colors()
            Color(
                c["card2"][0],
                c["card2"][1],
                c["card2"][2],
                0.30
            )

            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(16)]
            )

        # Pink border
        with self.canvas.after:

            Color(
                c["accent"][0],
                c["accent"][1],
                c["accent"][2],
                0.65
            )

            self.border = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    dp(16)
                ),
                width=1
            )

        self.bind(
            pos=self.update_graphics,
            size=self.update_graphics
        )


    def update_graphics(self, *_):

        self.bg.pos = self.pos
        self.bg.size = self.size

        self.border.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            dp(16)
        )


# =========================================================
# TASK SCREEN
# =========================================================

class TasksScreen(BoxLayout):

    def __init__(self, **kwargs):

        super().__init__(
            orientation="vertical",
            spacing=dp(7),
            padding=[
                dp(10),
                dp(8),
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


        # -------------------------------------------------
        # TOP BAR
        # -------------------------------------------------

        self.add_widget(
            Navigation.top_bar(
                self,
                "Tasks"
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
                "Tasks & Topics",
                23
            )
        )


        header.add_widget(
            subtitle_label(
                "Keep track of what you need to finish"
            )
        )


        self.add_widget(
            header
        )


        # -------------------------------------------------
        # ADD TASK BUTTON
        # -------------------------------------------------

        add_button = PrimaryButton(
            text="+  ADD TASK",
            size_hint_y=None,
            height=dp(44)
        )


        add_button.bind(
            on_release=lambda *_:
            self.add_task_popup()
        )


        self.add_widget(
            add_button
        )


        # -------------------------------------------------
        # MAIN SCROLL VIEW
        # -------------------------------------------------

        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(3)
        )


        # IMPORTANT:
        #
        # This BoxLayout fills the available height.
        # Therefore the spacer below can push the
        # Completed Tasks box to the bottom.

        self.content = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=[
                0,
                dp(4),
                0,
                dp(8)
            ]
        )


        scroll.add_widget(
            self.content
        )


        self.add_widget(
            scroll
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
    # REFRESH
    # =====================================================

    def refresh(self):

        self.refresh_tasks()


    # =====================================================
    # REFRESH TASKS
    # =====================================================

    def refresh_tasks(self):

        self.content.clear_widgets()


        # -------------------------------------------------
        # GET TASKS
        # -------------------------------------------------

        tasks = get_tasks()


        # -------------------------------------------------
        # PENDING TASKS
        # -------------------------------------------------

        pending_tasks = [
            task
            for task in tasks
            if not bool(
                task["completed"]
            )
        ]


        # -------------------------------------------------
        # COMPLETED TASKS
        # -------------------------------------------------

        completed_tasks = [
            task
            for task in tasks
            if bool(
                task["completed"]
            )
        ]


        # =================================================
        # TASKS BOX
        # =================================================

        tasks_box = TaskSection(
            orientation="vertical",
            spacing=dp(4),
            padding=[
                dp(10),
                dp(8)
            ],
            size_hint_y=None
        )


        # -------------------------------------------------
        # TASKS HEADER
        # -------------------------------------------------

        task_header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(27)
        )


        task_header.add_widget(
            section_label(
                "TASKS"
            )
        )


        task_count = Label(
            text=str(
                len(pending_tasks)
            ),
            color=get_colors()["muted"],
            font_size="9sp",
            size_hint_x=None,
            width=dp(25)
        )


        task_header.add_widget(
            task_count
        )


        tasks_box.add_widget(
            task_header
        )


        # -------------------------------------------------
        # TASK ROWS
        # -------------------------------------------------

        if pending_tasks:

            for task in pending_tasks:

                self.add_task_row(
                    task,
                    tasks_box
                )


            # Dynamic height:
            #
            # Header
            # + each task
            # + padding

            tasks_box.height = (
                dp(43)
                +
                (
                    len(pending_tasks)
                    * dp(55)
                )
                +
                dp(8)
            )


        else:

            empty = Label(
                text="No pending tasks",
                color=get_colors()["muted"],
                font_size="9sp",
                size_hint_y=None,
                height=dp(30)
            )


            tasks_box.add_widget(
                empty
            )


            tasks_box.height = dp(70)


        # =================================================
        # ALWAYS ADD TASKS FIRST
        # =================================================

        self.content.add_widget(
            tasks_box
        )


        # =================================================
        # FLEXIBLE SPACE
        # =================================================

        # This pushes the completed box to the bottom
        # whenever there is free vertical space.

        spacer = BoxLayout(
            size_hint_y=1
        )


        self.content.add_widget(
            spacer
        )


        # =================================================
        # COMPLETED TASKS BOX
        # =================================================

        completed_box = TaskSection(
            orientation="vertical",
            spacing=dp(4),
            padding=[
                dp(10),
                dp(8)
            ],
            size_hint_y=None
        )


        # -------------------------------------------------
        # COMPLETED HEADER
        # -------------------------------------------------

        completed_header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(27)
        )


        completed_header.add_widget(
            section_label(
                "COMPLETED TASKS"
            )
        )


        completed_count = Label(
            text=str(
                len(completed_tasks)
            ),
            color=get_colors()["muted"],
            font_size="9sp",
            size_hint_x=None,
            width=dp(25)
        )


        completed_header.add_widget(
            completed_count
        )


        completed_box.add_widget(
            completed_header
        )


        # -------------------------------------------------
        # COMPLETED TASK ROWS
        # -------------------------------------------------

        if completed_tasks:

            for task in completed_tasks:

                self.add_task_row(
                    task,
                    completed_box
                )


            completed_box.height = (
                dp(43)
                +
                (
                    len(completed_tasks)
                    * dp(55)
                )
                +
                dp(8)
            )


        else:

            empty = Label(
                text="No completed tasks yet",
                color=get_colors()["muted"],
                font_size="9sp",
                size_hint_y=None,
                height=dp(30)
            )


            completed_box.add_widget(
                empty
            )


            completed_box.height = dp(70)


        # =================================================
        # ALWAYS ADD COMPLETED LAST
        # =================================================

        self.content.add_widget(
            completed_box
        )


    # =====================================================
    # TASK ROW
    # =====================================================

    def add_task_row(
        self,
        task,
        parent
    ):

        task_id = task["id"]

        task_title = task["title"]

        completed = bool(
            task["completed"]
        )


        # -------------------------------------------------
        # ROW
        # -------------------------------------------------

        row = BoxLayout(
            orientation="horizontal",
            spacing=dp(7),
            padding=[
                dp(4),
                dp(2)
            ],
            size_hint_y=None,
            height=dp(55)
        )


        # -------------------------------------------------
        # CHECKBOX
        # -------------------------------------------------

        checkbox = TaskCheckBox(
            active=completed
        )


        row.add_widget(
            checkbox
        )


        # -------------------------------------------------
        # get_colors()["text"] AREA
        # -------------------------------------------------

        text_box = BoxLayout(
            orientation="vertical",
            spacing=0
        )


        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        title = Label(
            text=task_title,

            color=(
                get_colors()["muted"]
                if completed
                else get_colors()["text"]
            ),

            font_size="11sp",

            bold=not completed,

            halign="left",

            valign="middle"
        )


        title.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )


        text_box.add_widget(
            title
        )


        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        status = Label(
            text=(
                "COMPLETED"
                if completed
                else "PENDING"
            ),

            color=(
                get_colors()["accent"]
                if completed
                else get_colors()["muted"]
            ),

            font_size="7sp",

            halign="left",

            valign="middle"
        )


        status.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )


        text_box.add_widget(
            status
        )


        row.add_widget(
            text_box
        )


        # -------------------------------------------------
        # DELETE BUTTON
        # -------------------------------------------------

        delete = DangerButton(
            text="×",
            size_hint_x=None,
            width=dp(42),
            font_size="17sp"
        )


        delete.bind(
            on_release=lambda *_,
            tid=task_id:
            self.remove_task(
                tid
            )
        )


        row.add_widget(
            delete
        )


        # -------------------------------------------------
        # CHECKBOX ACTION
        # -------------------------------------------------

        def checkbox_changed(
            checkbox,
            value
        ):

            toggle_task(
                task_id
            )


            # Rebuild the two sections.
            #
            # CHECK:
            # TASKS
            #      ↓
            # COMPLETED TASKS
            #
            # UNCHECK:
            # COMPLETED TASKS
            #      ↓
            # TASKS

            self.refresh_tasks()


        checkbox.bind(
            active=checkbox_changed
        )


        parent.add_widget(
            row
        )


    # =====================================================
    # ADD TASK POPUP
    # =====================================================

    def add_task_popup(self):

        box = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10)
        )


        # -------------------------------------------------
        # LABEL
        # -------------------------------------------------

        box.add_widget(
            section_label(
                "NEW TASK"
            )
        )


        # -------------------------------------------------
        # INPUT
        # -------------------------------------------------

        task_input = styled_input(
            "Task or topic"
        )


        box.add_widget(
            task_input
        )


        # -------------------------------------------------
        # BUTTONS
        # -------------------------------------------------

        buttons = BoxLayout(
            spacing=dp(8),
            size_hint_y=None,
            height=dp(44)
        )


        cancel = SecondaryButton(
            text="CANCEL"
        )


        add = PrimaryButton(
            text="ADD"
        )


        buttons.add_widget(
            cancel
        )


        buttons.add_widget(
            add
        )


        box.add_widget(
            buttons
        )


        # -------------------------------------------------
        # POPUP
        # -------------------------------------------------

        popup = Popup(
            title="Add Task",
            content=box,
            size_hint=(
                0.86,
                None
            ),
            height=dp(230),
            separator_color=get_colors()["accent"]
        )


        cancel.bind(
            on_release=popup.dismiss
        )


        # -------------------------------------------------
        # SAVE
        # -------------------------------------------------

        def save(*_):

            task_text = (
                task_input.text.strip()
            )


            if not task_text:
                return


            add_task(
                task_text
            )


            popup.dismiss()


            self.refresh_tasks()


        add.bind(
            on_release=save
        )


        popup.open()


        task_input.focus = True


    # =====================================================
    # DELETE TASK
    # =====================================================

    def remove_task(
        self,
        task_id
    ):

        delete_task(
            task_id
        )


        self.refresh_tasks()


# =========================================================
# COMPATIBILITY
# =========================================================

TasksPage = TasksScreen