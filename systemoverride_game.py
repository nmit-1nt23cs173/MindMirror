import pygame
import sys
import time

pygame.init()

# Screen
WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("MindMirror AI")

# Colors
BG = (15, 15, 25)
CARD = (30, 30, 50)
BUTTON = (60, 60, 100)
HOVER = (90, 90, 150)
TEXT = (230, 230, 255)
ACCENT = (0, 200, 255)
GOOD = (0, 255, 150)
DANGER = (255, 80, 80)

# Fonts
title_font = pygame.font.SysFont("consolas", 50)
font = pygame.font.SysFont("consolas", 26)
small = pygame.font.SysFont("consolas", 18)

clock = pygame.time.Clock()

# States
MENU, TEST, RESULT = "menu", "test", "result"
state = MENU
active_test = None

# Timer
QUESTION_TIME = 10
question_start_time = 0

# ===================== TEST DATA =====================
tests = {
    "confidence": [
        ("You are given responsibility to lead a critical task.", [
            ("Take charge immediately", 4),
            ("Accept after thinking", 3),
            ("Feel unsure but try", 2),
            ("Avoid responsibility", 1)
        ]),
        ("You face a new challenge.", [
            ("Confident to handle", 4),
            ("Prepare and try", 3),
            ("Nervous but try", 2),
            ("Avoid it", 1)
        ])
    ],

    "personality": [
        ("At a party, you usually:", [
            ("Talk to many people", 4),
            ("Talk to few people", 3),
            ("Stay with known friends", 2),
            ("Avoid interaction", 1)
        ]),
        ("Your energy comes from:", [
            ("Being around people", 4),
            ("Mix of both", 3),
            ("Mostly alone time", 2),
            ("Complete isolation", 1)
        ])
    ],

    "stress": [
        ("When under pressure:", [
            ("Stay calm and act", 4),
            ("Feel tense but manage", 3),
            ("Get anxious", 2),
            ("Panic or freeze", 1)
        ]),
        ("Facing deadlines:", [
            ("Work efficiently", 4),
            ("Manage somehow", 3),
            ("Feel overwhelmed", 2),
            ("Avoid work", 1)
        ])
    ],

    "leadership": [
        ("In group work:", [
            ("Lead naturally", 4),
            ("Help coordinate", 3),
            ("Follow others", 2),
            ("Avoid involvement", 1)
        ]),
        ("When conflict arises:", [
            ("Resolve confidently", 4),
            ("Try to mediate", 3),
            ("Stay silent", 2),
            ("Avoid situation", 1)
        ])
    ],

    "decision": [
        ("When making decisions:", [
            ("Analyze and decide fast", 4),
            ("Think carefully", 3),
            ("Doubt often", 2),
            ("Avoid deciding", 1)
        ]),
        ("Under uncertainty:", [
            ("Take calculated risk", 4),
            ("Be cautious", 3),
            ("Feel confused", 2),
            ("Avoid decision", 1)
        ])
    ],

    "creativity": [
        ("When solving problems:", [
            ("Think out of the box", 4),
            ("Use known methods", 3),
            ("Follow others", 2),
            ("Give up", 1)
        ]),
        ("You prefer:", [
            ("Creating ideas", 4),
            ("Improving ideas", 3),
            ("Following ideas", 2),
            ("Avoid thinking", 1)
        ])
    ],

    "discipline": [
        ("Daily routine:", [
            ("Highly structured", 4),
            ("Somewhat planned", 3),
            ("Unorganized", 2),
            ("No routine", 1)
        ]),
        ("When distracted:", [
            ("Stay focused", 4),
            ("Refocus quickly", 3),
            ("Lose track", 2),
            ("Give up", 1)
        ])
    ]
}

# ===================== DATA =====================
responses = []
current_q = 0
option_buttons = []
result_lines = []

# ===================== BUTTON =====================
class Button:
    def __init__(self, text, x, y, w, h, color=BUTTON):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color

    def draw(self):
        mouse = pygame.mouse.get_pos()
        col = HOVER if self.rect.collidepoint(mouse) else self.color
        pygame.draw.rect(screen, col, self.rect, border_radius=12)

        txt = font.render(self.text, True, TEXT)
        screen.blit(txt, (self.rect.centerx - txt.get_width()//2,
                          self.rect.centery - txt.get_height()//2))

    def click(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# ===================== BUTTONS =====================
menu_buttons = []
y = 220
for key in tests.keys():
    menu_buttons.append((key, Button(key.capitalize(), WIDTH//2-150, y, 300, 50)))
    y += 60

exit_btn = Button("EXIT", WIDTH-150, HEIGHT-80, 120, 50, DANGER)
back_btn = Button("BACK", WIDTH//2-150, HEIGHT-100, 300, 60)

# ===================== FUNCTIONS =====================
def start_test(name):
    global state, active_test, current_q, responses
    state = TEST
    active_test = name
    current_q = 0
    responses = []
    next_question()

def next_question():
    global option_buttons, question_start_time
    option_buttons = []
    q, options = tests[active_test][current_q]

    y = 320
    for text, value in options:
        option_buttons.append((Button(text, WIDTH//2-250, y, 500, 50), value))
        y += 70

    question_start_time = time.time()

def analyze():
    global state, result_lines

    values = [r[0] for r in responses]
    times = [r[1] for r in responses]

    avg = sum(values)/len(values)
    variance = sum((v-avg)**2 for v in values)/len(values)
    consistency = max(0, 1 - variance/4)

    avg_time = sum(times)/len(times)
    speed = max(0, 1 - (avg_time/QUESTION_TIME))

    final = (avg/4)*60 + consistency*20 + speed*20

    if final > 80:
        level = "EXCELLENT"
    elif final > 65:
        level = "STRONG"
    elif final > 50:
        level = "AVERAGE"
    else:
        level = "NEEDS IMPROVEMENT"

    insight = f"This reflects your {active_test} behavior pattern."

    result_lines = [
        f"{active_test.upper()} LEVEL: {level}",
        f"Score: {int(final)}%",
        "",
        "Analysis:",
        "- Decision pattern evaluated",
        "- Consistency measured",
        "- Response speed analyzed",
        "",
        "Insight:",
        insight
    ]

    state = RESULT

def next_step():
    global current_q
    current_q += 1
    if current_q >= len(tests[active_test]):
        analyze()
    else:
        next_question()

# ===================== DRAW =====================
def draw_menu():
    screen.fill(BG)
    title = title_font.render("MindMirror AI", True, ACCENT)
    screen.blit(title, (WIDTH//2-title.get_width()//2, 100))

    for _, b in menu_buttons:
        b.draw()

    exit_btn.draw()

def draw_test():
    screen.fill(BG)

    q, _ = tests[active_test][current_q]

    pygame.draw.rect(screen, CARD, (150, 150, 700, 120), border_radius=15)
    txt = font.render(q, True, TEXT)
    screen.blit(txt, (WIDTH//2-txt.get_width()//2, 190))

    elapsed = time.time() - question_start_time
    remaining = max(0, QUESTION_TIME - int(elapsed))

    timer = font.render(f"Time: {remaining}s", True, ACCENT)
    screen.blit(timer, (50, 50))

    progress = (current_q+1)/len(tests[active_test])
    pygame.draw.rect(screen, ACCENT, (150, 100, 700*progress, 10))

    for b, _ in option_buttons:
        b.draw()

    if remaining <= 0:
        responses.append((2, QUESTION_TIME))
        next_step()

def draw_result():
    screen.fill(BG)

    y = 150
    for line in result_lines:
        txt = font.render(line, True, GOOD if "LEVEL" in line else TEXT)
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, y))
        y += 45

    back_btn.draw()
    exit_btn.draw()

# ===================== LOOP =====================
running = True
while running:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Exit only menu/result
        if state in [MENU, RESULT]:
            if exit_btn.click(event):
                pygame.quit()
                sys.exit()

        if state == MENU:
            for key, btn in menu_buttons:
                if btn.click(event):
                    start_test(key)

        elif state == TEST:
            for b, val in option_buttons:
                if b.click(event):
                    t = time.time() - question_start_time
                    responses.append((val, t))
                    next_step()

        elif state == RESULT:
            if back_btn.click(event):
                state = MENU

    if state == MENU:
        draw_menu()
    elif state == TEST:
        draw_test()
    elif state == RESULT:
        draw_result()

    pygame.display.update()
    clock.tick(60)