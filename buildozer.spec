[app]
title = Nexoguard
package.name = nexoguard
package.domain = org.nexoguard
source.dir = .
source.include_exts = py,png,jpg,kv,html,css,js
source.include_patterns = templates/*

version = 1.0
requirements = python3,kivy,flask,android,requests

orientation = portrait
fullscreen = 1

android.permissions = INTERNET, ACCESS_WIFI_STATE, ACCESS_NETWORK_STATE, CHANGE_WIFI_STATE, ACCESS_FINE_LOCATION

android.api = 33
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
