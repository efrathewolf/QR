[app]
title = Creador QR Avanzado
package.name = creadorqr
package.domain = com.multiserviciosvazquez
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,txt
version = 1.0.0
requirements = python3,kivy==2.3.0,qrcode[pil]==8.2,pillow
orientation = portrait
fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 35
android.minapi = 23
android.ndk = 27c
android.archs = arm64-v8a
android.accept_sdk_license = True
p4a.branch = v2024.01.21

[buildozer]
log_level = 2
warn_on_root = 1
