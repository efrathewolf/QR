#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced QR Code Creator  ·  Creador de códigos QR  ·  Créateur de QR codes
---------------------------------------------------------------------------
Features / Funciones / Fonctionnalités:
  • 7 content types: Text/URL, Wi-Fi, vCard, Email, SMS, Phone, Geo
  • Module shapes: square, rounded, circle, gapped, vertical/horizontal bars
  • Color modes: solid, radial / square / horizontal / vertical gradients
  • Logo embedding with automatic error-correction upgrade
  • Export to PNG, JPG and SVG (vector)
  • Live preview
  • Language selector: Español / English / Français
"""

import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from urllib.parse import quote

# --------------------------------------------------------------------------
# Dependencies
# --------------------------------------------------------------------------
try:
    import qrcode
    from qrcode.constants import (ERROR_CORRECT_L, ERROR_CORRECT_M,
                                  ERROR_CORRECT_Q, ERROR_CORRECT_H)
except ImportError:
    raise SystemExit("Missing dependency: qrcode\n  pip install qrcode pillow")

try:
    from PIL import Image, ImageTk
except ImportError:
    raise SystemExit("Missing dependency: Pillow\n  pip install qrcode pillow")

HAS_STYLED = False
try:
    from qrcode.image.styledpil import StyledPilImage
    try:  # qrcode >= 7.4
        from qrcode.image.styles.moduledrawers.pil import (
            SquareModuleDrawer, RoundedModuleDrawer, CircleModuleDrawer,
            GappedSquareModuleDrawer, VerticalBarsDrawer, HorizontalBarsDrawer)
    except ImportError:  # older layout
        from qrcode.image.styles.moduledrawers import (
            SquareModuleDrawer, RoundedModuleDrawer, CircleModuleDrawer,
            GappedSquareModuleDrawer, VerticalBarsDrawer, HorizontalBarsDrawer)
    from qrcode.image.styles.colormasks import (
        SolidFillColorMask, RadialGradiantColorMask, SquareGradiantColorMask,
        HorizontalGradiantColorMask, VerticalGradiantColorMask)
    HAS_STYLED = True
except ImportError:
    pass


# --------------------------------------------------------------------------
# Internationalisation
# --------------------------------------------------------------------------
LANGUAGES = {"es": "Español", "en": "English", "fr": "Français"}
LANG_ORDER = ["es", "en", "fr"]

TRANSLATIONS = {
    "en": {
        "app_title": "Advanced QR Code Creator",
        "language": "Language:",
        "tab_text": "Text / URL", "tab_wifi": "Wi-Fi", "tab_vcard": "Contact",
        "tab_email": "Email", "tab_sms": "SMS", "tab_phone": "Phone",
        "tab_geo": "Location",
        "lbl_content": "Text or URL:",
        "ph_content": "https://example.com",
        "lbl_ssid": "Network name (SSID):", "lbl_password": "Password:",
        "lbl_encryption": "Encryption:", "lbl_hidden": "Hidden network",
        "enc_none": "None", "enc_wpa": "WPA/WPA2", "enc_wep": "WEP",
        "lbl_first": "First name:", "lbl_last": "Last name:",
        "lbl_org": "Organization:", "lbl_jobtitle": "Job title:",
        "lbl_phone": "Phone:", "lbl_email": "Email:", "lbl_website": "Website:",
        "lbl_street": "Street:", "lbl_city": "City:",
        "lbl_zip": "ZIP / Postal code:", "lbl_country": "Country:",
        "lbl_to": "To:", "lbl_subject": "Subject:", "lbl_body": "Message:",
        "lbl_number": "Number:", "lbl_message": "Message:",
        "lbl_lat": "Latitude:", "lbl_lon": "Longitude:",
        "options": "Design options", "preview": "Preview",
        "opt_ec": "Error correction:", "opt_box": "Module size:",
        "opt_border": "Border:", "opt_fg": "Foreground:",
        "opt_bg": "Background:", "opt_style": "Module shape:",
        "opt_mask": "Color mode:", "opt_grad": "Gradient color:",
        "opt_logo": "Logo:", "opt_logosize": "Logo size (%):",
        "btn_browse": "Browse…", "btn_remove": "Remove",
        "style_square": "Square", "style_rounded": "Rounded",
        "style_circle": "Circle", "style_gapped": "Gapped",
        "style_vertical": "Vertical bars", "style_horizontal": "Horizontal bars",
        "mask_solid": "Solid", "mask_radial": "Radial gradient",
        "mask_square": "Square gradient", "mask_h": "Horizontal gradient",
        "mask_v": "Vertical gradient",
        "btn_generate": "Generate", "btn_save": "Save…", "btn_clear": "Clear",
        "save_title": "Save QR code",
        "status_ready": "Ready.",
        "msg_empty": "Please enter some content first.",
        "msg_saved": "Saved to:\n{path}",
        "msg_error": "Error:\n{err}",
        "msg_logo_ec": "Error correction raised to H because a logo is used.",
        "filetype_png": "PNG image", "filetype_jpg": "JPEG image",
        "filetype_svg": "SVG vector",
        "err_title": "Error", "info_title": "Information",
        "choose_color": "Choose a color",
        "fmt": "Format:", "no_logo": "No logo selected",
        "logo_files": "Image files",
    },
    "es": {
        "app_title": "Creador de códigos QR avanzado",
        "language": "Idioma:",
        "tab_text": "Texto / URL", "tab_wifi": "Wi-Fi", "tab_vcard": "Contacto",
        "tab_email": "Correo", "tab_sms": "SMS", "tab_phone": "Teléfono",
        "tab_geo": "Ubicación",
        "lbl_content": "Texto o URL:",
        "ph_content": "https://ejemplo.com",
        "lbl_ssid": "Nombre de la red (SSID):", "lbl_password": "Contraseña:",
        "lbl_encryption": "Cifrado:", "lbl_hidden": "Red oculta",
        "enc_none": "Ninguno", "enc_wpa": "WPA/WPA2", "enc_wep": "WEP",
        "lbl_first": "Nombre:", "lbl_last": "Apellido:",
        "lbl_org": "Organización:", "lbl_jobtitle": "Puesto:",
        "lbl_phone": "Teléfono:", "lbl_email": "Correo:", "lbl_website": "Sitio web:",
        "lbl_street": "Calle:", "lbl_city": "Ciudad:",
        "lbl_zip": "Código postal:", "lbl_country": "País:",
        "lbl_to": "Para:", "lbl_subject": "Asunto:", "lbl_body": "Mensaje:",
        "lbl_number": "Número:", "lbl_message": "Mensaje:",
        "lbl_lat": "Latitud:", "lbl_lon": "Longitud:",
        "options": "Opciones de diseño", "preview": "Vista previa",
        "opt_ec": "Corrección de errores:", "opt_box": "Tamaño de módulo:",
        "opt_border": "Borde:", "opt_fg": "Color frontal:",
        "opt_bg": "Fondo:", "opt_style": "Forma del módulo:",
        "opt_mask": "Modo de color:", "opt_grad": "Color del degradado:",
        "opt_logo": "Logotipo:", "opt_logosize": "Tamaño del logo (%):",
        "btn_browse": "Examinar…", "btn_remove": "Quitar",
        "style_square": "Cuadrado", "style_rounded": "Redondeado",
        "style_circle": "Círculo", "style_gapped": "Con espacio",
        "style_vertical": "Barras verticales", "style_horizontal": "Barras horizontales",
        "mask_solid": "Sólido", "mask_radial": "Degradado radial",
        "mask_square": "Degradado cuadrado", "mask_h": "Degradado horizontal",
        "mask_v": "Degradado vertical",
        "btn_generate": "Generar", "btn_save": "Guardar…", "btn_clear": "Limpiar",
        "save_title": "Guardar código QR",
        "status_ready": "Listo.",
        "msg_empty": "Introduce primero algún contenido.",
        "msg_saved": "Guardado en:\n{path}",
        "msg_error": "Error:\n{err}",
        "msg_logo_ec": "Corrección de errores elevada a H por usar logotipo.",
        "filetype_png": "Imagen PNG", "filetype_jpg": "Imagen JPEG",
        "filetype_svg": "Vector SVG",
        "err_title": "Error", "info_title": "Información",
        "choose_color": "Elige un color",
        "fmt": "Formato:", "no_logo": "Ningún logo seleccionado",
        "logo_files": "Archivos de imagen",
    },
    "fr": {
        "app_title": "Créateur de QR codes avancé",
        "language": "Langue :",
        "tab_text": "Texte / URL", "tab_wifi": "Wi-Fi", "tab_vcard": "Contact",
        "tab_email": "E-mail", "tab_sms": "SMS", "tab_phone": "Téléphone",
        "tab_geo": "Lieu",
        "lbl_content": "Texte ou URL :",
        "ph_content": "https://exemple.com",
        "lbl_ssid": "Nom du réseau (SSID) :", "lbl_password": "Mot de passe :",
        "lbl_encryption": "Chiffrement :", "lbl_hidden": "Réseau masqué",
        "enc_none": "Aucun", "enc_wpa": "WPA/WPA2", "enc_wep": "WEP",
        "lbl_first": "Prénom :", "lbl_last": "Nom :",
        "lbl_org": "Organisation :", "lbl_jobtitle": "Fonction :",
        "lbl_phone": "Téléphone :", "lbl_email": "E-mail :", "lbl_website": "Site web :",
        "lbl_street": "Rue :", "lbl_city": "Ville :",
        "lbl_zip": "Code postal :", "lbl_country": "Pays :",
        "lbl_to": "À :", "lbl_subject": "Objet :", "lbl_body": "Message :",
        "lbl_number": "Numéro :", "lbl_message": "Message :",
        "lbl_lat": "Latitude :", "lbl_lon": "Longitude :",
        "options": "Options de design", "preview": "Aperçu",
        "opt_ec": "Correction d'erreur :", "opt_box": "Taille du module :",
        "opt_border": "Bordure :", "opt_fg": "Couleur de premier plan :",
        "opt_bg": "Arrière-plan :", "opt_style": "Forme du module :",
        "opt_mask": "Mode de couleur :", "opt_grad": "Couleur du dégradé :",
        "opt_logo": "Logo :", "opt_logosize": "Taille du logo (%) :",
        "btn_browse": "Parcourir…", "btn_remove": "Retirer",
        "style_square": "Carré", "style_rounded": "Arrondi",
        "style_circle": "Cercle", "style_gapped": "Espacé",
        "style_vertical": "Barres verticales", "style_horizontal": "Barres horizontales",
        "mask_solid": "Uni", "mask_radial": "Dégradé radial",
        "mask_square": "Dégradé carré", "mask_h": "Dégradé horizontal",
        "mask_v": "Dégradé vertical",
        "btn_generate": "Générer", "btn_save": "Enregistrer…", "btn_clear": "Effacer",
        "save_title": "Enregistrer le QR code",
        "status_ready": "Prêt.",
        "msg_empty": "Veuillez d'abord saisir du contenu.",
        "msg_saved": "Enregistré dans :\n{path}",
        "msg_error": "Erreur :\n{err}",
        "msg_logo_ec": "Correction d'erreur portée à H à cause du logo.",
        "filetype_png": "Image PNG", "filetype_jpg": "Image JPEG",
        "filetype_svg": "Vectoriel SVG",
        "err_title": "Erreur", "info_title": "Information",
        "choose_color": "Choisissez une couleur",
        "fmt": "Format :", "no_logo": "Aucun logo sélectionné",
        "logo_files": "Fichiers image",
    },
}


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def hex_to_rgb(value):
    value = (value or "#000000").lstrip("#")
    if len(value) == 3:
        value = "".join(c * 2 for c in value)
    try:
        return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return (0, 0, 0)


def safe_hex(value, default="#000000"):
    value = (value or "").strip()
    if re.fullmatch(r"#?[0-9a-fA-F]{6}", value):
        return "#" + value.lstrip("#").upper()
    if re.fullmatch(r"#?[0-9a-fA-F]{3}", value):
        return "#" + "".join(c * 2 for c in value.lstrip("#")).upper()
    return default


def wifi_escape(text):
    return re.sub(r'([\\;,:"])', r'\\\1', text or "")


def vcard_escape(text):
    return (text or "").replace("\\", "\\\\").replace(";", "\\;") \
                       .replace(",", "\\,").replace("\n", "\\n")


EC_MAP = {"L": ERROR_CORRECT_L, "M": ERROR_CORRECT_M,
          "Q": ERROR_CORRECT_Q, "H": ERROR_CORRECT_H}


# --------------------------------------------------------------------------
# Main application
# --------------------------------------------------------------------------
class QRApp:
    def __init__(self, root):
        self.root = root
        self.lang = "es"
        self._tr_widgets = []
        self.logo_path = None
        self.current_image = None
        self.current_qr = None
        self.tk_preview = None

        self.tab_keys = ["text", "wifi", "vcard", "email", "sms", "phone", "geo"]
        self.style_keys = ["square", "rounded", "circle", "gapped", "vertical", "horizontal"]
        self.mask_keys = ["solid", "radial", "square", "h", "v"]
        self.enc_keys = ["n", "WPA", "WEP"]

        self._create_vars()
        self._build_ui()
        self.retranslate()

    # ------------------------------------------------------------------ i18n
    def T(self, key, **kw):
        text = TRANSLATIONS.get(self.lang, TRANSLATIONS["en"]).get(key, key)
        return text.format(**kw) if kw else text

    def reg(self, widget, key, attr="text"):
        self._tr_widgets.append((widget, key, attr))
        try:
            widget.configure(**{attr: self.T(key)})
        except tk.TclError:
            pass
        return widget

    # ------------------------------------------------------------------ vars
    def _create_vars(self):
        # Wi-Fi
        self.v_ssid = tk.StringVar()
        self.v_pass = tk.StringVar()
        self.v_hidden = tk.BooleanVar(value=False)
        # vCard
        self.v_first = tk.StringVar()
        self.v_last = tk.StringVar()
        self.v_org = tk.StringVar()
        self.v_jobtitle = tk.StringVar()
        self.v_phone = tk.StringVar()
        self.v_email = tk.StringVar()
        self.v_website = tk.StringVar()
        self.v_street = tk.StringVar()
        self.v_city = tk.StringVar()
        self.v_zip = tk.StringVar()
        self.v_country = tk.StringVar()
        # Email
        self.v_to = tk.StringVar()
        self.v_subject = tk.StringVar()
        # SMS / Phone
        self.v_number = tk.StringVar()
        # Geo
        self.v_lat = tk.StringVar()
        self.v_lon = tk.StringVar()
        # Design
        self.v_box = tk.IntVar(value=10)
        self.v_border = tk.IntVar(value=4)
        self.v_logosize = tk.IntVar(value=20)
        self.v_fg = tk.StringVar(value="#000000")
        self.v_bg = tk.StringVar(value="#FFFFFF")
        self.v_grad = tk.StringVar(value="#3B82F6")
        self.v_logo_display = tk.StringVar(value="")

    # -------------------------------------------------------------------- UI
    def _build_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # ---- top bar -----------------------------------------------------
        top = ttk.Frame(self.root, padding=(12, 10, 12, 6))
        top.pack(fill="x")

        self.title_label = ttk.Label(top, font=("Segoe UI", 15, "bold"))
        self.reg(self.title_label, "app_title")
        self.title_label.pack(side="left")

        lang_box = ttk.Frame(top)
        lang_box.pack(side="right")
        self.lang_label = ttk.Label(lang_box)
        self.reg(self.lang_label, "language")
        self.lang_label.pack(side="left", padx=(0, 6))

        self.lang_combo = ttk.Combobox(
            lang_box, state="readonly", width=12,
            values=[LANGUAGES[c] for c in LANG_ORDER])
        self.lang_combo.current(LANG_ORDER.index(self.lang))
        self.lang_combo.pack(side="left")
        self.lang_combo.bind("<<ComboboxSelected>>", self._on_lang_change)

        ttk.Separator(self.root).pack(fill="x", padx=12)

        # ---- main area ---------------------------------------------------
        main = ttk.Frame(self.root, padding=(12, 8, 12, 4))
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=0)
        main.rowconfigure(0, weight=1)

        left = ttk.Frame(main)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        right = ttk.Frame(main)
        right.grid(row=0, column=1, sticky="nsew")

        self._build_notebook(left)
        self._build_options(right)
        self._build_preview(right)

        # ---- bottom bar --------------------------------------------------
        bottom = ttk.Frame(self.root, padding=(12, 6, 12, 10))
        bottom.pack(fill="x")

        self.btn_generate = ttk.Button(bottom, command=self.generate, width=16)
        self.reg(self.btn_generate, "btn_generate")
        self.btn_generate.pack(side="left", padx=(0, 8))

        self.btn_save = ttk.Button(bottom, command=self.save, width=16)
        self.reg(self.btn_save, "btn_save")
        self.btn_save.pack(side="left", padx=(0, 8))

        self.btn_clear = ttk.Button(bottom, command=self.clear_current, width=12)
        self.reg(self.btn_clear, "btn_clear")
        self.btn_clear.pack(side="left")

        self.status = ttk.Label(bottom, anchor="e")
        self.status.pack(side="right", fill="x", expand=True)

    # ---- notebook --------------------------------------------------------
    def _build_notebook(self, parent):
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True)

        self.tab_frames = {}
        for key in self.tab_keys:
            frame = ttk.Frame(self.notebook, padding=14)
            self.notebook.add(frame, text=key)
            self.tab_frames[key] = frame
            getattr(self, f"_build_tab_{key}")(frame)

    def _field(self, parent, row, key, var, show=None, width=32):
        lbl = ttk.Label(parent)
        self.reg(lbl, key)
        lbl.grid(row=row, column=0, sticky="w", pady=4, padx=(0, 10))
        ent = ttk.Entry(parent, textvariable=var, width=width)
        if show:
            ent.configure(show=show)
        ent.grid(row=row, column=1, sticky="we", pady=4)
        parent.columnconfigure(1, weight=1)
        return ent

    def _build_tab_text(self, f):
        lbl = ttk.Label(f)
        self.reg(lbl, "lbl_content")
        lbl.grid(row=0, column=0, sticky="nw", pady=(0, 4))
        self.txt_content = tk.Text(f, height=12, width=44, wrap="word",
                                   relief="solid", borderwidth=1,
                                   font=("Consolas", 10))
        self.txt_content.grid(row=1, column=0, sticky="nsew")
        f.rowconfigure(1, weight=1)
        f.columnconfigure(0, weight=1)

    def _build_tab_wifi(self, f):
        self._field(f, 0, "lbl_ssid", self.v_ssid)
        self._field(f, 1, "lbl_password", self.v_pass, show="•")

        lbl = ttk.Label(f)
        self.reg(lbl, "lbl_encryption")
        lbl.grid(row=2, column=0, sticky="w", pady=4, padx=(0, 10))

        # FIX: populate values at creation time so .current(1) is valid
        self.enc_combo = ttk.Combobox(
            f, state="readonly", width=29,
            values=[self.T("enc_none"), self.T("enc_wpa"), self.T("enc_wep")])
        self.enc_combo.grid(row=2, column=1, sticky="w", pady=4)
        self.enc_combo.current(1)  # default = WPA/WPA2

        chk = ttk.Checkbutton(f, variable=self.v_hidden)
        self.reg(chk, "lbl_hidden")
        chk.grid(row=3, column=1, sticky="w", pady=(8, 0))

    def _build_tab_vcard(self, f):
        rows = [
            ("lbl_first", self.v_first), ("lbl_last", self.v_last),
            ("lbl_org", self.v_org), ("lbl_jobtitle", self.v_jobtitle),
            ("lbl_phone", self.v_phone), ("lbl_email", self.v_email),
            ("lbl_website", self.v_website), ("lbl_street", self.v_street),
            ("lbl_city", self.v_city), ("lbl_zip", self.v_zip),
            ("lbl_country", self.v_country),
        ]
        for i, (key, var) in enumerate(rows):
            self._field(f, i, key, var)

    def _build_tab_email(self, f):
        self._field(f, 0, "lbl_to", self.v_to)
        self._field(f, 1, "lbl_subject", self.v_subject)
        lbl = ttk.Label(f)
        self.reg(lbl, "lbl_body")
        lbl.grid(row=2, column=0, sticky="nw", pady=(8, 4), padx=(0, 10))
        self.txt_email_body = tk.Text(f, height=8, width=44, wrap="word",
                                      relief="solid", borderwidth=1)
        self.txt_email_body.grid(row=3, column=0, columnspan=2, sticky="nsew")
        f.rowconfigure(3, weight=1)
        f.columnconfigure(0, weight=1)

    def _build_tab_sms(self, f):
        self._field(f, 0, "lbl_number", self.v_number)
        lbl = ttk.Label(f)
        self.reg(lbl, "lbl_message")
        lbl.grid(row=1, column=0, sticky="nw", pady=(8, 4), padx=(0, 10))
        self.txt_sms = tk.Text(f, height=8, width=44, wrap="word",
                               relief="solid", borderwidth=1)
        self.txt_sms.grid(row=2, column=0, columnspan=2, sticky="nsew")
        f.rowconfigure(2, weight=1)
        f.columnconfigure(0, weight=1)

    def _build_tab_phone(self, f):
        self._field(f, 0, "lbl_number", self.v_number)

    def _build_tab_geo(self, f):
        self._field(f, 0, "lbl_lat", self.v_lat)
        self._field(f, 1, "lbl_lon", self.v_lon)

    # ---- design options --------------------------------------------------
    def _grid_pair(self, parent, row, col, key, widget):
        lbl = ttk.Label(parent)
        self.reg(lbl, key)
        lbl.grid(row=row, column=col, sticky="w", padx=(0, 6), pady=4)
        widget.grid(row=row, column=col + 1, sticky="w", padx=(0, 16), pady=4)

    def _color_button(self, parent, var):
        btn = tk.Button(parent, width=8, relief="groove", cursor="hand2",
                        command=lambda: self._pick_color(var, btn))
        try:
            btn.configure(bg=var.get())
        except tk.TclError:
            pass

        def _sync(*_):
            try:
                btn.configure(bg=var.get())
            except tk.TclError:
                pass
        var.trace_add("write", _sync)
        return btn

    def _pick_color(self, var, btn):
        rgb, hexval = colorchooser.askcolor(color=var.get(),
                                            title=self.T("choose_color"))
        if hexval:
            var.set(hexval.upper())

    def _build_options(self, parent):
        frame = ttk.LabelFrame(parent, padding=10)
        self.reg(frame, "options")
        frame.pack(fill="x", pady=(0, 10))

        # Error correction
        self.ec_combo = ttk.Combobox(frame, state="readonly", width=6,
                                     values=["L", "M", "Q", "H"])
        self.ec_combo.current(1)
        self._grid_pair(frame, 0, 0, "opt_ec", self.ec_combo)

        # FIX: populate module-shape values at creation time
        self.style_combo = ttk.Combobox(
            frame, state="readonly", width=14,
            values=[self.T("style_" + k) for k in self.style_keys])
        self.style_combo.current(0)
        self._grid_pair(frame, 0, 2, "opt_style", self.style_combo)

        # Module size
        box_spin = ttk.Spinbox(frame, from_=1, to=60, width=6,
                               textvariable=self.v_box)
        self._grid_pair(frame, 1, 0, "opt_box", box_spin)

        # FIX: populate color-mode values at creation time
        self.mask_combo = ttk.Combobox(
            frame, state="readonly", width=14,
            values=[self.T("mask_" + k) for k in self.mask_keys])
        self.mask_combo.current(0)
        self._grid_pair(frame, 1, 2, "opt_mask", self.mask_combo)

        # Border
        border_spin = ttk.Spinbox(frame, from_=0, to=30, width=6,
                                  textvariable=self.v_border)
        self._grid_pair(frame, 2, 0, "opt_border", border_spin)

        # Format
        self.fmt_combo = ttk.Combobox(frame, state="readonly", width=14,
                                      values=["PNG", "JPG", "SVG"])
        self.fmt_combo.current(0)
        self._grid_pair(frame, 2, 2, "fmt", self.fmt_combo)

        # Foreground
        self._grid_pair(frame, 3, 0, "opt_fg", self._color_button(frame, self.v_fg))
        # Background
        self._grid_pair(frame, 3, 2, "opt_bg", self._color_button(frame, self.v_bg))

        # Gradient color
        self._grid_pair(frame, 4, 0, "opt_grad", self._color_button(frame, self.v_grad))

        # Logo size
        logo_spin = ttk.Spinbox(frame, from_=5, to=40, width=6,
                                textvariable=self.v_logosize)
        self._grid_pair(frame, 4, 2, "opt_logosize", logo_spin)

        # Logo chooser
        lbl = ttk.Label(frame)
        self.reg(lbl, "opt_logo")
        lbl.grid(row=5, column=0, sticky="w", padx=(0, 6), pady=4)

        logo_entry = ttk.Entry(frame, textvariable=self.v_logo_display,
                               state="readonly", width=22)
        logo_entry.grid(row=5, column=1, sticky="we", pady=4)

        btn_browse = ttk.Button(frame, command=self.choose_logo, width=9)
        self.reg(btn_browse, "btn_browse")
        btn_browse.grid(row=5, column=2, sticky="w", padx=(6, 4), pady=4)

        btn_rm = ttk.Button(frame, command=self.remove_logo, width=9)
        self.reg(btn_rm, "btn_remove")
        btn_rm.grid(row=5, column=3, sticky="w", pady=4)

        frame.columnconfigure(1, weight=1)

    # ---- preview ---------------------------------------------------------
    def _build_preview(self, parent):
        frame = ttk.LabelFrame(parent, padding=8)
        self.reg(frame, "preview")
        frame.pack(fill="both", expand=True)

        holder = ttk.Frame(frame, width=340, height=340)
        holder.pack_propagate(False)
        holder.pack()

        self.preview_label = ttk.Label(holder, anchor="center")
        self.preview_label.pack(fill="both", expand=True)

    # -------------------------------------------------------------- i18n UI
    def _on_lang_change(self, _event=None):
        self.lang = LANG_ORDER[self.lang_combo.current()]
        self.retranslate()

    def retranslate(self):
        self.root.title(self.T("app_title"))
        for widget, key, attr in self._tr_widgets:
            try:
                widget.configure(**{attr: self.T(key)})
            except tk.TclError:
                pass

        for i, key in enumerate(self.tab_keys):
            self.notebook.tab(i, text=self.T("tab_" + key))

        # Re-populate comboboxes with translated labels, preserving selection
        cur_enc = self.enc_combo.current()
        self.enc_combo.configure(values=[self.T("enc_none"),
                                         self.T("enc_wpa"),
                                         self.T("enc_wep")])
        if cur_enc >= 0:
            self.enc_combo.current(cur_enc)

        cur_style = self.style_combo.current()
        self.style_combo.configure(
            values=[self.T("style_" + k) for k in self.style_keys])
        if cur_style >= 0:
            self.style_combo.current(cur_style)

        cur_mask = self.mask_combo.current()
        self.mask_combo.configure(
            values=[self.T("mask_" + k) for k in self.mask_keys])
        if cur_mask >= 0:
            self.mask_combo.current(cur_mask)

        if not self.logo_path:
            self.v_logo_display.set(self.T("no_logo"))

        self.status.configure(text=self.T("status_ready"))

    # ------------------------------------------------------------- handlers
    def choose_logo(self):
        path = filedialog.askopenfilename(
            title=self.T("opt_logo"),
            filetypes=[(self.T("logo_files"), "*.png *.jpg *.jpeg *.gif *.bmp"),
                       ("All files", "*.*")])
        if path:
            self.logo_path = path
            self.v_logo_display.set(os.path.basename(path))

    def remove_logo(self):
        self.logo_path = None
        self.v_logo_display.set(self.T("no_logo"))

    # ------------------------------------------------------------- data
    def _collect_data(self):
        idx = self.notebook.index(self.notebook.select())
        key = self.tab_keys[idx]

        if key == "text":
            return self.txt_content.get("1.0", "end").strip()

        if key == "wifi":
            ssid = self.v_ssid.get().strip()
            if not ssid:
                raise ValueError(self.T("msg_empty"))
            enc = self.enc_keys[self.enc_combo.current()]
            t = "nopass" if enc == "n" else enc
            payload = f"WIFI:T:{t};S:{wifi_escape(ssid)};"
            if enc != "n":
                payload += f"P:{wifi_escape(self.v_pass.get())};"
            payload += f"H:{'true' if self.v_hidden.get() else 'false'};;"
            return payload

        if key == "vcard":
            first, last = self.v_first.get().strip(), self.v_last.get().strip()
            if not any([first, last, self.v_phone.get().strip(),
                        self.v_email.get().strip()]):
                raise ValueError(self.T("msg_empty"))
            lines = ["BEGIN:VCARD", "VERSION:3.0",
                     f"N:{vcard_escape(last)};{vcard_escape(first)};;;",
                     f"FN:{vcard_escape((first + ' ' + last).strip())}"]
            for tag, var in (("ORG", self.v_org), ("TITLE", self.v_jobtitle),
                             ("TEL;TYPE=CELL", self.v_phone), ("EMAIL", self.v_email),
                             ("URL", self.v_website)):
                val = var.get().strip()
                if val:
                    lines.append(f"{tag}:{vcard_escape(val)}")
            if any(v.get().strip() for v in (self.v_street, self.v_city,
                                             self.v_zip, self.v_country)):
                lines.append("ADR;TYPE=WORK:;;{};{};;{};{}".format(
                    vcard_escape(self.v_street.get()), vcard_escape(self.v_city.get()),
                    vcard_escape(self.v_zip.get()), vcard_escape(self.v_country.get())))
            lines.append("END:VCARD")
            return "\r\n".join(lines)

        if key == "email":
            to = self.v_to.get().strip()
            if not to:
                raise ValueError(self.T("msg_empty"))
            url = "mailto:" + to
            params = []
            if self.v_subject.get().strip():
                params.append("subject=" + quote(self.v_subject.get().strip()))
            body = self.txt_email_body.get("1.0", "end").strip()
            if body:
                params.append("body=" + quote(body))
            return url + ("?" + "&".join(params) if params else "")

        if key == "sms":
            number = self.v_number.get().strip()
            if not number:
                raise ValueError(self.T("msg_empty"))
            msg = self.txt_sms.get("1.0", "end").strip()
            return f"SMSTO:{number}:{msg}"

        if key == "phone":
            number = self.v_number.get().strip()
            if not number:
                raise ValueError(self.T("msg_empty"))
            return "tel:" + number

        if key == "geo":
            try:
                lat = float(self.v_lat.get().replace(",", "."))
                lon = float(self.v_lon.get().replace(",", "."))
            except ValueError:
                raise ValueError(self.T("msg_empty"))
            return f"geo:{lat},{lon}"

        return ""

    # ------------------------------------------------------------- render
    def _build_qr(self, data):
        ec = self.ec_combo.get() or "M"
        if self.logo_path and ec in ("L", "M"):
            ec = "H"
            self.status.configure(text=self.T("msg_logo_ec"))
        qr = qrcode.QRCode(
            version=None,
            error_correction=EC_MAP[ec],
            box_size=max(1, int(self.v_box.get())),
            border=max(0, int(self.v_border.get())),
        )
        qr.add_data(data)
        qr.make(fit=True)
        return qr

    def _render_pil(self, qr):
        fg_hex = safe_hex(self.v_fg.get(), "#000000")
        bg_hex = safe_hex(self.v_bg.get(), "#FFFFFF")
        grad_hex = safe_hex(self.v_grad.get(), "#3B82F6")
        fg, bg, gc = hex_to_rgb(fg_hex), hex_to_rgb(bg_hex), hex_to_rgb(grad_hex)

        style = self.style_keys[max(0, self.style_combo.current())]
        mask = self.mask_keys[max(0, self.mask_combo.current())]

        if HAS_STYLED and (style != "square" or mask != "solid"):
            drawers = {
                "square": SquareModuleDrawer(),
                "rounded": RoundedModuleDrawer(),
                "circle": CircleModuleDrawer(),
                "gapped": GappedSquareModuleDrawer(),
                "vertical": VerticalBarsDrawer(),
                "horizontal": HorizontalBarsDrawer(),
            }
            if mask == "solid":
                cm = SolidFillColorMask(back_color=bg, front_color=fg)
            elif mask == "radial":
                cm = RadialGradiantColorMask(back_color=bg, center_color=fg, edge_color=gc)
            elif mask == "square":
                cm = SquareGradiantColorMask(back_color=bg, center_color=fg, edge_color=gc)
            elif mask == "h":
                cm = HorizontalGradiantColorMask(back_color=bg, left_color=fg, right_color=gc)
            else:
                cm = VerticalGradiantColorMask(back_color=bg, top_color=fg, bottom_color=gc)
            img = qr.make_image(image_factory=StyledPilImage,
                                module_drawer=drawers[style], color_mask=cm)
        else:
            img = qr.make_image(fill_color=fg_hex, back_color=bg_hex)

        img = img.convert("RGB")
        if self.logo_path and os.path.exists(self.logo_path):
            img = self._add_logo(img)
        return img

    def _add_logo(self, img):
        try:
            logo = Image.open(self.logo_path).convert("RGBA")
        except Exception:
            return img
        qr_w, qr_h = img.size
        target = max(16, int(min(qr_w, qr_h) * int(self.v_logosize.get()) / 100))
        logo.thumbnail((target, target), Image.LANCZOS)

        pad = max(2, target // 12)
        box_w, box_h = logo.width + 2 * pad, logo.height + 2 * pad
        box = Image.new("RGBA", (box_w, box_h), (255, 255, 255, 255))
        pos = ((qr_w - box_w) // 2, (qr_h - box_h) // 2)

        img = img.convert("RGBA")
        img.paste(box, pos, box)
        img.paste(logo, (pos[0] + pad, pos[1] + pad), logo)
        return img.convert("RGB")

    def _render_svg(self, qr):
        fg_hex = safe_hex(self.v_fg.get(), "#000000")
        bg_hex = safe_hex(self.v_bg.get(), "#FFFFFF")
        box = qr.box_size
        matrix = qr.get_matrix()
        dim = len(matrix) * box
        paths = []
        for y, row in enumerate(matrix):
            for x, val in enumerate(row):
                if val:
                    paths.append(f"M{x * box},{y * box}h{box}v{box}h-{box}z")
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{dim}" height="{dim}" '
            f'viewBox="0 0 {dim} {dim}" shape-rendering="crispEdges">\n'
            f'  <rect width="100%" height="100%" fill="{bg_hex}"/>\n'
            f'  <path d="{" ".join(paths)}" fill="{fg_hex}"/>\n'
            f'</svg>\n'
        )

    def _update_preview(self, img):
        preview = img.copy()
        preview.thumbnail((330, 330), Image.LANCZOS)
        self.tk_preview = ImageTk.PhotoImage(preview)
        self.preview_label.configure(image=self.tk_preview)

    # ------------------------------------------------------------- actions
    def generate(self):
        try:
            data = self._collect_data()
        except Exception as exc:
            messagebox.showerror(self.T("err_title"), str(exc))
            return
        if not data:
            messagebox.showwarning(self.T("err_title"), self.T("msg_empty"))
            return
        try:
            qr = self._build_qr(data)
            img = self._render_pil(qr)
        except Exception as exc:
            messagebox.showerror(self.T("err_title"),
                                 self.T("msg_error", err=exc))
            return
        self.current_qr = qr
        self.current_image = img
        self._update_preview(img)
        if self.T("msg_logo_ec") not in self.status.cget("text"):
            self.status.configure(text=self.T("status_ready"))

    def save(self):
        if self.current_image is None or self.current_qr is None:
            self.generate()
            if self.current_image is None:
                return

        fmt = self.fmt_combo.get() or "PNG"
        ext = fmt.lower()
        key = {"PNG": "filetype_png", "JPG": "filetype_jpg",
               "SVG": "filetype_svg"}[fmt]

        path = filedialog.asksaveasfilename(
            title=self.T("save_title"),
            defaultextension="." + ext,
            filetypes=[(self.T(key), "*." + ext), ("All files", "*.*")])
        if not path:
            return

        try:
            if fmt == "SVG":
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(self._render_svg(self.current_qr))
            elif fmt == "JPG":
                self.current_image.convert("RGB").save(path, "JPEG", quality=95)
            else:
                self.current_image.save(path, "PNG")
        except Exception as exc:
            messagebox.showerror(self.T("err_title"),
                                 self.T("msg_error", err=exc))
            return

        messagebox.showinfo(self.T("info_title"),
                            self.T("msg_saved", path=path))

    def clear_current(self):
        idx = self.notebook.index(self.notebook.select())
        key = self.tab_keys[idx]

        if key == "text":
            self.txt_content.delete("1.0", "end")
        elif key == "wifi":
            for v in (self.v_ssid, self.v_pass):
                v.set("")
            self.v_hidden.set(False)
            self.enc_combo.current(1)
        elif key == "vcard":
            for v in (self.v_first, self.v_last, self.v_org, self.v_jobtitle,
                      self.v_phone, self.v_email, self.v_website, self.v_street,
                      self.v_city, self.v_zip, self.v_country):
                v.set("")
        elif key == "email":
            self.v_to.set("")
            self.v_subject.set("")
            self.txt_email_body.delete("1.0", "end")
        elif key == "sms":
            self.v_number.set("")
            self.txt_sms.delete("1.0", "end")
        elif key == "phone":
            self.v_number.set("")
        elif key == "geo":
            self.v_lat.set("")
            self.v_lon.set("")

        self.current_image = None
        self.current_qr = None
        self.preview_label.configure(image="")
        self.status.configure(text=self.T("status_ready"))


# --------------------------------------------------------------------------
def main():
    root = tk.Tk()
    root.geometry("1080x760")
    root.minsize(940, 640)
    app = QRApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()