import pygame
import sys

# Inicializar Pygame
pygame.init()
pygame.display.set_caption("Calibrador de Zoltar")

# Tamaño de ventana
WIDTH, HEIGHT = 800, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Cargar imágenes
zoltar_img = pygame.image.load("backend/frontend/static/img/Zoltar_1.png")
gabinete_img = pygame.image.load("backend/frontend/static/img/Gabinete_Zoltar.png")
coin_img = pygame.image.load("backend/frontend/static/img/coin.png")

# Posiciones y escalas
elements = {
    "zoltar": {"img": zoltar_img, "x": 150, "y": 50, "scale": 1.0},
    "gabinete": {"img": gabinete_img, "x": 0, "y": 0, "scale": 1.0},
    "slot": {"x": 380, "y": 900, "scale": 1.0},  # sin imagen
    "coin": {"img": coin_img, "x": 350, "y": 920, "scale": 0.15},
}

order = ["zoltar", "gabinete", "slot", "coin"]
selected_index = 0
selected = order[selected_index]

font = pygame.font.SysFont(None, 24)

# Función para escalar imágenes
def scale_image(img, scale):
    w = int(img.get_width() * scale)
    h = int(img.get_height() * scale)
    return pygame.transform.scale(img, (w, h))

clock = pygame.time.Clock()
running = True

while running:
    screen.fill((0, 0, 0))

    # Escalar imágenes
    zoltar_scaled = scale_image(elements["zoltar"]["img"], elements["zoltar"]["scale"])
    gabinete_scaled = scale_image(elements["gabinete"]["img"], elements["gabinete"]["scale"])
    coin_scaled = scale_image(elements["coin"]["img"], elements["coin"]["scale"])
    slot_rect = pygame.Rect(
        elements["slot"]["x"], elements["slot"]["y"],
        int(28 * elements["slot"]["scale"]), int(60 * elements["slot"]["scale"])
    )

    # Orden correcto
    screen.blit(zoltar_scaled, (elements["zoltar"]["x"], elements["zoltar"]["y"]))
    screen.blit(gabinete_scaled, (elements["gabinete"]["x"], elements["gabinete"]["y"]))
    pygame.draw.rect(screen, (30, 30, 30), slot_rect)
    pygame.draw.rect(screen, (160, 160, 160), slot_rect, 3)
    screen.blit(coin_scaled, (elements["coin"]["x"], elements["coin"]["y"]))

    # Instrucciones
    text = font.render(f"[{selected.upper()}] ←↑↓→: mover  |  W/S: escala  |  TAB: cambiar  |  ESC: salir", True, (255, 255, 255))
    screen.blit(text, (20, 20))

    pygame.display.flip()

    # Manejar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            # Cambiar selección con TAB
            if event.key == pygame.K_TAB:
                selected_index = (selected_index + 1) % len(order)
                selected = order[selected_index]

            # Salir con ESC
            elif event.key == pygame.K_ESCAPE:
                running = False

    # Teclas presionadas
    keys = pygame.key.get_pressed()

    # Movimiento
    if keys[pygame.K_LEFT]:
        elements[selected]["x"] -= 5
    if keys[pygame.K_RIGHT]:
        elements[selected]["x"] += 5
    if keys[pygame.K_UP]:
        elements[selected]["y"] -= 5
    if keys[pygame.K_DOWN]:
        elements[selected]["y"] += 5

    # Escalar
    if keys[pygame.K_w]:
        elements[selected]["scale"] += 0.01
    if keys[pygame.K_s]:
        elements[selected]["scale"] = max(0.01, elements[selected]["scale"] - 0.01)

    clock.tick(60)

# Imprimir resultados
print("\n=== VALORES DE CALIBRACIÓN ===")
for key in elements:
    el = elements[key]
    if "img" in el:
        print(f"{key.title()} → x: {el['x']}, y: {el['y']}, scale: {el['scale']:.3f}")
    else:
        print(f"{key.title()} (slot) → x: {el['x']}, y: {el['y']}, scale: {el['scale']:.3f}")

pygame.quit()
sys.exit()






