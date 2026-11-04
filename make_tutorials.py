# -*- coding: utf-8 -*-
"""
Regenera los tutoriales PDF del Plan de Mejora V2026 replicando el diseno
original (pagina 540 x 765.12 pt, fondo #f5f7fc, titulos #1e3a8a, acentos
#2563eb, paneles #e2e8f0, recuadros #dce6f5) y aplicando las correcciones
detectadas al contrastarlos con la aplicacion index.html.
"""
import os
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont as RLTTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (BaseDocTemplate, Frame, Flowable, PageBreak,
                                PageTemplate, Paragraph, Spacer)
from reportlab.lib.utils import simpleSplit

W, H = 540.0, 765.12
MARGIN_X = 48.0
CONTENT_W = W - 2 * MARGIN_X          # 444

BG = '#f5f7fc'
INK = '#1f2937'
NAVY = '#1e3a8a'
BLUE = '#2563eb'
GRAY = '#64748b'
PAGENUM = '#8c949e'
PANEL_BG = '#e2e8f0'
CALLOUT_BG = '#dce6f5'

FONT, FONT_BOLD = 'Helvetica', 'Helvetica-Bold'


def _register_fonts():
    """Incrusta Arial (metricamente identica a la Liberation Sans original)
    cuando esta disponible en el sistema; si no, usa Helvetica (base 14)."""
    global FONT, FONT_BOLD
    regular = 'C:/Windows/Fonts/arial.ttf'
    bold = 'C:/Windows/Fonts/arialbd.ttf'
    try:
        if os.path.exists(regular) and os.path.exists(bold):
            pdfmetrics.registerFont(RLTTFont('AppSans', regular))
            pdfmetrics.registerFont(RLTTFont('AppSans-Bold', bold))
            registerFontFamily('AppSans', normal='AppSans', bold='AppSans-Bold',
                               italic='AppSans', boldItalic='AppSans-Bold')
            FONT, FONT_BOLD = 'AppSans', 'AppSans-Bold'
    except Exception:
        FONT, FONT_BOLD = 'Helvetica', 'Helvetica-Bold'


_register_fonts()

URL = 'HTTPS://IESVILLADIEGO.GITHUB.IO/PLANDEMEJORAV2/'
SCHOOL = 'IES VIRGEN DE VILLADIEGO · PEÑAFLOR'


def md(text, bold_color=NAVY):
    """Convierte **negrita** en marcado de reportlab (negrita + color)."""
    out = []
    bold = False
    for chunk in text.split('**'):
        if bold:
            out.append('<b><font color="%s">%s</font></b>' % (bold_color, chunk))
        else:
            out.append(chunk)
        bold = not bold
    return ''.join(out)


def esc(t):
    return (t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


class TwoPanels(Flowable):
    """Dos paneles lado a lado con barra azul, titulo y vinetas."""

    def __init__(self, left, right, width=CONTENT_W):
        Flowable.__init__(self)
        self.width = width
        self.left = left      # (titulo, [items])
        self.right = right
        self.colw = (width - 8) / 2.0
        self.textw = self.colw - 28 - 10

    def _col_height(self, col):
        h = 34.0
        for it in col[1]:
            n = len(simpleSplit(it, FONT, 10.1, self.textw))
            h += n * 16 + 4
        return h - 4 + 13   # sin el ultimo hueco, mas relleno inferior

    def wrap(self, aw, ah):
        self.height = max(self._col_height(self.left), self._col_height(self.right))
        return self.width, self.height

    def draw(self):
        c = self.canv
        for i, col in enumerate((self.left, self.right)):
            x = 0 if i == 0 else self.colw + 8
            h = self.height
            c.setFillColor(HexColor(PANEL_BG))
            c.roundRect(x, 0, self.colw, h, 4, stroke=0, fill=1)
            c.setFillColor(HexColor(BLUE))
            c.rect(x, 0, 3, h, stroke=0, fill=1)
            # titulo
            c.setFillColor(HexColor(NAVY))
            c.setFont(FONT_BOLD, 10.5)
            c.drawString(x + 15, h - 13 - 8.4, col[0])
            # vinetas
            c.setFillColor(HexColor(INK))
            c.setFont(FONT, 10.1)
            top = h - 34
            for it in col[1]:
                lines = simpleSplit(it, FONT, 10.1, self.textw)
                c.setFillColor(HexColor(INK))
                c.rect(x + 17, top - 5.6, 3, 3, stroke=0, fill=1)
                for ln in lines:
                    c.drawString(x + 28, top - 7.6, ln)
                    top -= 16
                top -= 4


class Callout(Flowable):
    """Recuadro destacado con barra oscura, titulo y cuerpo justificado."""

    def __init__(self, title, body, width=CONTENT_W):
        Flowable.__init__(self)
        self.width = width
        self.title = title
        self.body = body
        self.textw = width - 16 - 8

    def _build(self):
        style = ParagraphStyle('callout', fontName=FONT, fontSize=10.1,
                               leading=16, textColor=HexColor(INK),
                               alignment=TA_JUSTIFY)
        self.par = Paragraph(md(self.body), style)
        self.par.wrap(self.textw, 10000)
        self.height = 13 + 12 + 6 + self.par.height + 13

    def wrap(self, aw, ah):
        self._build()
        return self.width, self.height

    def draw(self):
        c = self.canv
        h = self.height
        c.setFillColor(HexColor(CALLOUT_BG))
        c.roundRect(0, 0, self.width, h, 4, stroke=0, fill=1)
        c.setFillColor(HexColor(NAVY))
        c.rect(0, 0, 2.4, h, stroke=0, fill=1)
        c.setFillColor(HexColor(NAVY))
        c.setFont(FONT_BOLD, 9.4)
        c.drawString(16, h - 13 - 7.6, self.title)
        self.par.drawOn(c, 16, h - 13 - 12 - 6 - self.par.height)


BODY = ParagraphStyle('body', fontName=FONT, fontSize=11.2, leading=18,
                      textColor=HexColor(INK), alignment=TA_JUSTIFY,
                      spaceAfter=9)
CHAP_LABEL = ParagraphStyle('label', fontName=FONT_BOLD, fontSize=8.2,
                            leading=10, textColor=HexColor(BLUE), spaceBefore=24,
                            spaceAfter=1)
CHAP_TITLE = ParagraphStyle('ctitle', fontName=FONT_BOLD, fontSize=18.8,
                            leading=21, textColor=HexColor(NAVY), spaceBefore=2,
                            spaceAfter=12)


def story_for(doc_spec):
    story = [PageBreak()]           # portada dibujada en el canvas
    for i, ch in enumerate(doc_spec['chapters'], start=1):
        label = 'C A P Í T U L O  %d' % i
        if i == 1:
            CHAP_LABEL.spaceBefore = 0
        else:
            CHAP_LABEL.spaceBefore = 24
        story.append(Paragraph(label, CHAP_LABEL))
        story.append(Paragraph(ch['title'], CHAP_TITLE))
        for block in ch['blocks']:
            kind = block[0]
            if kind == 'p':
                story.append(Paragraph(md(esc(block[1])), BODY))
            elif kind == 'panels':
                story.append(TwoPanels(block[1], block[2]))
                story.append(Spacer(1, 12))
            elif kind == 'callout':
                story.append(Callout(block[1], esc(block[2])))
                story.append(Spacer(1, 10))
    return story


def draw_cover(c, spec):
    c.setFillColor(HexColor(BG))
    c.rect(0, 0, W, H, stroke=0, fill=1)
    # circulo decorativo (derecha)
    c.setFillColor(HexColor(CALLOUT_BG))
    c.ellipse(285, H - 330, 510, H - 105, stroke=0, fill=1)
    # pildora del rotulo
    badge = 'T U T O R I A L  P O R  P E R F I L'
    size = 9.0
    text_w = stringWidth(badge, FONT_BOLD, size)
    pill_x, pill_h = 48, 28
    pill_w = max(160.0, text_w + 26)
    pill_top = 232
    c.setFillColor(HexColor(CALLOUT_BG))
    c.roundRect(pill_x, H - pill_top - pill_h, pill_w, pill_h, 6, stroke=0, fill=1)
    c.setFillColor(HexColor(NAVY))
    c.setFont(FONT_BOLD, size)
    c.drawString(pill_x + (pill_w - text_w) / 2.0, H - pill_top - pill_h + (pill_h - size) / 2.0 + 1.5, badge)
    # titulo
    c.setFillColor(HexColor(NAVY))
    c.setFont(FONT_BOLD, 42)
    c.drawString(48, H - 308, 'Plan de Mejora')
    c.drawString(48, H - 353, 'V2026')
    # subtitulo
    c.setFillColor(HexColor(BLUE))
    c.setFont(FONT_BOLD, 18.8)
    c.drawString(48, H - 393.5, spec['subtitle'])
    # linea separadora
    c.setFillColor(HexColor(BLUE))
    c.rect(48, H - 442, 66, 4, stroke=0, fill=1)
    # texto de introduccion
    c.setFillColor(HexColor(INK))
    c.setFont(FONT, 11.2)
    y = H - 486.7
    for ln in simpleSplit(spec['intro'], FONT, 11.2, 398):
        c.drawString(48, y, ln)
        y -= 19.5
    # cabecera y pie
    c.setFillColor(HexColor(GRAY))
    c.setFont(FONT, 9)
    c.drawRightString(492, H - 53, SCHOOL)
    c.drawString(48, H - 715, 'CURSO 2026-2027   APLICACIÓN ' + URL)


def build(spec, path):
    def on_page(c, doc):
        c.setFillColor(HexColor(BG))
        c.rect(0, 0, W, H, stroke=0, fill=1)
        if doc.page == 1:
            draw_cover(c, spec)
        else:
            c.setFillColor(HexColor(PAGENUM))
            c.setFont(FONT, 10)
            c.drawCentredString(W / 2.0, 24, str(doc.page - 1))

    doc = BaseDocTemplate(path, pagesize=(W, H),
                          leftMargin=MARGIN_X, rightMargin=MARGIN_X,
                          topMargin=45, bottomMargin=52,
                          title=spec['meta_title'], author='IES Virgen de Villadiego',
                          subject=spec['meta_subject'], creator='IES Virgen de Villadiego')
    frame = Frame(MARGIN_X, 52, CONTENT_W, H - 45 - 52, id='f',
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id='main', frames=[frame], onPage=on_page)])
    doc.build(story_for(spec))


# ---------------------------------------------------------------------------
# Contenido: ADMIN (con las correcciones aplicadas)
# ---------------------------------------------------------------------------

ADMIN = {
    'meta_title': 'Tutorial Plan de Mejora V2026 — perfil Admin',
    'meta_subject': 'Tutorial de la app Plan de Mejora V2026 para el perfil Admin',
    'subtitle': 'Perfil Admin · Administración completa',
    'intro': ('Para la dirección: todo lo de FOREVIN y además gestión de usuarios y '
              'contraseñas, bloqueos de edición, cursos (añadir, copiar, eliminar) y borrado '
              'general del curso.'),
    'chapters': [
        {'title': 'Tu perfil: Admin', 'blocks': [
            ('p', 'El perfil **Admin** es el de más privilegios: además de todo lo que hacen '
                  'FOREVIN y Usuario, tienes la **administración completa de la app**: usuarios y '
                  'contraseñas, bloqueos de edición, gestión de cursos y herramientas de '
                  'recuperación. Es el perfil de la dirección del centro o de quien responda por '
                  'la app.'),
            ('panels',
             ('Todo lo de FOREVIN', [
                 'Consultar, filtrar, informes PDF',
                 'Editar estados, indicadores y actuaciones',
                 'Exportar / importar datos']),
             ('Además, solo Admin', [
                 'Gestionar usuarios: crear, editar, eliminar, perfiles',
                 'Bloquear la edición (general e indicador a indicador)',
                 'Añadir/eliminar cursos y copiar al próximo curso',
                 'Borrar todos los indicadores y guardar a mano'])),
        ]},
        {'title': 'La pantalla principal', 'blocks': [
            ('p', 'Al entrar verás el banner del título: **PLAN DE MEJORA V2026** con el curso '
                  'escolar debajo. En esa misma línea, bajo el curso, están el **chip de versión** '
                  'de la aplicación y el enlace **Tutorial en PDF**, que descarga esta misma guía. '
                  'Debajo del banner va la fila de sesión, alineada a la derecha: el botón '
                  '**Guardar** (solo Admin), el estado del último guardado, el **chip del usuario '
                  'activo** y el botón **Cerrar sesión**, siempre juntos a la derecha.'),
            ('p', 'Los 51 indicadores del curso están agrupados por ámbitos. Cada ámbito es un '
                  'acordeón: un clic lo despliega y otro lo recoge, y solo puede haber uno abierto '
                  'a la vez. Cada ámbito lleva el check **«Mostrar indicadores sin propuestas»**: '
                  'desmarcado, el ámbito enseña solo sus indicadores con propuesta de mejora '
                  'redactada; marcado, enseña todos. Es independiente por ámbito y se conserva al '
                  'filtrar.'),
            ('p', 'Los paneles de gestión están agrupados bajo la barra **GESTIÓN**: Configuración, '
                  'Generar Informes PDF, Filtros y Añadir Nuevo Indicador (este último, solo para '
                  'perfiles que editan). Un clic en la barra la despliega y otro la recoge; dentro '
                  'solo puede haber un panel abierto a la vez. Todo llega recogido al entrar en la '
                  'app.'),
        ]},
        {'title': 'Consultar el plan y filtrar', 'blocks': [
            ('p', 'Despliega un ámbito y verás sus indicadores en fichas: cada uno muestra su '
                  'descripción, su estado (No iniciado, En proceso o Conseguido), el valor '
                  'objetivo, la propuesta de mejora, la memoria y sus actuaciones vinculadas con '
                  'la temporalización, los responsables, el logro, la justificación y las '
                  'dificultades. El foco del teclado salta al primer indicador del ámbito al '
                  'abrirlo.'),
            ('p', 'El panel **Filtros** (en GESTIÓN) acota la vista por ámbito, por proceso, por '
                  'responsable o por estado. Los filtros se combinan entre sí y con el check del '
                  'ámbito. El panel **Generar Informes PDF** produce dos informes: **por Estado** '
                  '(marcas qué estados entran: no iniciadas, en proceso, conseguidas) y **por '
                  'Responsable** (eligiendo un responsable concreto o todos). Los PDF se generan '
                  'en el navegador y se titulan «IES VIRGEN DE VILLADIEGO - PLAN DE MEJORA V2026».'),
            ('callout', 'SIN CONEXIÓN',
             'La app es una PWA: una vez cargada, arranca desde caché aunque no haya red, y puede '
             'instalarse en el escritorio o en el móvil desde el navegador. Los datos viven en la '
             'nube (Firestore): sin conexión se pueden consultar y generar informes, y los cambios '
             'se guardan en cuanto vuelve la conexión.'),
        ]},
        {'title': 'Cambiar el estado de un indicador', 'blocks': [
            ('p', 'Cada indicador trae en su ficha un selector con tres estados: **No iniciado**, '
                  '**En proceso** y **Conseguido**. Marca una opción y el cambio se aplica al '
                  'momento; si el indicador pasa a **Conseguido**, la app anota la fecha de '
                  'consecución automáticamente (la primera vez), y si vuelve a otro estado, esa '
                  'fecha se retira.'),
            ('p', 'Al marcar «En proceso» o «Conseguido» desde la ficha, la app abre el **modal de '
                  'revisión de actuaciones**: pide revisar las actuaciones vinculadas al nuevo '
                  'estado. Ahí se ajustan sus estados, justificaciones y dificultades, e incluso el '
                  'estado del propio indicador. La regla es que **al menos una actuación quede con '
                  'el mismo estado que el indicador**; si no, al Guardar avisa y el modal sigue '
                  'abierto. «Cancelar» descarta lo editado en el modal (el cambio de la ficha ya '
                  'quedó hecho). Sin actuaciones vinculadas no hay modal.'),
        ]},
        {'title': 'Editar un indicador completo', 'blocks': [
            ('p', 'El botón **Editar** de la ficha abre el modal de edición completa. En la **parte '
                  'superior**, encima de la descripción, está el **selector de estado del '
                  'indicador** (visible si ya está En proceso o Conseguido): marcar «No iniciado» '
                  'oculta en el acto las actuaciones vinculadas y marcar otro estado las muestra '
                  'de nuevo; al Guardar se aplica la regla de la fecha de consecución.'),
            ('p', 'El resto del modal: descripción, valor objetivo, propuesta de mejora, memoria, '
                  'fecha de inclusión y las **actuaciones vinculadas** (temporalización, '
                  'responsables, estado, logro, justificación, dificultades). Con el indicador en '
                  '«No iniciada» el modal oculta las actuaciones existentes, aunque seguirás '
                  'pudiendo añadir alguna nueva: sus valores se conservan intactos al Guardar.'),
            ('p', 'El botón **Eliminar** de la ficha pide confirmación y borra el indicador; no se '
                  'puede deshacer. Los cambios de cualquier edición se guardan solos: hay un '
                  'auto-guardado cada 3 minutos y la app avisa al cerrar sesión si queda algo sin '
                  'guardar.'),
        ]},
        {'title': 'Gestión de usuarios', 'blocks': [
            ('p', 'En Configuración (GESTIÓN), el panel **Gestión de usuarios** (solo Admin) lista '
                  'a todos con su perfil. Desde ahí se crean usuarios nuevos (usuario, nombre para '
                  'mostrar, contraseña y perfil), se editan —cambiar nombre, restablecer contraseña '
                  'o cambiar de perfil— y se eliminan. El perfil se elige de tres opciones: '
                  '**Usuario** (solo lectura), **FOREVIN** (edición del plan) y **Admin** (como el '
                  'tuyo).'),
            ('p', 'Conviene que exista más de un Admin: si el único olvida la contraseña, nadie '
                  'puede entrar a gestionar. El botón **Guardar** de la cabecera fuerza el guardado '
                  'en ese instante; el estado del último guardado se ve al lado.'),
        ]},
        {'title': 'Bloqueos y cursos', 'blocks': [
            ('p', 'El panel **Bloqueo de edición** congela total o parcialmente la edición del '
                  'plan: se puede bloquear todo, solo la edición de lo existente, solo los añadidos '
                  'o nada. Además hay bloqueos individuales por indicador (el candado en la ficha) '
                  'para cerrar acuerdos ya revisados. El bloqueo «solo usuarios» no afecta al '
                  'Admin; el de «para todos» sí le afecta, y los candados individuales también le '
                  'impiden editar, aunque él mismo puede quitarlos.'),
            ('p', 'En **Gestión de cursos** se administra la vida del plan: **+ Añadir** crea el '
                  'curso siguiente (2027-2028) y **Cargar indicadores a Plan de Mejora del próximo '
                  'curso** copia los indicadores del curso actual como punto de partida. '
                  '**Eliminar** solo acepta cursos futuros (que aún no hayan empezado); el curso en '
                  'vigor y los vencidos se protegen y el botón explica el motivo. **Borrar todos '
                  'los indicadores del curso** (no disponible en 2026-2027) vacía el curso actual '
                  'con confirmación doble.'),
            ('callout', 'CUIDADO CON EL BORRADO',
             'Borrar todos los indicadores del curso es la acción más destructiva de la app: se '
             'confirma por duplicado y conviene exportar antes. El botón Eliminar de cada ficha '
             'también es definitivo.'),
        ]},
    ],
}

# ---------------------------------------------------------------------------
# Contenido: USUARIO (con las correcciones aplicadas)
# ---------------------------------------------------------------------------

USUARIO = {
    'meta_title': 'Tutorial Plan de Mejora V2026 — perfil Usuario',
    'meta_subject': 'Tutorial de la app Plan de Mejora V2026 para el perfil Usuario',
    'subtitle': 'Perfil Usuario · Consulta y seguimiento del plan',
    'intro': ('Para el claustro: ver el plan completo, filtrar y generar los informes PDF '
              'oficiales, sin opción de modificar nada. Los selectores de estado llegan '
              'deshabilitados y las fichas no traen botones de edición.'),
    'chapters': [
        {'title': 'Tu perfil: Usuario', 'blocks': [
            ('p', 'El perfil **Usuario** es el de menos privilegios: está pensado para el claustro '
                  'y para cualquiera que necesite **consultar** el Plan de Mejora sin alterarlo. '
                  'Puedes ver todos los ámbitos, indicadores y actuaciones del curso con todos sus '
                  'detalles, filtrar la información y generar los informes PDF oficiales. A cambio, '
                  'la app no te deja modificar nada: los selectores de estado aparecen '
                  'deshabilitados y las tarjetas no muestran botones de edición ni de borrado.'),
            ('panels',
             ('Puedes', [
                 'Ver el plan completo: ámbitos, indicadores y actuaciones',
                 'Filtrar por ámbito, proceso, responsable y estado',
                 'Generar informes PDF por estado y por responsable',
                 'Instalar la app y trabajar sin conexión']),
             ('No puedes', [
                 'Cambiar el estado de un indicador (viene deshabilitado)',
                 'Editar o eliminar indicadores: sin esos botones',
                 'Añadir indicadores nuevos ni exportar/importar datos',
                 'Gestionar usuarios, cursos o bloqueos (solo Admin)'])),
        ]},
        {'title': 'La pantalla principal', 'blocks': [
            ('p', 'Al entrar verás el banner del título: **PLAN DE MEJORA V2026** con el curso '
                  'escolar debajo. En esa misma línea, bajo el curso, están el **chip de versión** '
                  'de la aplicación y el enlace **Tutorial en PDF**, que descarga esta misma guía. '
                  'Debajo del banner va la fila de sesión, alineada a la derecha: el botón '
                  '**Guardar** (solo Admin), el estado del último guardado, el **chip del usuario '
                  'activo** y el botón **Cerrar sesión**, siempre juntos a la derecha.'),
            ('p', 'Los 51 indicadores del curso están agrupados por ámbitos. Cada ámbito es un '
                  'acordeón: un clic lo despliega y otro lo recoge, y solo puede haber uno abierto '
                  'a la vez. Cada ámbito lleva el check **«Mostrar indicadores sin propuestas»**: '
                  'desmarcado, el ámbito enseña solo sus indicadores con propuesta de mejora '
                  'redactada; marcado, enseña todos. Es independiente por ámbito y se conserva al '
                  'filtrar.'),
            ('p', 'Los paneles de gestión están agrupados bajo la barra **GESTIÓN**: Configuración, '
                  'Generar Informes PDF, Filtros y Añadir Nuevo Indicador (este último, solo para '
                  'perfiles que editan). Un clic en la barra la despliega y otro la recoge; dentro '
                  'solo puede haber un panel abierto a la vez. Todo llega recogido al entrar en la '
                  'app.'),
        ]},
        {'title': 'Consultar el plan y filtrar', 'blocks': [
            ('p', 'Despliega un ámbito y verás sus indicadores en fichas: cada uno muestra su '
                  'descripción, su estado (No iniciado, En proceso o Conseguido), el valor '
                  'objetivo, la propuesta de mejora, la memoria y sus actuaciones vinculadas con '
                  'la temporalización, los responsables, el logro, la justificación y las '
                  'dificultades. El foco del teclado salta al primer indicador del ámbito al '
                  'abrirlo.'),
            ('p', 'El panel **Filtros** (en GESTIÓN) acota la vista por ámbito, por proceso, por '
                  'responsable o por estado. Los filtros se combinan entre sí y con el check del '
                  'ámbito. El panel **Generar Informes PDF** produce dos informes: **por Estado** '
                  '(marcas qué estados entran: no iniciadas, en proceso, conseguidas) y **por '
                  'Responsable** (eligiendo un responsable concreto o todos). Los PDF se generan '
                  'en el navegador y se titulan «IES VIRGEN DE VILLADIEGO - PLAN DE MEJORA V2026».'),
            ('callout', 'SIN CONEXIÓN',
             'La app es una PWA: una vez cargada, arranca desde caché aunque no haya red, y puede '
             'instalarse en el escritorio o en el móvil desde el navegador. Los datos viven en la '
             'nube (Firestore): sin conexión se pueden consultar y generar informes, y los cambios '
             'se guardan en cuanto vuelve la conexión.'),
        ]},
        {'title': 'Cerrar sesión y preguntas frecuentes', 'blocks': [
            ('p', 'Pulsa **Cerrar sesión** (a la derecha, junto a tu chip de usuario) para salir: '
                  'la app vuelve a la pantalla de identificación. La sesión se mantiene mientras no '
                  'cierres la pestaña del navegador: al recargar la página no tienes que '
                  'identificarte de nuevo. Al cerrar sesión, los acordeones y paneles se recogen y '
                  'el check de cada ámbito vuelve a su valor por defecto.'),
            ('p', 'Si un compañero con perfil de edición cambia algo mientras tú tienes la app '
                  'abierta, tu pantalla se actualiza sola en unos segundos: no hace falta recargar. '
                  'La versión de la app que ves en el chip del banner se lee del service worker; si '
                  'algún día no se puede leer, el chip simplemente no se muestra.'),
            ('callout', 'OLVIDÉ LA CONTRASEÑA',
             'Las contraseñas las gestiona el administrador del centro desde el panel de gestión de '
             'usuarios: pídele que la restablezca. También es el administrador quien te cambia de '
             'perfil si en el futuro necesitas editar el plan.'),
        ]},
    ],
}


if __name__ == '__main__':
    build(ADMIN, 'Tutorial_PlanDeMejora_Admin.pdf')
    build(USUARIO, 'Tutorial_PlanDeMejora_Usuario.pdf')
    print('PDFs regenerados')
