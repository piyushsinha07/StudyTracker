from kivy.metrics import dp

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from kivy.graphics import Color, RoundedRectangle

from theme import get_colors


# =========================================================
# NAVIGATION
# =========================================================

class Navigation:


    # =====================================================
    # GET NAVIGATE FUNCTION
    # =====================================================

    @staticmethod
    def get_navigate(screen):

        def navigate(name):

            try:

                if hasattr(screen, "navigate"):

                    screen.navigate(name)

            except Exception as e:

                print(
                    "Navigation error:",
                    e
                )

        return navigate


    # =====================================================
    # TOP BAR
    # =====================================================

    @staticmethod
    def top_bar(*args):

        c = get_colors()


        # -------------------------------------------------
        # Support:
        #
        # Navigation.top_bar(self, "Title")
        #
        # Navigation.top_bar("Title", navigate)
        # -------------------------------------------------

        screen = None
        title = "Study Tracker"
        navigate_function = None


        if len(args) == 2:

            if isinstance(args[0], str):

                # Old style

                title = args[0]

                navigate_function = args[1]

            else:

                # New style

                screen = args[0]

                title = args[1]


        # -------------------------------------------------
        # TOP BAR
        # -------------------------------------------------

        bar = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(54),
            padding=[
                dp(4),
                dp(3)
            ],
            spacing=dp(4)
        )


        # =================================================
        # THREE DOT BUTTON
        # =================================================

        menu = Button(
            text="...",
            font_size=17,
            bold=True,
            size_hint_x=None,
            width=dp(45),
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            color=c["text"]
        )


        def open_more(*args):

            try:

                # If a screen object was supplied,
                # get its current navigate function NOW.

                if screen is not None:

                    if hasattr(
                        screen,
                        "navigate"
                    ):

                        screen.navigate(
                            "more"
                        )

                    return


                # Otherwise use supplied function

                if navigate_function is not None:

                    navigate_function(
                        "more"
                    )

            except Exception as e:

                print(
                    "More button error:",
                    e
                )


        menu.bind(
            on_release=open_more
        )


        bar.add_widget(
            menu
        )


        # =================================================
        # TITLE
        # =================================================

        title_label = Label(
            text=title,
            font_size=21,
            bold=True,
            color=c["text"],
            halign="left",
            valign="middle"
        )


        title_label.bind(
            size=lambda obj, value:
            setattr(
                obj,
                "text_size",
                value
            )
        )


        bar.add_widget(
            title_label
        )


        return bar


    # =====================================================
    # BOTTOM NAVIGATION
    # =====================================================

    @staticmethod
    def bottom_nav(*args):

        c = get_colors()


        screen = None
        navigate_function = None
        current = None


        # -------------------------------------------------
        # Navigation.bottom_nav(navigate, "home")
        # -------------------------------------------------

        if len(args) == 2:

            navigate_function = args[0]

            current = args[1]


        # -------------------------------------------------
        # Navigation.bottom_nav(self)
        # -------------------------------------------------

        elif len(args) == 1:

            screen = args[0]

            current = (
                Navigation.get_current_screen(
                    screen
                )
            )


        # -------------------------------------------------
        # NAVIGATION BAR
        # -------------------------------------------------

        nav = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(58),
            spacing=dp(2),
            padding=[
                dp(4),
                dp(4),
                dp(4),
                dp(4)
            ]
        )


        items = [
            ("Home", "home"),
            ("Subjects", "subjects"),
            ("Timer", "timer"),
            ("Stats", "stats"),
            ("Tasks", "tasks")
        ]


        for text, screen_name in items:

            active = (
                screen_name == current
            )


            button = Button(
                text=text,
                font_size=11,
                bold=active,
                background_normal="",
                background_down="",
                color=(
                    (1, 1, 1, 1)
                    if active
                    else c["text"]
                )
            )


            # -------------------------------------------------
            # ACTIVE BUTTON
            # -------------------------------------------------

            if active:

                button.background_color = (
                    c["accent"]
                )

            else:

                button.background_color = (
                    0,
                    0,
                    0,
                    0
                )


            # -------------------------------------------------
            # IMPORTANT:
            #
            # Do NOT capture the old navigate function.
            # Resolve it when clicked.
            # -------------------------------------------------

            def go_to_screen(
                instance,
                target=screen_name
            ):

                try:

                    if screen is not None:

                        if hasattr(
                            screen,
                            "navigate"
                        ):

                            screen.navigate(
                                target
                            )

                        return


                    if navigate_function is not None:

                        navigate_function(
                            target
                        )

                except Exception as e:

                    print(
                        "Bottom navigation error:",
                        e
                    )


            button.bind(
                on_release=go_to_screen
            )


            nav.add_widget(
                button
            )


        return nav



    # =====================================================
    # CHANGE SCREEN
    # =====================================================

    @staticmethod
    def change_screen(source, name):

        try:
            if hasattr(source, "manager") and source.manager is not None:
                source.manager.current = name
                return

            if hasattr(source, "navigate"):
                source.navigate(name)
                return

            if hasattr(source, "current"):
                source.current = name

        except Exception as e:
            print("Screen change error:", e)

    # =====================================================
    # GET CURRENT SCREEN
    # =====================================================

    @staticmethod
    def get_current_screen(screen):

        try:

            # Usually:
            #
            # Page
            #   ↓
            # BaseScreen
            #   ↓
            # ScreenManager

            parent = screen.parent


            while parent is not None:

                if hasattr(
                    parent,
                    "manager"
                ):

                    manager = parent.manager

                    if manager is not None:

                        return manager.current


                parent = parent.parent


        except Exception:

            pass


        return None