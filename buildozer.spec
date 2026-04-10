[app]

# (str) Title of your application
title = Mess Manager

# (str) Package name
package.name = messmanager

# (str) Package domain (needed for android/ios packaging)
package.domain = org.messmanager

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,db

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to exclude nothing)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to exclude nothing)
#source.exclude_dirs = tests, bin, venv

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*_orig.png

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.1,reportlab

# (str) Custom source folders for requirements
# packagename.ignore_warnings = True

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientations (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
#android.sdk = 20

# (str) Android NDK version to use
#android.ndk = 23b

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
#android.ant_path =

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess bandwidth usage or redirecting to a local SDK
#android.skip_update = False

# (bool) If True, then manually accepts SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when installing SDK
android.accept_sdk_license = True

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme, default is ok for Kivy-based app
# android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Pattern to white list for the libp7zip
#android.p7zip_whitelist =

# (str) For resizable (must be True for multisplit)
#android.window_resizable = True

# (list) Extra window attributes
#android.window_attributes = 

# (list) List of Java files to add to the android project
#android.add_libs_clashing = 

# (str) Full name including package path of the Java class that implements PythonService
#android.service_class_name = org.kivy.android.PythonService

# (list) Android additionnal libraries to copy into libs/armeabi
#android.add_libs_armeabi = lib/armeabi/libtest.so

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >= 23)
android.allow_backup = True

# (str) format used to package the app for release mode (aab or apk or aar)
android.release_artifact = apk

# (str) format used to package the app for debug mode (aab or apk or aar)
android.debug_artifact = apk

#
# Python for android (p4a) specific
#

# (str) python-for-android branch to use, defaults to master
#p4a.branch = master

# (str) python-for-android git repository to use, defaults to https://github.com/kivy/python-for-android.git
#p4a.url =

# (str) python-for-android local directory to use (substitutes p4a.url and p4a.branch)
#p4a.source_dir =

# (list) List of extra p4a arguments
#p4a.extra_args = 


#
# iOS specific
#

# (str) Path to a custom icon to use (o/w default Kivy icon is used)
#ios.icon.filename = %(source.dir)s/data/icon.png

# (str) Name of the certificate to use for signing the debug version
# Get a list of available identities: buildozer ios list_identities
#ios.codesign.debug = "iPhone Developer: <firstname> <lastname> (<identifier>)"

# (str) Name of the certificate to use for signing the release version
#ios.codesign.release = %(ios.codesign.debug)s


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (str) Path to build artifact storage, second part is default
warn_on_root = 1

# (str) Path to build output (default is ./bin)
# bin_dir = ./bin
