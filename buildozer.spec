[app]

# (str) Title of your application
title = Study Tracker

# (str) Package name
package.name = studytracker

# (str) Package domain
package.domain = org.studytracker

# (str) Source code directory
source.dir = .

# (str) Application version
version = 1.0.0

# (list) Source files to include
source.include_exts = py,png,jpg,jpeg,kv,atlas,db,txt

# (str) Application requirements
requirements = python3,kivy==2.3.1

# (str) Supported orientation
orientation = portrait

# (bool) Fullscreen
fullscreen = 0


# --------------------------------------------------
# Android settings
# --------------------------------------------------

# Android package version
android.numeric_version = 1

# Android architectures
android.archs = arm64-v8a,armeabi-v7a

# Android backup
android.allow_backup = True

# Android API
android.api = 35

# Minimum Android API
android.minapi = 24

# Android NDK
android.ndk = 28c

# NDK API
android.ndk_api = 24

# Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# Automatically accept Android SDK licenses
android.accept_sdk_license = True


[buildozer]

# (str) Log level
log_level = 2

# (bool) Warn if buildozer is run as root
warn_on_root = 1
