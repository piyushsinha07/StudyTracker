STUDY TRACKER — FINAL UI PACK

This is the unified UI version.

Replace these files in your project:
    main.py
    ui_style.py
    theme.py
    navigation.py
    dashboard.py
    subjects.py
    timer.py
    stats.py
    tasks.py
    more.py

Keep:
    database.py
    study_tracker.db

Important changes:
- Dashboard keeps the previous Dashboard layout you preferred.
- All screens now use the same plum/pink glass visual system.
- Timer functionality is preserved and restyled.
- More is NO LONGER a ScreenManager page.
- More / Settings opens from the top-left "..." button.
- Bottom navigation is Home / Subjects / Timer / Stats / Tasks.
- Settings changes refresh the underlying screen.
- No emoji icons are used.

Run:
    python main.py

If an old database is present, keep it. The UI uses the existing database structure.
