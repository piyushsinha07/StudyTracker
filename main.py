from kivy.config import Config

Config.set("graphics", "width", "400")
Config.set("graphics", "height", "650")

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen

from database import init_db
import theme


Window.size = (400, 650)


# =========================================================
# BASE SCREEN
# =========================================================

class BaseScreen(Screen):

    page_class = None

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.page = None

        self.create_page()


    def create_page(self):

        self.clear_widgets()

        if self.page_class is None:

            return


        self.page = self.page_class()

        self.page.navigate = self.navigate

        self.add_widget(self.page)


    def navigate(self, name):

        if self.manager is None:

            return


        if name in self.manager.screen_names:

            self.manager.current = name


    def rebuild_page(self):

        self.create_page()


    def on_pre_enter(self, *args):

        if self.page is not None:

            if hasattr(self.page, "refresh"):

                try:

                    self.page.refresh()

                except Exception as e:

                    print(
                        "Refresh error:",
                        e
                    )


# =========================================================
# SCREEN CLASSES
# =========================================================

class HomeScreen(BaseScreen):
    pass


class SubjectsScreen(BaseScreen):
    pass


class TimerScreen(BaseScreen):
    pass


class StatsScreen(BaseScreen):
    pass


class TasksScreen(BaseScreen):
    pass


class MoreScreen(BaseScreen):
    pass


class ProfileScreen(BaseScreen):
    pass


# =========================================================
# APPLICATION
# =========================================================

class StudyTrackerApp(App):

    title = "Study Tracker"


    def build(self):

        init_db()

        theme.apply_window()

        self.sm = ScreenManager()

        self.load_page_classes()

        self.create_all_screens()

        self.sm.current = "home"

        return self.sm


    # =====================================================
    # LOAD PAGE CLASSES
    # =====================================================

    def load_page_classes(self):

        global dashboard
        global subjects
        global timer
        global stats
        global tasks
        global more
        global profile


        import dashboard
        import subjects
        import timer
        import stats
        import tasks
        import more
        import profile


        HomeScreen.page_class = (
            dashboard.Dashboard
        )

        SubjectsScreen.page_class = (
            subjects.SubjectsPage
        )

        TimerScreen.page_class = (
            timer.TimerPage
        )

        StatsScreen.page_class = (
            stats.StatsPage
        )

        TasksScreen.page_class = (
            tasks.TasksPage
        )

        MoreScreen.page_class = (
            more.MorePage
        )

        ProfileScreen.page_class = (
            profile.ProfilePage
        )


    # =====================================================
    # CREATE SCREENS
    # =====================================================

    def create_all_screens(self):

        self.sm.clear_widgets()


        self.sm.add_widget(
            HomeScreen(
                name="home"
            )
        )


        self.sm.add_widget(
            SubjectsScreen(
                name="subjects"
            )
        )


        self.sm.add_widget(
            TimerScreen(
                name="timer"
            )
        )


        self.sm.add_widget(
            StatsScreen(
                name="stats"
            )
        )


        self.sm.add_widget(
            TasksScreen(
                name="tasks"
            )
        )


        self.sm.add_widget(
            MoreScreen(
                name="more"
            )
        )


        self.sm.add_widget(
            ProfileScreen(
                name="profile"
            )
        )


    # =====================================================
    # REFRESH THEME
    # =====================================================

    def refresh_theme(self):

        print("Applying new theme...")

        current_screen = self.sm.current

        # Every page now asks theme.get_colors() when it is built,
        # so simply rebuilding the pages applies the new theme.
        theme.apply_window()

        self.load_page_classes()
        self.create_all_screens()

        if current_screen in self.sm.screen_names:

            self.sm.current = current_screen

        else:

            self.sm.current = "home"

        print("Theme applied to all screens.")

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    StudyTrackerApp().run()