# -*- coding: utf-8 -*-
"""Creador QR avanzado para Android. Port móvil del programa Tkinter original."""
import os, re
from urllib.parse import quote
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy.uix.popup import Popup
from kivy.core.image import Image as CoreImage
from kivy.utils import platform
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
from PIL import Image

try:
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.moduledrawers.pil import (SquareModuleDrawer, RoundedModuleDrawer,
        CircleModuleDrawer, GappedSquareModuleDrawer, VerticalBarsDrawer, HorizontalBarsDrawer)
    from qrcode.image.styles.colormasks import (SolidFillColorMask, RadialGradiantColorMask,
        SquareGradiantColorMask, HorizontalGradiantColorMask, VerticalGradiantColorMask)
    STYLED = True
except Exception:
    STYLED = False

TABS = ['Texto / URL','Wi-Fi','Contacto','Correo','SMS','Teléfono','Ubicación']
FIELDS = {
 'Texto / URL':[('Contenido','https://ejemplo.com')],
 'Wi-Fi':[('Nombre de red (SSID)',''),('Contraseña','')],
 'Contacto':[('Nombre',''),('Apellido',''),('Organización',''),('Puesto',''),('Teléfono',''),('Correo',''),('Sitio web',''),('Calle',''),('Ciudad',''),('Código postal',''),('País','')],
 'Correo':[('Para',''),('Asunto',''),('Mensaje','')],
 'SMS':[('Número',''),('Mensaje','')],
 'Teléfono':[('Número','')],
 'Ubicación':[('Latitud',''),('Longitud','')]
}
EC={'L':ERROR_CORRECT_L,'M':ERROR_CORRECT_M,'Q':ERROR_CORRECT_Q,'H':ERROR_CORRECT_H}

def esc(s): return (s or '').replace('\\','\\\\').replace(';','\\;').replace(',','\\,').replace('\n','\\n')
def wifi_esc(s): return re.sub(r'([\\;,:\"])',r'\\\1',s or '')
def rgb(h):
    h=(h or '#000000').lstrip('#')
    if len(h)==3: h=''.join(c*2 for c in h)
    try: return tuple(int(h[i:i+2],16) for i in (0,2,4))
    except Exception: return (0,0,0)

class QRMobile(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation='vertical', padding=dp(10), spacing=dp(7), **kw)
        self.inputs={}; self.qr_image=None; self.logo_path=None
        with self.canvas.before:
            Color(.96,.97,.99,1); self.bg=Rectangle(pos=self.pos,size=self.size)
        self.bind(pos=self._bg,size=self._bg)
        self.add_widget(Label(text='CREADOR QR AVANZADO',size_hint_y=None,height=dp(38),bold=True,font_size='20sp',color=(.08,.16,.3,1)))
        self.tabs=Spinner(text=TABS[0],values=TABS,size_hint_y=None,height=dp(48),background_color=(.12,.35,.68,1),color=(1,1,1,1))
        self.tabs.bind(text=self.build_fields); self.add_widget(self.tabs)
        self.form_scroll=ScrollView(size_hint_y=.38)
        self.form=GridLayout(cols=1,spacing=dp(5),size_hint_y=None,padding=dp(4)); self.form.bind(minimum_height=self.form.setter('height'))
        self.form_scroll.add_widget(self.form); self.add_widget(self.form_scroll)
        self.build_fields(self.tabs,TABS[0])
        opts=GridLayout(cols=2,spacing=dp(5),size_hint_y=None,height=dp(164))
        self.ec=Spinner(text='M',values=['L','M','Q','H']); self.shape=Spinner(text='Cuadrado',values=['Cuadrado','Redondeado','Círculo','Con espacio','Barras verticales','Barras horizontales'])
        self.mode=Spinner(text='Sólido',values=['Sólido','Radial','Cuadrado','Horizontal','Vertical'])
        self.fg=TextInput(text='#000000',hint_text='Color QR (#000000)',multiline=False)
        self.bgcolor=TextInput(text='#FFFFFF',hint_text='Color fondo (#FFFFFF)',multiline=False)
        self.grad=TextInput(text='#3B82F6',hint_text='Color degradado',multiline=False)
        for w in (self._pair('Corrección',self.ec),self._pair('Forma',self.shape),self._pair('Color',self.mode),self.fg,self.bgcolor,self.grad): opts.add_widget(w)
        self.add_widget(opts)
        actions=GridLayout(cols=2,spacing=dp(6),size_hint_y=None,height=dp(96))
        for title,fn in [('GENERAR QR',self.generate),('GUARDAR PNG',lambda:self.save('PNG')),('GUARDAR JPG',lambda:self.save('JPG')),('GUARDAR SVG',lambda:self.save('SVG')),('LIMPIAR',self.clear_fields),('USAR LOGO',self.choose_logo)]:
            b=Button(text=title,background_normal='',background_color=(.12,.35,.68,1),color=(1,1,1,1),bold=True); b.bind(on_release=lambda _,f=fn:f()); actions.add_widget(b)
        self.add_widget(actions)
        self.preview=KivyImage(size_hint=(1,.36),allow_stretch=True,keep_ratio=True)
        self.add_widget(self.preview)
        self.status=Label(text='Listo. Selecciona el tipo de QR y captura los datos.',size_hint_y=None,height=dp(30),color=(.12,.2,.3,1),font_size='12sp')
        self.add_widget(self.status)
    def _bg(self,*_): self.bg.pos=self.pos; self.bg.size=self.size
    def _pair(self,label,w):
        box=BoxLayout(spacing=dp(4)); box.add_widget(Label(text=label,size_hint_x=.42,color=(.1,.15,.22,1))); box.add_widget(w); return box
    def build_fields(self,*args):
        tab=self.tabs.text; self.form.clear_widgets(); self.inputs={}
        for label,default in FIELDS[tab]:
            row=BoxLayout(size_hint_y=None,height=dp(44),spacing=dp(5))
            row.add_widget(Label(text=label,size_hint_x=.36,color=(.1,.15,.22,1),font_size='12sp'))
            inp=TextInput(text=default,hint_text=label,multiline=(label in ('Contenido','Mensaje')),size_hint_y=1)
            if label=='Contraseña': inp.password=True
            row.add_widget(inp); self.form.add_widget(row); self.inputs[label]=inp
    def val(self,k): return self.inputs[k].text.strip() if k in self.inputs else ''
    def payload(self):
        t=self.tabs.text
        if t=='Texto / URL': return self.val('Contenido')
        if t=='Wi-Fi':
            s=self.val('Nombre de red (SSID)')
            if not s: raise ValueError('Escribe el nombre de la red Wi-Fi.')
            p=self.val('Contraseña'); return f'WIFI:T:WPA;S:{wifi_esc(s)};P:{wifi_esc(p)};H:false;;'
        if t=='Contacto':
            first,last=self.val('Nombre'),self.val('Apellido')
            if not any([first,last,self.val('Teléfono'),self.val('Correo')]): raise ValueError('Captura al menos nombre, teléfono o correo.')
            lines=['BEGIN:VCARD','VERSION:3.0',f'N:{esc(last)};{esc(first)};;;',f'FN:{esc((first+" "+last).strip())}']
            for tag,key in [('ORG','Organización'),('TITLE','Puesto'),('TEL;TYPE=CELL','Teléfono'),('EMAIL','Correo'),('URL','Sitio web')]:
                if self.val(key): lines.append(f'{tag}:{esc(self.val(key))}')
            if any(self.val(k) for k in ('Calle','Ciudad','Código postal','País')): lines.append(f'ADR;TYPE=WORK:;;{esc(self.val("Calle"))};{esc(self.val("Ciudad"))};;{esc(self.val("Código postal"))};{esc(self.val("País"))}')
            return '\r\n'.join(lines+'END:VCARD'.splitlines())
        if t=='Correo':
            to=self.val('Para')
            if not to: raise ValueError('Escribe el destinatario.')
            args=[]
            if self.val('Asunto'): args.append('subject='+quote(self.val('Asunto')))
            if self.val('Mensaje'): args.append('body='+quote(self.val('Mensaje')))
            return 'mailto:'+to+('?'+'&'.join(args) if args else '')
        if t=='SMS':
            if not self.val('Número'): raise ValueError('Escribe el número.')
            return 'SMSTO:'+self.val('Número')+':'+self.val('Mensaje')
        if t=='Teléfono':
            if not self.val('Número'): raise ValueError('Escribe el número.')
            return 'tel:'+self.val('Número')
        if t=='Ubicación':
            try: lat=float(self.val('Latitud').replace(',','.')); lon=float(self.val('Longitud').replace(',','.'))
            except Exception: raise ValueError('Captura latitud y longitud válidas.')
            if not -90<=lat<=90 or not -180<=lon<=180: raise ValueError('Latitud o longitud fuera de rango.')
            return f'geo:{lat},{lon}'
    def generate(self,*_):
        try:
            data=self.payload()
            if not data: raise ValueError('Introduce contenido antes de generar.')
            ec=self.ec.text
            if self.logo_path and ec in ('L','M'): ec='H'; self.status.text='Corrección elevada a H por usar logotipo.'
            qr=qrcode.QRCode(error_correction=EC[ec],box_size=10,border=4); qr.add_data(data); qr.make(fit=True)
            fg,bg,gc=rgb(self.fg.text),rgb(self.bgcolor.text),rgb(self.grad.text)
            styles={'Cuadrado':SquareModuleDrawer,'Redondeado':RoundedModuleDrawer,'Círculo':CircleModuleDrawer,'Con espacio':GappedSquareModuleDrawer,'Barras verticales':VerticalBarsDrawer,'Barras horizontales':HorizontalBarsDrawer}
            masks={'Sólido':lambda:SolidFillColorMask(back_color=bg,front_color=fg),'Radial':lambda:RadialGradiantColorMask(back_color=bg,center_color=fg,edge_color=gc),'Cuadrado':lambda:SquareGradiantColorMask(back_color=bg,center_color=fg,edge_color=gc),'Horizontal':lambda:HorizontalGradiantColorMask(back_color=bg,left_color=fg,right_color=gc),'Vertical':lambda:VerticalGradiantColorMask(back_color=bg,top_color=fg,bottom_color=gc)}
            if STYLED:
                img=qr.make_image(image_factory=StyledPilImage,module_drawer=styles[self.shape.text](),color_mask=masks[self.mode.text]()).convert('RGB')
            else: img=qr.make_image(fill_color=fg,back_color=bg).convert('RGB')
            if self.logo_path:
                logo=Image.open(self.logo_path).convert('RGBA'); target=max(16,int(min(img.size)*.20)); logo.thumbnail((target,target))
                pad=max(2,target//12); plate=Image.new('RGBA',(logo.width+pad*2,logo.height+pad*2),'white'); plate.alpha_composite(logo,(pad,pad)); img=img.convert('RGBA'); img.alpha_composite(plate,((img.width-plate.width)//2,(img.height-plate.height)//2)); img=img.convert('RGB')
            self.qr_image=img; preview=img.copy(); preview.thumbnail((560,560)); path=os.path.join(App.get_running_app().user_data_dir,'qr_preview.png'); preview.save(path); self.preview.source=path; self.preview.reload(); self.status.text='Código QR generado correctamente.'
        except Exception as e: self.alert('No se pudo generar',str(e))
    def save(self,fmt):
        if self.qr_image is None: self.generate()
        if self.qr_image is None: return
        app=App.get_running_app(); name='codigo_qr.'+fmt.lower(); path=os.path.join(app.user_data_dir,name)
        try:
            if fmt=='SVG':
                # SVG vectorial compatible con lectores QR; conserva el contenido codificado.
                qr=qrcode.QRCode(error_correction=EC[self.ec.text],box_size=10,border=4); qr.add_data(self.payload()); qr.make(fit=True)
                matrix=qr.get_matrix(); n=len(matrix); cells=''.join(f'<rect x="{x}" y="{y}" width="1" height="1"/>' for y,row in enumerate(matrix) for x,v in enumerate(row) if v)
                with open(path,'w',encoding='utf-8') as f: f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" shape-rendering="crispEdges"><rect width="100%" height="100%" fill="{self.bgcolor.text}"/><g fill="{self.fg.text}">{cells}</g></svg>')
            elif fmt=='JPG': self.qr_image.convert('RGB').save(path,'JPEG',quality=95)
            else: self.qr_image.save(path,'PNG')
            self.status.text='Guardado en: '+path; self.alert('Archivo guardado','Se guardó en el almacenamiento privado de la app:\n'+path+'\n\nPuedes encontrarlo desde el administrador de archivos de la aplicación o compartirlo desde el menú de Android si está habilitado.')
        except Exception as e: self.alert('Error al guardar',str(e))
    def choose_logo(self): self.alert('Logotipo','En esta primera compilación Android, coloca el archivo de imagen en la carpeta de datos de la app y configura logo_path. El selector SAF se añadirá en la siguiente iteración.')
    def clear_fields(self):
        for w in self.inputs.values(): w.text=''
        self.qr_image=None; self.preview.source=''; self.status.text='Campos limpiados.'
    def alert(self,title,msg): Popup(title=title,content=Label(text=msg),size_hint=(.88,.42)).open()

class QRAppAndroid(App):
    title='Creador QR Avanzado'
    def build(self): return QRMobile()

if __name__=='__main__': QRAppAndroid().run()
