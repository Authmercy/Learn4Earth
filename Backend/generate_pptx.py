"""
Generateur de presentation PowerPoint pour le projet EcoLearn AI.
Execute avec : python3 generate_pptx.py
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ── Couleurs du theme ──
GREEN_DARK = RGBColor(0x1B, 0x5E, 0x20)    # #1B5E20
GREEN_MID = RGBColor(0x2E, 0x7D, 0x32)     # #2E7D32
GREEN_LIGHT = RGBColor(0x4C, 0xAF, 0x50)   # #4CAF50
GREEN_PALE = RGBColor(0xE8, 0xF5, 0xE9)    # #E8F5E9
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x21, 0x21, 0x21)          # #212121
GRAY = RGBColor(0x61, 0x61, 0x61)           # #616161
GRAY_LIGHT = RGBColor(0x9E, 0x9E, 0x9E)
BLUE = RGBColor(0x15, 0x65, 0xC0)           # #1565C0
ORANGE = RGBColor(0xE6, 0x51, 0x00)         # #E65100
RED = RGBColor(0xC6, 0x28, 0x28)            # #C62828

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


# ══════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════

def add_bg(slide, color):
    """Remplir l'arriere-plan d'une slide."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(slide, left, top, width, height, color, alpha=None):
    """Ajouter un rectangle colore."""
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    if alpha is not None:
        shape.fill.fore_color.brightness = alpha
    return shape


def add_text_box(slide, left, top, width, height, text, font_size=18, color=BLACK, bold=False, alignment=PP_ALIGN.LEFT, font_name="Calibri"):
    """Ajouter une boite de texte."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = alignment
    return txBox


def add_bullet_list(slide, left, top, width, height, items, font_size=16, color=BLACK, title=None, title_size=22, title_color=GREEN_DARK):
    """Ajouter une liste a puces avec titre optionnel."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True

    if title:
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(title_size)
        p.font.color.rgb = title_color
        p.font.bold = True
        p.font.name = "Calibri"
        p.space_after = Pt(12)

    for i, item in enumerate(items):
        if title or i > 0:
            p = tf.add_paragraph()
        else:
            p = tf.paragraphs[0]
        p.text = item
        p.font.size = Pt(font_size)
        p.font.color.rgb = color
        p.font.name = "Calibri"
        p.space_before = Pt(6)
        p.space_after = Pt(4)
        p.level = 0

    return txBox


def add_card(slide, left, top, width, height, title, body_lines, icon="", title_color=GREEN_DARK, bg_color=WHITE):
    """Ajouter une carte avec titre, icone et contenu."""
    # Fond de carte
    rect = add_rect(slide, left, top, width, height, bg_color)
    rect.shadow.inherit = False

    # Titre de carte
    y_offset = top + Inches(0.15)
    card_title = icon + " " + title if icon else title
    add_text_box(slide, left + Inches(0.2), y_offset, width - Inches(0.4), Inches(0.45),
                 card_title, font_size=16, color=title_color, bold=True)

    # Contenu
    y_offset += Inches(0.5)
    for line in body_lines:
        add_text_box(slide, left + Inches(0.2), y_offset, width - Inches(0.4), Inches(0.3),
                     line, font_size=12, color=GRAY)
        y_offset += Inches(0.28)


def add_section_header(slide, number, title):
    """Ajouter un bandeau de section en haut."""
    add_rect(slide, Inches(0), Inches(0), SLIDE_W, Inches(1.2), GREEN_DARK)
    add_text_box(slide, Inches(0.8), Inches(0.15), Inches(11), Inches(0.5),
                 f"SECTION {number}", font_size=14, color=GREEN_LIGHT, bold=True)
    add_text_box(slide, Inches(0.8), Inches(0.5), Inches(11), Inches(0.6),
                 title, font_size=32, color=WHITE, bold=True)
    # Ligne decorative sous le header
    add_rect(slide, Inches(0), Inches(1.2), SLIDE_W, Inches(0.05), GREEN_LIGHT)


# ══════════════════════════════════════════════════════════
#  SLIDE 1 : COUVERTURE
# ══════════════════════════════════════════════════════════

slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
add_bg(slide, GREEN_DARK)

# Bande decorative
add_rect(slide, Inches(0), Inches(2.8), SLIDE_W, Inches(0.06), GREEN_LIGHT)
add_rect(slide, Inches(0), Inches(4.5), SLIDE_W, Inches(0.06), GREEN_LIGHT)

# Titre principal
add_text_box(slide, Inches(1), Inches(1.2), Inches(11.3), Inches(0.8),
             "ECOLEARNAI", font_size=54, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)

# Sous-titre
add_text_box(slide, Inches(1), Inches(2.1), Inches(11.3), Inches(0.6),
             "Plateforme d'Apprentissage en Ligne Intelligente et Ecologique",
             font_size=24, color=GREEN_LIGHT, alignment=PP_ALIGN.CENTER)

# Description
add_text_box(slide, Inches(2), Inches(3.2), Inches(9.3), Inches(1.2),
             "Parcours adaptatifs generes par IA  |  Gamification et progression  |  "
             "Suivi d'empreinte carbone  |  Paiements securises  |  Conformite RGPD",
             font_size=16, color=WHITE, alignment=PP_ALIGN.CENTER)

# Version et date
add_text_box(slide, Inches(1), Inches(5.0), Inches(11.3), Inches(0.4),
             "Version 1.3.0  -  Fevrier 2026", font_size=16, color=GRAY_LIGHT, alignment=PP_ALIGN.CENTER)

# Technologies
add_text_box(slide, Inches(1), Inches(5.8), Inches(11.3), Inches(0.4),
             "FastAPI  |  Flask  |  MySQL NDB Cluster  |  Redis  |  OpenAI GPT  |  Docker  |  Prometheus  |  Grafana",
             font_size=13, color=GRAY_LIGHT, alignment=PP_ALIGN.CENTER)

# Pied de page
add_text_box(slide, Inches(1), Inches(6.5), Inches(11.3), Inches(0.4),
             "Presente par : Equipe EcoLearn AI", font_size=14, color=GRAY_LIGHT, alignment=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════
#  SLIDE 2 : SOMMAIRE
# ══════════════════════════════════════════════════════════

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_rect(slide, Inches(0), Inches(0), Inches(0.15), SLIDE_H, GREEN_DARK)

add_text_box(slide, Inches(0.8), Inches(0.4), Inches(11), Inches(0.7),
             "SOMMAIRE", font_size=36, color=GREEN_DARK, bold=True)
add_rect(slide, Inches(0.8), Inches(1.1), Inches(3), Inches(0.04), GREEN_LIGHT)

sections = [
    ("01", "Pitch Startup et Demo Live"),
    ("02", "Demo technique : Inscription + IA"),
    ("03", "Demo technique : Paiement + Monitoring"),
    ("04", "Contexte et problematique"),
    ("05", "Vision et objectifs"),
    ("06", "Architecture technique"),
    ("07", "Architecture applicative"),
    ("08", "Schema base de donnees"),
    ("09", "Relations et flux de donnees"),
    ("10", "Fonctionnalites cles"),
    ("11", "Intelligence Artificielle"),
    ("12", "Securite et conformite RGPD"),
    ("13", "Paiements et abonnements"),
    ("14", "Cache Redis et performance"),
    ("15", "Monitoring et observabilite"),
    ("16", "Backup et haute disponibilite"),
    ("17", "Methodologie Agile / DevOps"),
    ("18", "Stack technologique"),
    ("19", "Feuille de route"),
]

col1_x = Inches(1.0)
col2_x = Inches(7.0)
y_start = Inches(1.6)

for i, (num, title) in enumerate(sections):
    col = 0 if i < 10 else 1
    x = col1_x if col == 0 else col2_x
    row = i if col == 0 else i - 10
    y = y_start + Inches(0.50) * row
    add_text_box(slide, x, y, Inches(0.6), Inches(0.38),
                 num, font_size=19, color=GREEN_LIGHT, bold=True)
    add_text_box(slide, x + Inches(0.65), y + Inches(0.03), Inches(4.8), Inches(0.32),
                 title, font_size=15, color=BLACK)


# ══════════════════════════════════════════════════════════
#  SLIDE 3 : PITCH STARTUP + DEMO LIVE (20%)
# ══════════════════════════════════════════════════════════

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_section_header(slide, "01", "Pitch Startup et Demo Live (20%)")

# ── Vision Business (gauche) ──
add_text_box(slide, Inches(0.6), Inches(1.5), Inches(5.8), Inches(0.35),
             "Vision Business", font_size=20, color=GREEN_DARK, bold=True)

# Elevator Pitch
add_rect(slide, Inches(0.6), Inches(2.0), Inches(5.8), Inches(1.4), GREEN_PALE)
add_text_box(slide, Inches(0.8), Inches(2.1), Inches(5.4), Inches(0.35),
             "Elevator Pitch (30 secondes)", font_size=15, color=GREEN_DARK, bold=True)
add_text_box(slide, Inches(0.8), Inches(2.5), Inches(5.4), Inches(0.8),
             "\"EcoLearn AI est une plateforme e-learning qui personnalise\n"
             "chaque cours grace a l'IA, mesure l'impact ecologique du\n"
             "numerique, et securise les donnees selon le RGPD.\n"
             "Notre cible : etudiants et professionnels en Afrique et Europe.\"",
             font_size=12, color=GRAY)

# Proposition de valeur
add_text_box(slide, Inches(0.6), Inches(3.6), Inches(5.8), Inches(0.35),
             "Proposition de valeur unique", font_size=16, color=GREEN_DARK, bold=True)

value_props = [
    ("Personnalisation IA", "Contenu adapte en temps reel par OpenAI GPT"),
    ("Eco-responsable", "Suivi carbone + compensation (plantation d'arbres)"),
    ("Gamification", "XP, niveaux, streaks, badges pour la retention"),
    ("RGPD natif", "Chiffrement AES-128, consentement, droit a l'oubli"),
    ("Paiement Afrique", "Carte Visa/MC (Umoja) + Mobile Money"),
]

for i, (prop, desc) in enumerate(value_props):
    y = Inches(4.05) + Inches(0.42) * i
    bg = GREEN_PALE if i % 2 == 0 else WHITE
    add_rect(slide, Inches(0.6), y, Inches(5.8), Inches(0.38), bg)
    add_text_box(slide, Inches(0.75), y + Inches(0.05), Inches(2.0), Inches(0.28),
                 prop, font_size=12, color=GREEN_DARK, bold=True)
    add_text_box(slide, Inches(2.8), y + Inches(0.05), Inches(3.5), Inches(0.28),
                 desc, font_size=11, color=GRAY)

# ── Demo Live (droite) ──
add_text_box(slide, Inches(7.0), Inches(1.5), Inches(5.8), Inches(0.35),
             "Demonstration technique live", font_size=20, color=GREEN_DARK, bold=True)

demo_steps = [
    ("1", "Inscription RGPD", "Formulaire + OTP SMS/Email", "POST /api/auth/register"),
    ("2", "Verification OTP", "Double canal (SMS + Email)", "POST /api/auth/verify-sms"),
    ("3", "Connexion JWT", "Token 30 min, bcrypt hash", "POST /api/auth/login"),
    ("4", "Creer un parcours", "Sujet, difficulte, sessions", "POST /api/learning/paths"),
    ("5", "Session IA live", "Contenu genere par GPT en direct", "POST /api/learning/sessions"),
    ("6", "Terminer session", "XP + streak + carbone + badges", "PUT /sessions/{id}/complete"),
    ("7", "Dashboard", "Stats, progression, empreinte CO2", "GET /api/dashboard/"),
    ("8", "Paiement carte", "Redirect Umoja -> callback", "POST /api/subscriptions/subscribe"),
    ("9", "Admin KPIs", "Revenus, users, plans", "GET /api/admin/dashboard"),
    ("10", "Monitoring", "Health check, Redis, MySQL", "GET /api/monitoring/health"),
]

for i, (num, step, detail, endpoint) in enumerate(demo_steps):
    y = Inches(2.0) + Inches(0.48) * i
    bg = GREEN_MID if i % 2 == 0 else GREEN_PALE
    text_color = WHITE if i % 2 == 0 else GREEN_DARK
    add_rect(slide, Inches(7.0), y, Inches(5.8), Inches(0.42), bg)
    add_text_box(slide, Inches(7.1), y + Inches(0.06), Inches(0.35), Inches(0.28),
                 num, font_size=11, color=text_color, bold=True)
    add_text_box(slide, Inches(7.5), y + Inches(0.06), Inches(1.6), Inches(0.28),
                 step, font_size=11, color=text_color, bold=True)
    add_text_box(slide, Inches(9.1), y + Inches(0.06), Inches(1.8), Inches(0.28),
                 detail, font_size=9, color=text_color)
    add_text_box(slide, Inches(10.9), y + Inches(0.06), Inches(1.8), Inches(0.28),
                 endpoint, font_size=8, color=text_color)

# URLs de demo
add_rect(slide, Inches(7.0), Inches(6.85), Inches(5.8), Inches(0.45), GREEN_DARK)
add_text_box(slide, Inches(7.2), Inches(6.9), Inches(5.4), Inches(0.35),
             "Swagger : http://206.189.56.166:8000/docs  |  Grafana : :3000  |  Prometheus : :9090",
             font_size=10, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════
#  SLIDE : DEMO TECHNIQUE 1 - Inscription + IA
# ══════════════════════════════════════════════════════════

TERMINAL_BG = RGBColor(0x1E, 0x1E, 0x2E)   # Dark terminal
TERMINAL_GREEN = RGBColor(0x50, 0xFA, 0x7B)  # Terminal green
TERMINAL_YELLOW = RGBColor(0xF1, 0xFA, 0x8C) # Terminal yellow
TERMINAL_CYAN = RGBColor(0x8B, 0xE9, 0xFD)   # Terminal cyan
TERMINAL_PINK = RGBColor(0xFF, 0x79, 0xC6)   # Terminal pink
TERMINAL_WHITE = RGBColor(0xF8, 0xF8, 0xF2)  # Terminal white

def add_terminal(slide, left, top, width, height, title, lines):
    """Ajouter un bloc terminal (fond sombre, texte monospace)."""
    # Barre de titre
    add_rect(slide, left, top, width, Inches(0.32), RGBColor(0x30, 0x30, 0x46))
    add_text_box(slide, left + Inches(0.15), top + Inches(0.03), width - Inches(0.3), Inches(0.25),
                 title, font_size=10, color=TERMINAL_CYAN, bold=True, font_name="Consolas")
    # Corps terminal
    body_top = top + Inches(0.32)
    body_h = height - Inches(0.32)
    add_rect(slide, left, body_top, width, body_h, TERMINAL_BG)
    # Lignes
    for i, (text, color) in enumerate(lines):
        ly = body_top + Inches(0.06) + Inches(0.22) * i
        add_text_box(slide, left + Inches(0.12), ly, width - Inches(0.24), Inches(0.2),
                     text, font_size=8, color=color, font_name="Consolas")

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, RGBColor(0x11, 0x11, 0x1B))

# Header
add_rect(slide, Inches(0), Inches(0), SLIDE_W, Inches(0.9), GREEN_DARK)
add_text_box(slide, Inches(0.6), Inches(0.1), Inches(12), Inches(0.35),
             "DEMO TECHNIQUE", font_size=13, color=GREEN_LIGHT, bold=True)
add_text_box(slide, Inches(0.6), Inches(0.4), Inches(12), Inches(0.4),
             "Inscription RGPD + Generation IA en direct", font_size=26, color=WHITE, bold=True)

# Terminal 1 : Inscription
add_terminal(slide, Inches(0.3), Inches(1.1), Inches(6.3), Inches(3.0),
    "$ curl - POST /api/auth/register", [
        ('$ curl -X POST http://206.189.56.166:8000/api/auth/register \\', TERMINAL_GREEN),
        ('  -H "Content-Type: application/json" \\', TERMINAL_WHITE),
        ('  -d \'{"email":"demo@ecolearnai.com", "password":"Demo@2026",', TERMINAL_YELLOW),
        ('       "full_name":"Jean Demo", "phone_number":"+243812345678",', TERMINAL_YELLOW),
        ('       "gdpr_consent":true, "gender":"M"}\'', TERMINAL_YELLOW),
        ('', TERMINAL_WHITE),
        ('HTTP 201 Created', TERMINAL_GREEN),
        ('{ "id": "d739ea6d-dd4d-4553-8cfb-...",', TERMINAL_CYAN),
        ('  "email": "demo@ecolearnai.com",', TERMINAL_CYAN),
        ('  "is_verified": false,  "sms_sent": true,', TERMINAL_PINK),
        ('  "email_sent": true,  "message": "Code OTP envoye" }', TERMINAL_PINK),
    ])

# Terminal 2 : Verification OTP
add_terminal(slide, Inches(6.8), Inches(1.1), Inches(6.3), Inches(1.7),
    "$ curl - POST /api/auth/verify-sms", [
        ('$ curl -X POST http://206.189.56.166:8000/api/auth/verify-sms \\', TERMINAL_GREEN),
        ('  -d \'{"email":"demo@ecolearnai.com", "code":"482917"}\'', TERMINAL_YELLOW),
        ('', TERMINAL_WHITE),
        ('HTTP 200 OK', TERMINAL_GREEN),
        ('{ "message": "Compte verifie avec succes !" }', TERMINAL_CYAN),
    ])

# Terminal 3 : Login JWT
add_terminal(slide, Inches(6.8), Inches(2.95), Inches(6.3), Inches(1.7),
    "$ curl - POST /api/auth/login", [
        ('$ curl -X POST http://206.189.56.166:8000/api/auth/login \\', TERMINAL_GREEN),
        ('  -d \'{"email":"demo@ecolearnai.com","password":"Demo@2026"}\'', TERMINAL_YELLOW),
        ('', TERMINAL_WHITE),
        ('HTTP 200 OK', TERMINAL_GREEN),
        ('{ "access_token": "eyJhbGciOi...KOARPY1WH", "token_type": "bearer" }', TERMINAL_CYAN),
    ])

# Terminal 4 : Creer parcours
add_terminal(slide, Inches(0.3), Inches(4.3), Inches(6.3), Inches(2.2),
    "$ curl - POST /api/learning/paths", [
        ('$ curl -X POST http://206.189.56.166:8000/api/learning/paths \\', TERMINAL_GREEN),
        ('  -H "Authorization: Bearer eyJhbGciOi..." \\', TERMINAL_WHITE),
        ('  -d \'{"title":"Apprendre Python", "subject":"Python",', TERMINAL_YELLOW),
        ('       "difficulty":"debutant", "total_sessions":5}\'', TERMINAL_YELLOW),
        ('', TERMINAL_WHITE),
        ('HTTP 201 Created', TERMINAL_GREEN),
        ('{ "id": "4beacfc1-49bb-4c9e-...",', TERMINAL_CYAN),
        ('  "title": "Apprendre Python", "progress_percent": 0.0 }', TERMINAL_CYAN),
    ])

# Terminal 5 : Session IA
add_terminal(slide, Inches(6.8), Inches(4.85), Inches(6.3), Inches(2.3),
    "$ curl - POST /api/learning/sessions  [IA GPT]", [
        ('$ curl -X POST http://206.189.56.166:8000/api/learning/sessions \\', TERMINAL_GREEN),
        ('  -H "Authorization: Bearer eyJhbGciOi..." \\', TERMINAL_WHITE),
        ('  -d \'{"learning_path_id":"4beacfc1-...","title":"Intro Python"}\'', TERMINAL_YELLOW),
        ('', TERMINAL_WHITE),
        ('HTTP 201 Created  (Backend -> Flask AI -> OpenAI GPT)', TERMINAL_GREEN),
        ('{ "id": "3792833e-5687-...", "session_number": 1,', TERMINAL_CYAN),
        ('  "content": "# Session 1/5 : Introduction a Python\\n\\n', TERMINAL_PINK),
        ('   ## Objectif\\nComprendre les bases de Python...\\n', TERMINAL_PINK),
        ('   ## Exercice pratique\\nCreez un programme qui..." }', TERMINAL_PINK),
    ])

# Badge : flux
add_rect(slide, Inches(0.3), Inches(6.7), Inches(5.5), Inches(0.6), GREEN_MID)
add_text_box(slide, Inches(0.5), Inches(6.75), Inches(5.1), Inches(0.45),
             "Flux : Register -> Verify OTP -> Login -> Create Path -> Start Session (IA GPT)",
             font_size=10, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════
#  SLIDE : DEMO TECHNIQUE 2 - Completion + Paiement + Monitoring
# ══════════════════════════════════════════════════════════

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, RGBColor(0x11, 0x11, 0x1B))

# Header
add_rect(slide, Inches(0), Inches(0), SLIDE_W, Inches(0.9), GREEN_DARK)
add_text_box(slide, Inches(0.6), Inches(0.1), Inches(12), Inches(0.35),
             "DEMO TECHNIQUE", font_size=13, color=GREEN_LIGHT, bold=True)
add_text_box(slide, Inches(0.6), Inches(0.4), Inches(12), Inches(0.4),
             "Completion + Gamification + Paiement + Monitoring", font_size=26, color=WHITE, bold=True)

# Terminal 6 : Terminer session
add_terminal(slide, Inches(0.3), Inches(1.1), Inches(6.3), Inches(3.2),
    "$ curl - PUT /sessions/{id}/complete  [Gamification]", [
        ('$ curl -X PUT http://206.189.56.166:8000/api/learning/ \\', TERMINAL_GREEN),
        ('  sessions/3792833e-.../complete \\', TERMINAL_GREEN),
        ('  -H "Authorization: Bearer eyJhbGciOi..." \\', TERMINAL_WHITE),
        ('  -d \'{"score": 85, "duration_minutes": 25}\'', TERMINAL_YELLOW),
        ('', TERMINAL_WHITE),
        ('HTTP 200 OK', TERMINAL_GREEN),
        ('{ "message": "Session terminee avec succes !",', TERMINAL_CYAN),
        ('  "progression": {', TERMINAL_CYAN),
        ('    "xp_earned": 85, "total_xp": 85, "level": "debutant",', TERMINAL_PINK),
        ('    "streak": 1, "streak_continued": true,', TERMINAL_PINK),
        ('    "new_badges": [{"name":"Premiere session","xp_reward":25}]', TERMINAL_YELLOW),
        ('  }, "carbon_footprint": {', TERMINAL_CYAN),
        ('    "energy_kwh": 0.083, "carbon_kg": 0.039 } }', TERMINAL_YELLOW),
    ])

# Terminal 7 : Paiement carte
add_terminal(slide, Inches(6.8), Inches(1.1), Inches(6.3), Inches(2.5),
    "$ curl - POST /api/subscriptions/subscribe  [Umoja Visa]", [
        ('$ curl -X POST http://206.189.56.166:8000/api/subscriptions/ \\', TERMINAL_GREEN),
        ('  subscribe -H "Authorization: Bearer eyJhbG..." \\', TERMINAL_GREEN),
        ('  -d \'{"plan":"annuel","payment_method":"carte_bancaire"}\'', TERMINAL_YELLOW),
        ('', TERMINAL_WHITE),
        ('HTTP 200 OK', TERMINAL_GREEN),
        ('{ "subscription_id": "a1b2c3d4-...",', TERMINAL_CYAN),
        ('  "payment_url": "https://card.gofreshpay.com/pay/...",', TERMINAL_PINK),
        ('  "message": "Redirect vers page paiement Umoja" }', TERMINAL_CYAN),
        ('', TERMINAL_WHITE),
        ('-> Redirect navigateur -> Saisie Visa -> Callback HMAC -> Active', TERMINAL_YELLOW),
    ])

# Terminal 8 : Dashboard
add_terminal(slide, Inches(6.8), Inches(3.8), Inches(6.3), Inches(1.8),
    "$ curl - GET /api/dashboard/", [
        ('$ curl http://206.189.56.166:8000/api/dashboard/ \\', TERMINAL_GREEN),
        ('  -H "Authorization: Bearer eyJhbG..."', TERMINAL_WHITE),
        ('', TERMINAL_WHITE),
        ('{ "user": "Jean Demo", "level": "debutant", "total_xp": 110,', TERMINAL_CYAN),
        ('  "streak": 1, "paths": 1, "sessions_completed": 1,', TERMINAL_PINK),
        ('  "total_carbon_kg": 0.039, "trees_planted": 0 }', TERMINAL_YELLOW),
    ])

# Terminal 9 : Monitoring health
add_terminal(slide, Inches(0.3), Inches(4.5), Inches(6.3), Inches(2.0),
    "$ curl - GET /api/monitoring/health  [Public]", [
        ('$ curl http://206.189.56.166:8000/api/monitoring/health', TERMINAL_GREEN),
        ('', TERMINAL_WHITE),
        ('HTTP 200 OK', TERMINAL_GREEN),
        ('{ "overall": "healthy",', TERMINAL_CYAN),
        ('  "backend": {"status":"up","version":"1.3.0"},', TERMINAL_PINK),
        ('  "database": {"status":"up","host":"159.89.13.54"},', TERMINAL_PINK),
        ('  "redis": {"status":"up","memory":"2.1MB"},', TERMINAL_YELLOW),
        ('  "ai_service": {"status":"up"} }', TERMINAL_YELLOW),
    ])

# Terminal 10 : Admin dashboard
add_terminal(slide, Inches(6.8), Inches(5.8), Inches(6.3), Inches(1.5),
    "$ curl - GET /api/admin/dashboard  [Admin only]", [
        ('$ curl http://206.189.56.166:8000/api/admin/dashboard \\', TERMINAL_GREEN),
        ('  -H "Authorization: Bearer ADMIN_TOKEN"', TERMINAL_WHITE),
        ('', TERMINAL_WHITE),
        ('{ "total_users": 42, "active_subscriptions": 18,', TERMINAL_CYAN),
        ('  "total_revenue": 1259.82, "total_sessions": 156 }', TERMINAL_PINK),
    ])

# Badge : resume
add_rect(slide, Inches(0.3), Inches(6.7), Inches(12.7), Inches(0.6), GREEN_MID)
add_text_box(slide, Inches(0.5), Inches(6.75), Inches(12.3), Inches(0.45),
             "Complete -> XP+Streak+Carbon+Badges  |  Subscribe -> Umoja Visa/MC  |  Dashboard -> Stats  |  Monitoring -> Health + Redis + MySQL",
             font_size=10, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════
#  SLIDE : CONTEXTE ET PROBLEMATIQUE
# ══════════════════════════════════════════════════════════

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_section_header(slide, "04", "Contexte et Problematique")

add_bullet_list(slide, Inches(0.8), Inches(1.6), Inches(5.5), Inches(2.5),
    [
        "Le marche de l'e-learning atteint 400 milliards USD en 2026",
        "Les plateformes existantes offrent un contenu generique",
        "Pas de personnalisation en fonction du niveau reel",
        "Aucune sensibilisation a l'impact ecologique du numerique",
        "Les donnees personnelles sont rarement protegees",
    ],
    title="Les defis actuels", font_size=16)

add_bullet_list(slide, Inches(7.0), Inches(1.6), Inches(5.5), Inches(2.5),
    [
        "Comment personnaliser l'apprentissage a grande echelle ?",
        "Comment mesurer et reduire l'empreinte carbone ?",
        "Comment garantir la protection des donnees (RGPD) ?",
        "Comment securiser les paiements en Afrique ?",
        "Comment motiver les apprenants sur la duree ?",
    ],
    title="Nos questions cles", font_size=16)

# Citation
add_rect(slide, Inches(0.8), Inches(5.5), Inches(11.7), Inches(1.2), GREEN_PALE)
add_text_box(slide, Inches(1.2), Inches(5.7), Inches(11), Inches(0.8),
             "\"EcoLearn AI repond a ces defis en combinant intelligence artificielle, gamification, "
             "suivi ecologique et securite des donnees dans une seule plateforme.\"",
             font_size=15, color=GREEN_DARK, bold=True, alignment=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════
#  SLIDE 4 : VISION ET OBJECTIFS
# ══════════════════════════════════════════════════════════

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_section_header(slide, "05", "Vision et Objectifs")

objectives = [
    ("Apprentissage adaptatif", "Parcours personnalises generes par IA (OpenAI GPT)\nadaptes au niveau, objectifs et preferences de chaque apprenant"),
    ("Impact ecologique", "Calcul automatique de l'empreinte carbone de chaque session\net plantation d'arbres compensatoires a chaque seuil atteint"),
    ("Gamification", "Systeme XP + niveaux (debutant -> expert) + streaks\n+ badges/achievements pour maintenir la motivation"),
    ("Securite RGPD", "Chiffrement AES-128 des donnees sensibles\nConsentement explicite, droit a l'oubli, portabilite"),
]

for i, (title, desc) in enumerate(objectives):
    x = Inches(0.6) + Inches(3.1) * i
    y = Inches(1.8)
    add_rect(slide, x, y, Inches(2.9), Inches(4.0), GREEN_PALE)
    add_text_box(slide, x + Inches(0.15), y + Inches(0.2), Inches(2.6), Inches(0.5),
                 title, font_size=17, color=GREEN_DARK, bold=True, alignment=PP_ALIGN.CENTER)
    add_rect(slide, x + Inches(0.5), y + Inches(0.7), Inches(1.9), Inches(0.03), GREEN_LIGHT)
    add_text_box(slide, x + Inches(0.15), y + Inches(0.9), Inches(2.6), Inches(2.8),
                 desc, font_size=13, color=GRAY)


# ══════════════════════════════════════════════════════════
#  SLIDE 5 : ARCHITECTURE TECHNIQUE
# ══════════════════════════════════════════════════════════

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_section_header(slide, "06", "Architecture Technique")

# Couche par couche
layers = [
    ("Client", "Navigateur / Mobile App", Inches(1.5), BLUE),
    ("Nginx LB", "Load Balancer + Reverse Proxy", Inches(2.3), RGBColor(0x55, 0x55, 0x55)),
    ("FastAPI Backend", "API REST + Auth JWT + Cache Redis + Cron Backup", Inches(3.1), GREEN_MID),
    ("Flask AI Service", "OpenAI GPT - Generation de contenu", Inches(3.9), RGBColor(0x6A, 0x1B, 0x9A)),
    ("MySQL NDB Cluster", "2 Data Nodes + 2 Mgmt Nodes + Backup", Inches(4.7), ORANGE),
    ("Redis 7.2", "Cache 256Mo + Rate Limiting + Anti brute-force", Inches(5.5), RED),
]

for label, desc, y, color in layers:
    add_rect(slide, Inches(1.5), y, Inches(4.5), Inches(0.65), color)
    add_text_box(slide, Inches(1.7), y + Inches(0.05), Inches(4.1), Inches(0.3),
                 label, font_size=15, color=WHITE, bold=True)
    add_text_box(slide, Inches(1.7), y + Inches(0.32), Inches(4.1), Inches(0.3),
                 desc, font_size=11, color=WHITE)

# Services externes
add_text_box(slide, Inches(7.5), Inches(1.6), Inches(5), Inches(0.4),
             "Services Externes", font_size=18, color=GREEN_DARK, bold=True)

ext_services = [
    ("Umoja CardAPI", "Paiement Visa/Mastercard"),
    ("MGT-SMS", "OTP + Notifications SMS"),
    ("Gmail SMTP", "Verification email + Alertes"),
    ("OpenAI GPT", "Generation contenu pedagogique"),
    ("Prometheus", "Collecte metriques (14 alertes)"),
    ("Grafana", "Dashboards visuels temps reel"),
]

for i, (svc, desc) in enumerate(ext_services):
    y = Inches(2.2) + Inches(0.65) * i
    add_rect(slide, Inches(7.5), y, Inches(5), Inches(0.55), GREEN_PALE)
    add_text_box(slide, Inches(7.7), y + Inches(0.05), Inches(2), Inches(0.25),
                 svc, font_size=13, color=GREEN_DARK, bold=True)
    add_text_box(slide, Inches(9.7), y + Inches(0.05), Inches(2.6), Inches(0.25),
                 desc, font_size=12, color=GRAY)


# ══════════════════════════════════════════════════════════
#  SLIDE 6 : ARCHITECTURE APPLICATIVE (BACKEND)
# ══════════════════════════════════════════════════════════

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_section_header(slide, "07", "Architecture Applicative")

# ── Colonne gauche : couches backend ──
add_text_box(slide, Inches(0.6), Inches(1.5), Inches(5.5), Inches(0.35),
             "Couches du Backend FastAPI (Stateless)", font_size=18, color=GREEN_DARK, bold=True)

backend_layers = [
    ("Middlewares", "CORS | Auth JWT | Rate Limiting | Prometheus", BLUE),
    ("9 Routers (API)", "auth | users | subscriptions | payments | learning\ncarbon | dashboard | admin | monitoring", GREEN_MID),
    ("10 Services (metier)", "Payment | Progression | Carbon | Moko | SMS\nEmail | Encryption | Cache (Redis) | Backup", RGBColor(0x6A, 0x1B, 0x9A)),
    ("10 Models (ORM)", "User | Subscription | Payment | SubscriptionPlan\nLearningPath | Session | Carbon | Compensation\nAchievement | UserAchievement", ORANGE),
    ("Security & Utils", "JWT Auth | bcrypt Hash | RBAC | Fernet AES-128", RED),
]

for i, (layer_name, layer_desc, color) in enumerate(backend_layers):
    y = Inches(2.0) + Inches(0.95) * i
    add_rect(slide, Inches(0.6), y, Inches(5.8), Inches(0.85), color)
    add_text_box(slide, Inches(0.8), y + Inches(0.05), Inches(5.4), Inches(0.3),
                 layer_name, font_size=14, color=WHITE, bold=True)
    add_text_box(slide, Inches(0.8), y + Inches(0.35), Inches(5.4), Inches(0.45),
                 layer_desc, font_size=11, color=WHITE)

# Fleches vers le bas (texte symbolique)
add_text_box(slide, Inches(3.0), Inches(6.85), Inches(1), Inches(0.35),
             "SQLAlchemy / PyMySQL -> MySQL 8.0", font_size=10, color=GRAY, alignment=PP_ALIGN.CENTER)

# ── Colonne droite : services et communications ──
add_text_box(slide, Inches(7.2), Inches(1.5), Inches(5.5), Inches(0.35),
             "Communication entre composants", font_size=18, color=GREEN_DARK, bold=True)

comm_items = [
    ("Client -> Nginx", "HTTPS (443)", "TLS 1.3 + Rate Limit"),
    ("Nginx -> Backend", "HTTP interne", "Round Robin / Least Conn"),
    ("Backend -> MySQL", "TCP (3306)", "PyMySQL + pool_recycle"),
    ("Backend -> Redis", "TCP (6379)", "Connection pool (50 max)"),
    ("Backend -> Flask AI", "HTTP (5000)", "POST /generate"),
    ("Backend -> Umoja", "HTTPS", "HMAC-SHA256 signature"),
    ("Backend -> MGT-SMS", "HTTPS", "x-api-key header"),
    ("Backend -> Gmail", "SMTPS (465)", "App Password SSL"),
    ("Umoja -> Backend", "HTTPS POST", "Callback HMAC verifie"),
]

for i, (route, protocol, detail) in enumerate(comm_items):
    y = Inches(2.0) + Inches(0.53) * i
    bg = GREEN_PALE if i % 2 == 0 else WHITE
    add_rect(slide, Inches(7.2), y, Inches(5.5), Inches(0.46), bg)
    add_text_box(slide, Inches(7.3), y + Inches(0.06), Inches(2.0), Inches(0.3),
                 route, font_size=11, color=GREEN_DARK, bold=True)
    add_text_box(slide, Inches(9.3), y + Inches(0.06), Inches(1.3), Inches(0.3),
                 protocol, font_size=10, color=BLUE, bold=True)
    add_text_box(slide, Inches(10.6), y + Inches(0.06), Inches(2.0), Inches(0.3),
                 detail, font_size=10, color=GRAY)


# ══════════════════════════════════════════════════════════
#  SLIDE 7 : SCHEMA BASE DE DONNEES
# ══════════════════════════════════════════════════════════

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_section_header(slide, "08", "Schema de la Base de Donnees")

add_text_box(slide, Inches(0.6), Inches(1.4), Inches(12), Inches(0.35),
             "MySQL 8.0 (NDB Cluster) - 10 tables - Serveur : 159.89.13.54  |  Backup : 159.89.13.55  |  Chiffrement Fernet sur 7 champs",
             font_size=13, color=GRAY, alignment=PP_ALIGN.CENTER)

# 5 tables par ligne, 2 lignes
db_tables = [
    # Ligne 1
    [
        ("users", "38 colonnes", [
            "id : UUID (PK)",
            "email : String(255) UNIQUE",
            "phone_number : String(20)",
            "hashed_password : String(255)",
            "full_name : String(255)",
            "7x encrypted_* : Text (Fernet)",
            "role : user | admin | super_admin",
            "total_xp, streak, level",
            "gdpr_consent, is_verified",
        ]),
        ("subscriptions", "10 colonnes", [
            "id : UUID (PK)",
            "user_id : UUID (FK -> users)",
            "plan : String(50)",
            "price : Float",
            "is_active : Boolean",
            "start_date, end_date",
            "auto_renew : Boolean",
        ]),
        ("payments", "14 colonnes", [
            "id : UUID (PK)",
            "user_id : UUID (FK -> users)",
            "subscription_id : UUID (FK)",
            "amount : Float, currency",
            "payment_method : String(50)",
            "status : pending | completed | failed",
            "transaction_ref : UNIQUE",
            "invoice_number : UNIQUE",
            "moko_transaction_uuid",
        ]),
        ("subscription_plans", "13 colonnes", [
            "id : UUID (PK)",
            "code : String(50) UNIQUE",
            "name : String(255)",
            "price : Float, currency",
            "duration_days : Integer",
            "is_active : Boolean",
            "features : Text (JSON)",
            "max_sessions_per_day",
        ]),
        ("learning_paths", "12 colonnes", [
            "id : UUID (PK)",
            "user_id : UUID (FK -> users)",
            "title : String(255)",
            "subject : String(255)",
            "difficulty : String(50)",
            "total_sessions : Integer",
            "progress_percent : Float",
            "status : en_cours | termine",
        ]),
    ],
    # Ligne 2
    [
        ("learning_sessions", "13 colonnes", [
            "id : UUID (PK)",
            "user_id : UUID (FK -> users)",
            "learning_path_id : UUID (FK)",
            "title, content : Text",
            "ai_prompt_used : Text",
            "duration_minutes : Float",
            "score : Float",
            "session_number : Integer",
            "status : en_cours | termine",
        ]),
        ("carbon_footprints", "9 colonnes", [
            "id : UUID (PK)",
            "user_id : UUID (FK -> users)",
            "session_id : UUID (FK, UNIQUE)",
            "duration_minutes : Float",
            "energy_kwh : Float",
            "carbon_kg : Float",
            "server_region : String(100)",
            "carbon_factor : Float",
        ]),
        ("eco_compensations", "10 colonnes", [
            "id : UUID (PK)",
            "user_id : UUID (FK -> users)",
            "trees_planted : Integer",
            "co2_compensated_kg : Float",
            "partner_name : String(255)",
            "status : confirmed | pending",
            "notes : Text",
        ]),
        ("achievements", "10 colonnes", [
            "id : UUID (PK)",
            "code : String(100) UNIQUE",
            "name : String(255)",
            "description : Text",
            "category : String(50)",
            "xp_reward : Integer",
            "condition_type : String(100)",
            "condition_value : Integer",
        ]),
        ("user_achievements", "4 colonnes", [
            "id : UUID (PK)",
            "user_id : UUID (FK -> users)",
            "achievement_id : UUID (FK)",
            "unlocked_at : DateTime",
            "",
            "",
            "",
            "",
        ]),
    ],
]

for row_idx, row in enumerate(db_tables):
    for col_idx, (table_name, col_count, columns) in enumerate(row):
        x = Inches(0.3) + Inches(2.55) * col_idx
        y_base = Inches(1.85) + Inches(2.75) * row_idx

        # Table header
        add_rect(slide, x, y_base, Inches(2.4), Inches(0.4), GREEN_MID)
        add_text_box(slide, x + Inches(0.05), y_base + Inches(0.02), Inches(2.3), Inches(0.2),
                     table_name, font_size=12, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)
        add_text_box(slide, x + Inches(0.05), y_base + Inches(0.2), Inches(2.3), Inches(0.18),
                     col_count, font_size=9, color=GREEN_PALE, alignment=PP_ALIGN.CENTER)

        # Table body
        body_h = Inches(0.22) * min(len([c for c in columns if c]), 9)
        add_rect(slide, x, y_base + Inches(0.4), Inches(2.4), body_h, GREEN_PALE)
        for ci, col_text in enumerate(columns):
            if not col_text:
                continue
            cy = y_base + Inches(0.42) + Inches(0.22) * ci
            add_text_box(slide, x + Inches(0.08), cy, Inches(2.25), Inches(0.2),
                         col_text, font_size=8, color=GRAY)


# ══════════════════════════════════════════════════════════
#  SLIDE 8 : RELATIONS ET FLUX DE DONNEES
# ══════════════════════════════════════════════════════════

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_section_header(slide, "09", "Relations et Flux de Donnees")

# Relations One-to-Many
add_text_box(slide, Inches(0.6), Inches(1.5), Inches(5.8), Inches(0.35),
             "Relations entre entites (cardinalites)", font_size=18, color=GREEN_DARK, bold=True)

relations = [
    ("User", "1 -> N", "Subscription", "Un utilisateur a 0..N abonnements"),
    ("User", "1 -> N", "Payment", "Un utilisateur a 0..N paiements"),
    ("User", "1 -> N", "LearningPath", "Un utilisateur a 0..N parcours"),
    ("User", "1 -> N", "LearningSession", "Un utilisateur a 0..N sessions"),
    ("User", "1 -> N", "CarbonFootprint", "Un utilisateur a 0..N empreintes"),
    ("User", "1 -> N", "EcoCompensation", "Un utilisateur a 0..N compensations"),
    ("User", "1 -> N", "UserAchievement", "Un utilisateur a 0..N badges"),
    ("Subscription", "1 -> N", "Payment", "Un abonnement a 1..N paiements"),
    ("LearningPath", "1 -> N", "LearningSession", "Un parcours a 0..N sessions"),
    ("LearningSession", "1 -> 1", "CarbonFootprint", "Une session a 0..1 empreinte"),
    ("Achievement", "1 -> N", "UserAchievement", "Un badge a 0..N deblocages"),
]

for i, (src, card, dst, desc) in enumerate(relations):
    y = Inches(1.95) + Inches(0.42) * i
    bg = GREEN_PALE if i % 2 == 0 else WHITE
    add_rect(slide, Inches(0.6), y, Inches(5.8), Inches(0.38), bg)
    add_text_box(slide, Inches(0.7), y + Inches(0.05), Inches(1.4), Inches(0.25),
                 src, font_size=11, color=GREEN_DARK, bold=True)
    add_text_box(slide, Inches(2.1), y + Inches(0.05), Inches(0.7), Inches(0.25),
                 card, font_size=10, color=BLUE, bold=True, alignment=PP_ALIGN.CENTER)
    add_text_box(slide, Inches(2.8), y + Inches(0.05), Inches(1.5), Inches(0.25),
                 dst, font_size=11, color=GREEN_DARK, bold=True)
    add_text_box(slide, Inches(4.3), y + Inches(0.05), Inches(2.1), Inches(0.25),
                 desc, font_size=9, color=GRAY)

# ── Colonne droite : Flux de donnees ──
add_text_box(slide, Inches(7.0), Inches(1.5), Inches(5.8), Inches(0.35),
             "Flux de donnees principaux", font_size=18, color=GREEN_DARK, bold=True)

# Flux inscription
add_card(slide, Inches(7.0), Inches(2.0), Inches(5.5), Inches(1.6),
    "Flux : Inscription", [
        "1. Client -> POST /api/auth/register",
        "2. Backend valide (Pydantic) + chiffre (Fernet)",
        "3. INSERT users (MySQL)",
        "4. Envoi OTP (MGT-SMS + Gmail en parallele)",
        "5. Client -> POST /api/auth/verify-sms",
    ], title_color=BLUE, bg_color=GREEN_PALE)

# Flux apprentissage
add_card(slide, Inches(7.0), Inches(3.8), Inches(5.5), Inches(1.6),
    "Flux : Apprentissage", [
        "1. Client -> POST /api/learning/sessions",
        "2. Backend -> Flask AI -> OpenAI GPT",
        "3. INSERT learning_sessions + contenu IA",
        "4. Client -> PUT /sessions/{id}/complete",
        "5. XP + Streak + Carbon + Badges + Level (atomique)",
    ], title_color=RGBColor(0x6A, 0x1B, 0x9A), bg_color=GREEN_PALE)

# Flux paiement
add_card(slide, Inches(7.0), Inches(5.6), Inches(5.5), Inches(1.5),
    "Flux : Paiement carte", [
        "1. Client -> POST /api/subscriptions/subscribe",
        "2. INSERT subscription (pending) + payment (pending)",
        "3. Backend -> Umoja API (HMAC) -> payment_url",
        "4. Umoja -> POST /callback (HMAC) -> completed",
        "5. UPDATE subscription (active) + SMS + Email",
    ], title_color=ORANGE, bg_color=GREEN_PALE)


# ══════════════════════════════════════════════════════════
#  SLIDE 9 : FONCTIONNALITES CLES
# ══════════════════════════════════════════════════════════

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_section_header(slide, "10", "Fonctionnalites Cles")

features = [
    ("Inscription RGPD", [
        "Collecte conforme (consentement obligatoire)",
        "Chiffrement Fernet (AES-128-CBC)",
        "Verification double canal (SMS + Email)",
        "Code OTP valable 10 minutes",
    ]),
    ("Parcours Adaptatifs", [
        "Creation de parcours personnalises",
        "Sessions generees par IA (OpenAI GPT)",
        "Progression automatique (XP, niveaux)",
        "Suivi par matiere et difficulte",
    ]),
    ("Dashboard Interactif", [
        "Progression pedagogique en temps reel",
        "Gamification : XP, streaks, badges",
        "Empreinte carbone personnelle",
        "Actions ecologiques (arbres plantes)",
    ]),
    ("Administration", [
        "CRUD plans d'abonnement (prix, duree)",
        "Gestion utilisateurs (roles, statut)",
        "KPIs : revenus, utilisateurs, sessions",
        "Dashboard admin avec statistiques",
    ]),
]

for i, (title, items) in enumerate(features):
    x = Inches(0.5) + Inches(3.15) * i
    y = Inches(1.6)

    add_rect(slide, x, y, Inches(3.0), Inches(0.5), GREEN_MID)
    add_text_box(slide, x + Inches(0.1), y + Inches(0.08), Inches(2.8), Inches(0.35),
                 title, font_size=15, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)

    for j, item in enumerate(items):
        iy = y + Inches(0.7) + Inches(0.55) * j
        add_rect(slide, x, iy, Inches(3.0), Inches(0.48), GREEN_PALE)
        add_text_box(slide, x + Inches(0.15), iy + Inches(0.08), Inches(2.7), Inches(0.35),
                     item, font_size=12, color=GRAY)


# ══════════════════════════════════════════════════════════
#  SLIDE 7 : INTELLIGENCE ARTIFICIELLE
# ══════════════════════════════════════════════════════════

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_section_header(slide, "11", "Intelligence Artificielle")

add_text_box(slide, Inches(0.8), Inches(1.6), Inches(5.5), Inches(0.4),
             "Microservice Flask + OpenAI GPT", font_size=20, color=GREEN_DARK, bold=True)

add_bullet_list(slide, Inches(0.8), Inches(2.2), Inches(5.5), Inches(3.5),
    [
        "Modele : GPT-3.5-turbo (2000 tokens max)",
        "Prompt contextuel adapte au profil de l'apprenant",
        "Parametres : niveau, objectifs, preferences, matiere",
        "Structure du contenu : objectif, explication, exemples, exercice, resume",
        "Mode fallback automatique si l'API OpenAI est indisponible",
        "Temperature : 0.7 (creativite equilibree)",
        "Service isole (conteneur Docker dedie)",
    ],
    font_size=15)

# Flux IA
add_text_box(slide, Inches(7.2), Inches(1.6), Inches(5.5), Inches(0.4),
             "Flux de generation de contenu", font_size=20, color=GREEN_DARK, bold=True)

steps = [
    "1. L'utilisateur demarre une session",
    "2. Le backend envoie le contexte au service IA",
    "3. Le prompt est construit avec le profil apprenant",
    "4. OpenAI GPT genere le contenu pedagogique",
    "5. Le contenu structure est retourne au backend",
    "6. La session est creee avec le contenu genere",
    "7. XP, streak, carbone sont mis a jour",
    "8. Badges verifies et debloques si necessaire",
]

for i, step in enumerate(steps):
    y = Inches(2.2) + Inches(0.52) * i
    color = GREEN_MID if i % 2 == 0 else GREEN_PALE
    text_color = WHITE if i % 2 == 0 else GREEN_DARK
    add_rect(slide, Inches(7.2), y, Inches(5.3), Inches(0.44), color)
    add_text_box(slide, Inches(7.4), y + Inches(0.07), Inches(5), Inches(0.3),
                 step, font_size=13, color=text_color, bold=(i % 2 == 0))


# ══════════════════════════════════════════════════════════
#  SLIDE 8 : SECURITE ET RGPD
# ══════════════════════════════════════════════════════════

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_section_header(slide, "12", "Securite et Conformite RGPD")

add_card(slide, Inches(0.5), Inches(1.6), Inches(3.8), Inches(2.5),
    "Authentification", [
        "JWT Bearer Token (HS256)",
        "Expiration : 30 minutes",
        "Mot de passe : bcrypt hash",
        "OTP double canal (SMS + Email)",
        "Anti brute-force OTP (Redis)",
    ], title_color=BLUE, bg_color=GREEN_PALE)

add_card(slide, Inches(4.7), Inches(1.6), Inches(3.8), Inches(2.5),
    "Chiffrement RGPD", [
        "Fernet (AES-128-CBC + HMAC-SHA256)",
        "7 champs sensibles chiffres :",
        "  date naissance, nationalite, ID,",
        "  adresse (4 champs)",
        "Cle : variable d'environnement",
    ], title_color=BLUE, bg_color=GREEN_PALE)

add_card(slide, Inches(8.9), Inches(1.6), Inches(3.8), Inches(2.5),
    "Droits Utilisateur", [
        "Art. 7 : Gestion des consentements",
        "Art. 13-14 : Droit a l'information",
        "Art. 15 : Droit d'acces",
        "Art. 17 : Droit a l'effacement",
        "Art. 20 : Droit a la portabilite",
    ], title_color=BLUE, bg_color=GREEN_PALE)

# Controle d'acces
add_text_box(slide, Inches(0.8), Inches(4.5), Inches(11.7), Inches(0.4),
             "Controle d'acces par roles (RBAC)", font_size=18, color=GREEN_DARK, bold=True)

roles = [
    ("user", "Acces a son profil, parcours, dashboard, paiements"),
    ("admin", "Gestion plans, utilisateurs, paiements, monitoring"),
    ("super_admin", "Tous les droits admin + changement de roles"),
]

for i, (role, desc) in enumerate(roles):
    y = Inches(5.1) + Inches(0.55) * i
    add_rect(slide, Inches(0.8), y, Inches(2.0), Inches(0.45), GREEN_MID)
    add_text_box(slide, Inches(0.9), y + Inches(0.07), Inches(1.8), Inches(0.3),
                 role, font_size=14, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)
    add_text_box(slide, Inches(3.0), y + Inches(0.07), Inches(9.5), Inches(0.3),
                 desc, font_size=14, color=GRAY)


# ══════════════════════════════════════════════════════════
#  SLIDE 9 : PAIEMENTS ET ABONNEMENTS
# ══════════════════════════════════════════════════════════

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_section_header(slide, "13", "Paiements et Abonnements")

# Plans
add_text_box(slide, Inches(0.8), Inches(1.5), Inches(5), Inches(0.4),
             "Plans d'abonnement (configurables par admin)", font_size=17, color=GREEN_DARK, bold=True)

plans = [
    ("Mensuel", "9.99 USD", "30 jours"),
    ("Trimestriel", "24.99 USD", "90 jours"),
    ("Annuel", "89.99 USD", "365 jours"),
]

for i, (name, price, duration) in enumerate(plans):
    x = Inches(0.8) + Inches(2.1) * i
    y = Inches(2.1)
    add_rect(slide, x, y, Inches(1.9), Inches(1.8), GREEN_PALE)
    add_text_box(slide, x + Inches(0.1), y + Inches(0.15), Inches(1.7), Inches(0.35),
                 name, font_size=15, color=GREEN_DARK, bold=True, alignment=PP_ALIGN.CENTER)
    add_text_box(slide, x + Inches(0.1), y + Inches(0.6), Inches(1.7), Inches(0.45),
                 price, font_size=24, color=GREEN_MID, bold=True, alignment=PP_ALIGN.CENTER)
    add_text_box(slide, x + Inches(0.1), y + Inches(1.2), Inches(1.7), Inches(0.3),
                 duration, font_size=13, color=GRAY, alignment=PP_ALIGN.CENTER)

# Methodes de paiement
add_text_box(slide, Inches(7.2), Inches(1.5), Inches(5.5), Inches(0.4),
             "Methodes de paiement", font_size=17, color=GREEN_DARK, bold=True)

add_card(slide, Inches(7.2), Inches(2.1), Inches(5.3), Inches(1.5),
    "Carte bancaire (Visa / Mastercard)", [
        "Via Umoja CardAPI (GoFreshPay)",
        "Redirection securisee vers page de paiement",
        "Callback HMAC-SHA256 pour confirmation",
        "Notifications SMS + Email automatiques",
    ], title_color=BLUE, bg_color=GREEN_PALE)

add_card(slide, Inches(7.2), Inches(3.9), Inches(5.3), Inches(1.2),
    "Mobile Money", [
        "Integration directe pour l'Afrique",
        "Activation instantanee de l'abonnement",
        "Factures automatiques generees",
    ], title_color=BLUE, bg_color=GREEN_PALE)

# Flux paiement
add_text_box(slide, Inches(0.8), Inches(4.3), Inches(6), Inches(0.4),
             "Flux de paiement carte bancaire", font_size=17, color=GREEN_DARK, bold=True)

pay_steps = [
    "Utilisateur choisit un plan",
    "Backend cree un paiement 'pending'",
    "Umoja genere une URL de paiement",
    "Utilisateur paye sur la page securisee",
    "Umoja envoie le callback au backend",
    "Backend active l'abonnement + facture",
    "Notifications SMS + Email envoyees",
]

for i, step in enumerate(pay_steps):
    y = Inches(4.8) + Inches(0.35) * i
    add_text_box(slide, Inches(0.8), y, Inches(6), Inches(0.3),
                 f"{i+1}. {step}", font_size=12, color=GRAY)


# ══════════════════════════════════════════════════════════
#  SLIDE 10 : CACHE REDIS
# ══════════════════════════════════════════════════════════

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_section_header(slide, "14", "Cache Redis et Performance")

add_bullet_list(slide, Inches(0.8), Inches(1.6), Inches(5.5), Inches(2.5),
    [
        "Redis 7.2 Alpine - 256 Mo de memoire",
        "Politique d'eviction : allkeys-lru (Least Recently Used)",
        "Persistence : AOF (sync chaque seconde) + Snapshots",
        "Connection pool : 50 connexions max",
        "Health check toutes les 30 secondes",
        "Mode degrade : si Redis tombe, l'app continue sans cache",
    ],
    title="Configuration Redis", font_size=15)

# Cles de cache
add_text_box(slide, Inches(7.0), Inches(1.6), Inches(5.5), Inches(0.4),
             "Strategie de cache (cles et TTL)", font_size=18, color=GREEN_DARK, bold=True)

cache_keys = [
    ("Plans d'abonnement", "10 minutes", "Catalogue des plans actifs"),
    ("Dashboard admin", "2 minutes", "Statistiques globales KPIs"),
    ("Dashboard utilisateur", "3 minutes", "Progression personnelle"),
    ("Tentatives OTP", "15 minutes", "Anti brute-force (max 5)"),
    ("Rate limiting", "1 minute", "60 requetes/min par IP"),
]

for i, (key, ttl, desc) in enumerate(cache_keys):
    y = Inches(2.2) + Inches(0.6) * i
    add_rect(slide, Inches(7.0), y, Inches(5.5), Inches(0.5), GREEN_PALE)
    add_text_box(slide, Inches(7.15), y + Inches(0.07), Inches(2.2), Inches(0.35),
                 key, font_size=13, color=GREEN_DARK, bold=True)
    add_text_box(slide, Inches(9.3), y + Inches(0.07), Inches(1.0), Inches(0.35),
                 ttl, font_size=12, color=ORANGE, bold=True)
    add_text_box(slide, Inches(10.3), y + Inches(0.07), Inches(2.0), Inches(0.35),
                 desc, font_size=11, color=GRAY)

# Impact performance
add_rect(slide, Inches(0.8), Inches(5.0), Inches(11.7), Inches(1.8), GREEN_PALE)
add_text_box(slide, Inches(1.2), Inches(5.15), Inches(11), Inches(0.4),
             "Impact sur les performances", font_size=18, color=GREEN_DARK, bold=True)

perfs = [
    ("Dashboard admin", "~500ms sans cache", "~5ms avec cache", "x100 plus rapide"),
    ("Liste des plans", "~100ms sans cache", "~2ms avec cache", "x50 plus rapide"),
    ("Dashboard user", "~300ms sans cache", "~3ms avec cache", "x100 plus rapide"),
]

for i, (endpoint, sans, avec, gain) in enumerate(perfs):
    y = Inches(5.65) + Inches(0.35) * i
    add_text_box(slide, Inches(1.2), y, Inches(2.5), Inches(0.3),
                 endpoint, font_size=13, color=BLACK, bold=True)
    add_text_box(slide, Inches(3.8), y, Inches(2.5), Inches(0.3),
                 sans, font_size=12, color=RED)
    add_text_box(slide, Inches(6.3), y, Inches(2.5), Inches(0.3),
                 avec, font_size=12, color=GREEN_MID)
    add_text_box(slide, Inches(9.0), y, Inches(3), Inches(0.3),
                 gain, font_size=13, color=GREEN_DARK, bold=True)


# ══════════════════════════════════════════════════════════
#  SLIDE 11 : MONITORING
# ══════════════════════════════════════════════════════════

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_section_header(slide, "15", "Monitoring et Observabilite")

# Stack
add_text_box(slide, Inches(0.8), Inches(1.6), Inches(5.5), Inches(0.4),
             "Stack de monitoring (Docker Compose)", font_size=18, color=GREEN_DARK, bold=True)

monitoring_services = [
    ("Prometheus :9090", "Collecte metriques, scrape 15s, retention 30j"),
    ("Grafana :3000", "Dashboards visuels, 10 panneaux auto-provisionnes"),
    ("Node Exporter :9100", "Metriques OS : CPU, RAM, Disque, Reseau"),
    ("Redis Exporter :9121", "Metriques Redis : memoire, hits, connexions"),
    ("MySQL Exporter :9104", "Metriques MySQL : QPS, connexions, slow queries"),
    ("Backend /metrics", "FastAPI Instrumentator (HTTP req/s, latence, erreurs)"),
]

for i, (svc, desc) in enumerate(monitoring_services):
    y = Inches(2.1) + Inches(0.55) * i
    add_rect(slide, Inches(0.8), y, Inches(5.5), Inches(0.48), GREEN_PALE if i % 2 == 0 else WHITE)
    add_text_box(slide, Inches(0.95), y + Inches(0.07), Inches(2.3), Inches(0.35),
                 svc, font_size=13, color=GREEN_DARK, bold=True)
    add_text_box(slide, Inches(3.3), y + Inches(0.07), Inches(3.0), Inches(0.35),
                 desc, font_size=12, color=GRAY)

# Alertes
add_text_box(slide, Inches(7.0), Inches(1.6), Inches(5.5), Inches(0.4),
             "14 regles d'alerte configurees", font_size=18, color=GREEN_DARK, bold=True)

alerts = [
    ("CRITICAL", "BackendDown, RedisDown, MySQLDown"),
    ("CRITICAL", "HighMemoryUsage (>90%), DiskSpaceCritical (>95%)"),
    ("WARNING", "HighErrorRate (5xx > 5%)"),
    ("WARNING", "HighLatency (P95 > 2s)"),
    ("WARNING", "RedisHighMemory (>85%)"),
    ("WARNING", "MySQLHighConnections (>80%)"),
    ("WARNING", "MySQLSlowQueries (>0.5/s)"),
    ("WARNING", "HighCPUUsage (>85%)"),
]

for i, (severity, desc) in enumerate(alerts):
    y = Inches(2.1) + Inches(0.55) * i
    sev_color = RED if severity == "CRITICAL" else ORANGE
    add_rect(slide, Inches(7.0), y, Inches(1.3), Inches(0.42), sev_color)
    add_text_box(slide, Inches(7.05), y + Inches(0.05), Inches(1.2), Inches(0.3),
                 severity, font_size=10, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)
    add_text_box(slide, Inches(8.4), y + Inches(0.05), Inches(4.2), Inches(0.35),
                 desc, font_size=12, color=GRAY)

# Endpoints monitoring
add_text_box(slide, Inches(0.8), Inches(5.6), Inches(11.7), Inches(0.3),
             "Endpoints API : /api/monitoring/health (public) | /system | /redis | /database | /backup | /cache/flush (admin)",
             font_size=13, color=GREEN_DARK, bold=True, alignment=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════
#  SLIDE 12 : BACKUP ET HAUTE DISPONIBILITE
# ══════════════════════════════════════════════════════════

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_section_header(slide, "16", "Backup et Haute Disponibilite")

# Cron backup
add_bullet_list(slide, Inches(0.8), Inches(1.6), Inches(5.5), Inches(3.5),
    [
        "APScheduler integre au backend FastAPI",
        "Execution automatique chaque jour a 01:00 UTC",
        "Replication complete : 10 tables, INSERT par lots de 500",
        "Synchronisation du schema (CREATE TABLE IF NOT EXISTS)",
        "Base de backup : ecolearnai_db_backup sur 159.89.13.55",
        "Historique des 30 derniers backups en memoire",
        "Alerte email automatique en cas d'echec",
        "Statut consultable via GET /api/monitoring/backup",
    ],
    title="Replication cron quotidienne", font_size=15)

# Haute dispo
add_bullet_list(slide, Inches(7.0), Inches(1.6), Inches(5.5), Inches(3.0),
    [
        "MySQL NDB Cluster : 2 Data Nodes + 2 Management Nodes",
        "Replication synchrone (NoOfReplicas=2)",
        "Zero perte de donnees si 1 noeud tombe",
        "2 SQL Nodes en Active-Active",
        "Redis : persistence AOF + Snapshots",
        "Docker : restart: always sur tous les services",
        "Health checks automatiques (Redis, MySQL, Backend)",
    ],
    title="Haute disponibilite", font_size=15)

# Procedure de restauration
add_rect(slide, Inches(0.8), Inches(5.5), Inches(11.7), Inches(1.3), GREEN_PALE)
add_text_box(slide, Inches(1.2), Inches(5.65), Inches(11), Inches(0.35),
             "En cas de perte de la base principale :", font_size=15, color=GREEN_DARK, bold=True)
add_text_box(slide, Inches(1.2), Inches(6.0), Inches(11), Inches(0.7),
             "1) Exporter depuis la base backup (mysqldump)  ->  "
             "2) Restaurer sur le serveur principal  ->  "
             "3) OU pointer le backend directement vers la base backup (changement de DATABASE_URL)",
             font_size=13, color=GRAY)


# ══════════════════════════════════════════════════════════
#  SLIDE : METHODOLOGIE AGILE / DEVOPS (10%)
# ══════════════════════════════════════════════════════════

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_section_header(slide, "17", "Methodologie Agile / DevOps (10%)")

# ── Colonne gauche : Organisation equipe + Workflow ──
add_text_box(slide, Inches(0.6), Inches(1.5), Inches(5.8), Inches(0.35),
             "Organisation equipe et workflow", font_size=18, color=GREEN_DARK, bold=True)

# Sprints Agile
add_card(slide, Inches(0.6), Inches(2.0), Inches(5.8), Inches(2.0),
    "Methodologie Scrum", [
        "Sprints de 2 semaines avec objectifs clairs",
        "Daily standup (15 min) - avancement + blocages",
        "Sprint Review : demo des fonctionnalites livrees",
        "Sprint Retrospective : amelioration continue",
        "Backlog priorise par valeur business (MoSCoW)",
        "Definition of Done : code + tests + doc + review",
    ], title_color=BLUE, bg_color=GREEN_PALE)

# Workflow Git
add_text_box(slide, Inches(0.6), Inches(4.2), Inches(5.8), Inches(0.35),
             "Workflow Git (GitFlow)", font_size=16, color=GREEN_DARK, bold=True)

git_flow = [
    ("main", "Production stable, deployee sur le serveur", GREEN_MID),
    ("develop", "Integration continue des features", BLUE),
    ("feature/*", "Branches par fonctionnalite (feature/auth, feature/payment)", RGBColor(0x6A, 0x1B, 0x9A)),
    ("hotfix/*", "Corrections urgentes en production", RED),
    ("release/*", "Preparation version (v1.0, v1.1, v1.3)", ORANGE),
]

for i, (branch, desc, color) in enumerate(git_flow):
    y = Inches(4.65) + Inches(0.45) * i
    add_rect(slide, Inches(0.6), y, Inches(1.4), Inches(0.38), color)
    add_text_box(slide, Inches(0.65), y + Inches(0.05), Inches(1.3), Inches(0.28),
                 branch, font_size=10, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)
    add_text_box(slide, Inches(2.1), y + Inches(0.05), Inches(4.3), Inches(0.28),
                 desc, font_size=11, color=GRAY)

# ── Colonne droite : DevOps + Documentation ──
add_text_box(slide, Inches(7.0), Inches(1.5), Inches(5.8), Inches(0.35),
             "Pipeline DevOps et documentation", font_size=18, color=GREEN_DARK, bold=True)

# CI/CD Pipeline
add_card(slide, Inches(7.0), Inches(2.0), Inches(5.8), Inches(2.0),
    "Pipeline CI/CD (Docker + Compose)", [
        "1. git push -> Declenchement automatique",
        "2. Build Docker image (backend + ai-service)",
        "3. Tests automatises (pytest + coverage)",
        "4. Analyse statique (linting, securite)",
        "5. Deploy sur serveur (docker compose up -d --build)",
        "6. Health check automatique post-deploy",
    ], title_color=BLUE, bg_color=GREEN_PALE)

# Documentation technique
add_text_box(slide, Inches(7.0), Inches(4.2), Inches(5.8), Inches(0.35),
             "Documentation technique", font_size=16, color=GREEN_DARK, bold=True)

docs = [
    ("API_DOCUMENTATION.md", "2700+ lignes", "50 endpoints documentes"),
    ("ARCHITECTURE.md", "786 lignes", "Architecture systeme complete"),
    ("CURL_COMMANDS.md", "500+ lignes", "Tous les curl de test"),
    ("UML_CAMUNDA.md", "1450+ lignes", "UML + BPMN Camunda"),
    (".env.example", "Configuration", "Variables d'environnement"),
    ("Swagger /docs", "Auto-genere", "OpenAPI 3.0 interactif"),
    ("ReDoc /redoc", "Auto-genere", "Documentation lisible"),
]

for i, (doc, size, desc) in enumerate(docs):
    y = Inches(4.65) + Inches(0.38) * i
    bg = GREEN_PALE if i % 2 == 0 else WHITE
    add_rect(slide, Inches(7.0), y, Inches(5.8), Inches(0.34), bg)
    add_text_box(slide, Inches(7.1), y + Inches(0.04), Inches(2.2), Inches(0.25),
                 doc, font_size=10, color=GREEN_DARK, bold=True)
    add_text_box(slide, Inches(9.3), y + Inches(0.04), Inches(1.3), Inches(0.25),
                 size, font_size=10, color=BLUE, bold=True)
    add_text_box(slide, Inches(10.6), y + Inches(0.04), Inches(2.1), Inches(0.25),
                 desc, font_size=10, color=GRAY)


# ══════════════════════════════════════════════════════════
#  SLIDE : STACK TECHNOLOGIQUE
# ══════════════════════════════════════════════════════════

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_section_header(slide, "18", "Stack Technologique")

tech_categories = [
    ("Backend", [
        ("FastAPI", "Framework API REST async"),
        ("SQLAlchemy 2.x", "ORM Python"),
        ("Pydantic", "Validation de donnees"),
        ("python-jose", "Tokens JWT"),
        ("passlib + bcrypt", "Hash mots de passe"),
        ("cryptography", "Chiffrement Fernet/AES"),
    ]),
    ("Data & Cache", [
        ("MySQL 8.0", "NDB Cluster (2+2+2)"),
        ("Redis 7.2", "Cache LRU 256 Mo"),
        ("PyMySQL", "Driver MySQL async"),
        ("APScheduler", "Cron backup quotidien"),
        ("redis-py 5.0", "Client Redis Python"),
        ("", ""),
    ]),
    ("IA & External", [
        ("Flask", "Microservice IA"),
        ("OpenAI GPT-3.5", "Generation de contenu"),
        ("httpx", "Client HTTP async"),
        ("Umoja CardAPI", "Paiement carte"),
        ("MGT-SMS", "Envoi SMS/OTP"),
        ("Gmail SMTP", "Envoi emails"),
    ]),
    ("DevOps & Monitoring", [
        ("Docker Compose", "Orchestration 8 services"),
        ("Nginx", "Load Balancer / Reverse Proxy"),
        ("Prometheus", "Collecte metriques"),
        ("Grafana", "Dashboards visuels"),
        ("Node/Redis/MySQL", "Exporters metriques"),
        ("psutil", "Metriques systeme Python"),
    ]),
]

for col, (category, techs) in enumerate(tech_categories):
    x = Inches(0.4) + Inches(3.2) * col
    y_top = Inches(1.6)

    add_rect(slide, x, y_top, Inches(3.0), Inches(0.5), GREEN_MID)
    add_text_box(slide, x + Inches(0.1), y_top + Inches(0.08), Inches(2.8), Inches(0.35),
                 category, font_size=15, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)

    for i, (tech, desc) in enumerate(techs):
        if not tech:
            continue
        iy = y_top + Inches(0.65) + Inches(0.52) * i
        add_text_box(slide, x + Inches(0.1), iy, Inches(1.4), Inches(0.3),
                     tech, font_size=12, color=GREEN_DARK, bold=True)
        add_text_box(slide, x + Inches(1.5), iy, Inches(1.4), Inches(0.3),
                     desc, font_size=11, color=GRAY)


# ══════════════════════════════════════════════════════════
#  SLIDE 14 : FEUILLE DE ROUTE
# ══════════════════════════════════════════════════════════

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, WHITE)
add_section_header(slide, "19", "Feuille de Route")

phases = [
    ("Phase 1 - Actuelle (v1.3)", GREEN_MID, [
        "Backend complet (FastAPI + 50 endpoints)",
        "IA (OpenAI GPT-3.5 + fallback)",
        "Paiements (Umoja + Mobile Money)",
        "RGPD complet (chiffrement + droits)",
        "Redis cache + Monitoring Prometheus/Grafana",
        "MySQL NDB Cluster + Backup cron quotidien",
    ]),
    ("Phase 2 - Q2 2026", BLUE, [
        "Frontend React.js / Next.js (SSR)",
        "Application mobile (React Native)",
        "WebSocket pour notifications temps reel",
        "Redis Cluster (haute dispo cache)",
        "CI/CD pipeline (GitHub Actions)",
        "Tests automatises (pytest, coverage > 80%)",
    ]),
    ("Phase 3 - Q3-Q4 2026", RGBColor(0x6A, 0x1B, 0x9A), [
        "Apprentissage collaboratif (groupes)",
        "Upgrade GPT-4 + fine-tuning educatif",
        "Marketplace de cours crees par la communaute",
        "Integration LMS (Moodle, Canvas)",
        "API publique pour partenaires",
        "Certification et diplomes numeriques",
    ]),
]

for col, (title, color, items) in enumerate(phases):
    x = Inches(0.4) + Inches(4.2) * col
    y_top = Inches(1.6)

    add_rect(slide, x, y_top, Inches(4.0), Inches(0.55), color)
    add_text_box(slide, x + Inches(0.15), y_top + Inches(0.1), Inches(3.7), Inches(0.4),
                 title, font_size=15, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)

    for i, item in enumerate(items):
        iy = y_top + Inches(0.7) + Inches(0.55) * i
        add_rect(slide, x, iy, Inches(4.0), Inches(0.48), GREEN_PALE)
        add_text_box(slide, x + Inches(0.15), iy + Inches(0.08), Inches(3.7), Inches(0.35),
                     item, font_size=13, color=GRAY)


# ══════════════════════════════════════════════════════════
#  SLIDE 15 : FIN / MERCI
# ══════════════════════════════════════════════════════════

slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, GREEN_DARK)

add_rect(slide, Inches(0), Inches(2.6), SLIDE_W, Inches(0.06), GREEN_LIGHT)
add_rect(slide, Inches(0), Inches(4.6), SLIDE_W, Inches(0.06), GREEN_LIGHT)

add_text_box(slide, Inches(1), Inches(1.3), Inches(11.3), Inches(0.8),
             "MERCI", font_size=60, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)

add_text_box(slide, Inches(1), Inches(2.1), Inches(11.3), Inches(0.5),
             "EcoLearn AI - Plateforme d'apprentissage intelligente et ecologique",
             font_size=20, color=GREEN_LIGHT, alignment=PP_ALIGN.CENTER)

add_text_box(slide, Inches(2), Inches(3.0), Inches(9.3), Inches(1.4),
             "API : http://206.189.56.166:8000/docs\n"
             "Grafana : http://206.189.56.166:3000\n"
             "Prometheus : http://206.189.56.166:9090\n"
             "ReDoc : http://206.189.56.166:8000/redoc",
             font_size=16, color=WHITE, alignment=PP_ALIGN.CENTER)

add_text_box(slide, Inches(1), Inches(5.0), Inches(11.3), Inches(0.5),
             "Questions ?", font_size=28, color=WHITE, bold=True, alignment=PP_ALIGN.CENTER)

add_text_box(slide, Inches(1), Inches(6.0), Inches(11.3), Inches(0.4),
             "Version 1.3.0  |  Fevrier 2026  |  Equipe EcoLearn AI",
             font_size=14, color=GRAY_LIGHT, alignment=PP_ALIGN.CENTER)


# ══════════════════════════════════════════════════════════
#  SAUVEGARDE
# ══════════════════════════════════════════════════════════

output_path = "EcoLearnAI_Presentation.pptx"
prs.save(output_path)
print(f"Presentation generee : {output_path}")
print(f"Nombre de slides : {len(prs.slides)}")
