import pygame
import random

# Inisialisasi pygame
pygame.init()
pygame.mixer.init()

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 102, 204)
RED = (200, 0, 0)
GREEN = (0, 200, 0)

# Ukuran layar
WIDTH, HEIGHT = 720, 1600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Batu Gunting Kertas - Critical Hit!")

# Font
default_font = pygame.font.Font(None, 48)
alert_font = pygame.font.Font(None, 80)
critical_font = pygame.font.Font(None, 120)

# Pilihan game
SHAPES = ["batu", "gunting", "kertas"]
MAX_HP = 200  # Konstanta HP

# Posisi tombol
button_rects = {
    "batu": pygame.Rect(WIDTH * 0.07, HEIGHT * 0.85, 200, 150),
    "gunting": pygame.Rect(WIDTH * 0.36, HEIGHT * 0.85, 200, 150),
    "kertas": pygame.Rect(WIDTH * 0.65, HEIGHT * 0.85, 200, 150),
}

# Tombol restart
restart_button = pygame.Rect(WIDTH * 0.36, HEIGHT * 0.5, 200, 100)

# Memuat gambar
bg = pygame.transform.scale(pygame.image.load("assets/bg.png"), (WIDTH, HEIGHT))
batu_img = pygame.image.load("assets/batu.png")
gunting_img = pygame.image.load("assets/gunting.png")
kertas_img = pygame.image.load("assets/kertas.png")

batu_btn = pygame.transform.scale(batu_img, (150, 150))
gunting_btn = pygame.transform.scale(gunting_img, (150, 150))
kertas_btn = pygame.transform.scale(kertas_img, (150, 150))

shape_images = {"batu": batu_img, "gunting": gunting_img, "kertas": kertas_img}
button_images = {"batu": batu_btn, "gunting": gunting_btn, "kertas": kertas_btn}

# Suara
pygame.mixer.music.load("assets/music/bg.mp3")
pygame.mixer.music.play(-1)

crit_sfx = pygame.mixer.Sound("assets/music/crit.mp3")
winron_sfx = pygame.mixer.Sound("assets/music/winron.mp3")
win_sfx = pygame.mixer.Sound("assets/music/menang.mp3")
lose_sfx = pygame.mixer.Sound("assets/music/kalah.mp3")
streak_sfx = pygame.mixer.Sound("assets/music/streak.mp3")

# HP Sistem
player_hp = MAX_HP
bot_hp = MAX_HP
score = 0
streak = 0
# Membaca high score dari file
def load_highscore():
    try:
        with open("highscore.txt", "r") as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return 0  # Jika file tidak ditemukan, high score dianggap 0

highscore = load_highscore()

# Variabel game
player_choice = None
bot_choice = None
game_over = False
winner_text = ""
critical_hit = False
can_click = True


# Variabel animasi easing
animation_progress = 0
animation_speed = 0.07  
winner_pos_offset = 0  

# Fungsi untuk menghitung damage
def calculate_damage(winner_hp):
    damage = 15
    is_critical = random.random() < 0.1  # 10% peluang critical
    if is_critical:
        damage += 25
        crit_sfx.play()

    return max(0, winner_hp - damage), is_critical

# Loop utama
running = True
while running:
    screen.blit(bg, (0, 0))

    # Menampilkan HP Bar
    pygame.draw.rect(screen, RED, (70, 1240, 200, 30))
    pygame.draw.rect(screen, GREEN, (70, 1240, player_hp, 30))
    pygame.draw.rect(screen, RED, (480, 320, 200, 30))
    pygame.draw.rect(screen, GREEN, (480, 320, bot_hp, 30))

    # Menampilkan tombol jika belum game over
    if not game_over:
        for shape, rect in button_rects.items():
            pygame.draw.rect(screen, BLUE, rect, border_radius=20)
            screen.blit(button_images[shape], (rect.x + 25, rect.y))

    # Menampilkan pilihan pemain dan bot
    if player_choice:
        player_pos = [WIDTH * 0.35, HEIGHT * 0.68 - winner_pos_offset]
        bot_pos = [WIDTH * 0.35, HEIGHT * 0.12 + winner_pos_offset]

        screen.blit(shape_images[player_choice], player_pos)
        bot_img_rotated = pygame.transform.rotate(shape_images[bot_choice], 180)
        screen.blit(bot_img_rotated, bot_pos)

        # Easing Animation
        if animation_progress < 1:
            animation_progress += animation_speed
            ease_out = 1 - (1 - animation_progress) ** 2  
            winner_pos_offset = int(ease_out * 100)

        # Menampilkan teks "CRITICAL!" jika terjadi critical damage
        if critical_hit:
            crit_text = critical_font.render("CRITICAL!", True, RED)
            screen.blit(crit_text, (WIDTH * 0.26, HEIGHT * 0.45))

    # Menampilkan hasil jika game over
    if game_over:
        winner_surface = alert_font.render(winner_text, True, WHITE)
        screen.blit(winner_surface, (WIDTH * 0.25, HEIGHT * 0.46))

        pygame.draw.rect(screen, BLUE, restart_button, border_radius=20)
        restart_text = default_font.render("Restart", True, WHITE)
        screen.blit(restart_text, (restart_button.x + 50, restart_button.y + 30))

    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and can_click:
            if not game_over:
                for shape, rect in button_rects.items():
                    if rect.collidepoint(event.pos):
                        player_choice = shape
                        bot_choice = random.choice(SHAPES)
                        animation_progress = 0
                        winner_pos_offset = 0
                        critical_hit = False  

                        # Menentukan pemenang
                        if player_choice == bot_choice:
                            winner_text = "Seri!"
                        elif (player_choice == "batu" and bot_choice == "gunting") or \
                             (player_choice == "gunting" and bot_choice == "kertas") or \
                             (player_choice == "kertas" and bot_choice == "batu"):
                            
                            bot_hp, critical_hit = calculate_damage(bot_hp)
                            streak += 1  # Tambah streak
                            score += 10  # Tambah 
                            if streak == 2:
                            	score += 50
                            elif streak == 3:
                            	score += 100
                            elif streak == 5:
                            	score += 200
                            	streak_sfx.play()  # Mainkan suara streak
                            winron_sfx.play()
                            winner_text = "Kamu Menang!"
                        else:
                            player_hp, critical_hit = calculate_damage(player_hp)
                            streak = 0  # Reset streak jika kalah
                            winner_text = "Bot Menang!"

                        # Cek kondisi game over
                        if player_hp == 0:
                            game_over = True
                            lose_sfx.play()
                        elif bot_hp == 0:
                            game_over = True
                            win_sfx.play()

                        can_click = False  
                        pygame.time.set_timer(pygame.USEREVENT, 500)

            elif restart_button.collidepoint(event.pos):
                player_hp = MAX_HP
                bot_hp = MAX_HP
                player_choice = None
                bot_choice = None
                game_over = False
                winner_text = ""
                critical_hit = False
                animation_progress = 0
                winner_pos_offset = 0
                score = 0
                streak = 0

    if event.type == pygame.USEREVENT:
        can_click = True

    score_text = default_font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH * 0.05, 100))
    streak_text = default_font.render(f"Streak: {streak}", True, WHITE)
    screen.blit(streak_text, (WIDTH * 0.05, 150))
    # Menyimpan high score jika skor lebih tinggi
    if score > highscore:
    	highscore = score
    with open("highscore.txt", "w") as file:
    	file.write(str(highscore))
    highscore_text = default_font.render(f"High Score: {highscore}", True, WHITE)
    screen.blit(highscore_text, (WIDTH * 0.05, 200))
    pygame.display.flip()
   

pygame.quit()