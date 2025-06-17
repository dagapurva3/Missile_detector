import pygame
import math
import random
import sys
from config import (
    WIDTH,
    HEIGHT,
    COLORS,
)
from game_objects import (
    FONTS,
    DefenseBase,
    EnhancedExplosion,
    ThreatRadar,
    get_missile,
    recycle_missile,
)
from physics import PhysicsEquation
from ui import (
    SystemMetrics,
    draw_enhanced_button,
    draw_enhanced_panel,
    draw_metric_display,
    generate_terrain,
)
from utils import calculate_intercept_point, classify_threat


pygame.init()
pygame.font.init()


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SUCCEDRA: Advanced Algorithmic Missile Defense System")


def main():
    clock = pygame.time.Clock()
    running = True

    # Initialize game objects
    base = DefenseBase(220, HEIGHT - 150)
    missiles = []
    interceptors = []
    explosions = []
    equations = []
    metrics = SystemMetrics()
    radar = ThreatRadar(130, 150, 80)

    # Game state
    auto_mode = True
    threat_level = 1
    last_missile_time = 0
    missile_intervals = [4000, 2000, 1000]  # ms for Low, Medium, High
    terrain = generate_terrain(WIDTH, HEIGHT, HEIGHT - 100)

    # Initialize equations
    for i in range(5):
        equations.append(PhysicsEquation(WIDTH // 2 + 50, 100 + i * 130))

    # Performance tracking
    frame_count = 0
    fps_display = 60
    last_terrain_update = 0

    while running:
        current_time = pygame.time.get_ticks()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not auto_mode:
                    # Manual missile launch
                    start_x = random.randint(100, WIDTH - 400)
                    start_y = random.randint(50, 200)
                    velocity = random.randint(500, 3500)
                    altitude = random.randint(500, 15000)
                    threat_type = classify_threat(velocity, altitude)
                    missiles.append(
                        get_missile(start_x, start_y, base.x, base.y, True, threat_type)
                    )
                    metrics.total_threats += 1
                elif event.key == pygame.K_a:
                    auto_mode = not auto_mode
                elif event.key == pygame.K_1:
                    threat_level = 0
                elif event.key == pygame.K_2:
                    threat_level = 1
                elif event.key == pygame.K_3:
                    threat_level = 2
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # Auto missile launch
        if (
            auto_mode
            and current_time - last_missile_time > missile_intervals[threat_level]
        ):
            last_missile_time = current_time

            # Launch primary missile
            start_x = random.randint(100, WIDTH - 400)
            start_y = random.randint(50, 250)
            velocity = random.randint(500, 3500)
            altitude = random.randint(500, 15000)
            threat_type = classify_threat(velocity, altitude)
            missiles.append(
                get_missile(start_x, start_y, base.x, base.y, True, threat_type)
            )
            metrics.total_threats += 1

            # Launch additional missiles based on threat level
            additional_missiles = threat_level
            for _ in range(additional_missiles):
                if random.random() < 0.4:
                    start_x = random.randint(100, WIDTH - 400)
                    start_y = random.randint(50, 250)
                    velocity = random.randint(500, 3500)
                    altitude = random.randint(500, 15000)
                    threat_type = classify_threat(velocity, altitude)
                    missiles.append(
                        get_missile(start_x, start_y, base.x, base.y, True, threat_type)
                    )
                    metrics.total_threats += 1

        # Launch interceptors
        for missile in missiles[:]:
            if missile.active and missile.is_hostile:
                # Check if interceptor already exists for this missile
                has_interceptor = any(
                    not interceptor.is_hostile
                    and abs(interceptor.target_x - missile.x) < 50
                    and abs(interceptor.target_y - missile.y) < 50
                    for interceptor in interceptors
                )

                if not has_interceptor and missile.threat_type == "missile":
                    # Calculate intercept point
                    intercept_x, intercept_y = calculate_intercept_point(
                        base.x, base.y, missile, 4.0
                    )
                    interceptors.append(
                        get_missile(base.x, base.y, intercept_x, intercept_y, False)
                    )

                    # Add radar blip
                    angle = math.degrees(
                        math.atan2(missile.y - base.y, missile.x - base.x)
                    )
                    distance = (
                        math.sqrt((missile.x - base.x) ** 2 + (missile.y - base.y) ** 2)
                        / 600
                    )
                    radar.add_blip(missile.threat_type, angle, min(0.95, distance))

        # Update game objects
        base.update()
        radar.update()

        # Update terrain occasionally
        if current_time - last_terrain_update > 5000:
            terrain = generate_terrain(WIDTH, HEIGHT, HEIGHT - 100)
            last_terrain_update = current_time

        # Update missiles
        for missile in missiles[:]:
            if missile.update():
                missiles.remove(missile)
                explosions.append(EnhancedExplosion(base.x, base.y, 1.5))
                metrics.missiles_evaded += 1
                recycle_missile(missile)

        # Update interceptors and check collisions
        for interceptor in interceptors[:]:
            interceptor.update()

            # Check missile collisions
            for missile in missiles[:]:
                if missile.active and missile.is_hostile and interceptor.active:
                    dist = math.sqrt(
                        (missile.x - interceptor.x) ** 2
                        + (missile.y - interceptor.y) ** 2
                    )
                    if dist < 30:
                        explosion_x = (missile.x + interceptor.x) / 2
                        explosion_y = (missile.y + interceptor.y) / 2
                        explosions.append(
                            EnhancedExplosion(explosion_x, explosion_y, 1.0)
                        )

                        missile.active = False
                        interceptor.active = False
                        metrics.missiles_intercepted += 1

                        # Remove missiles
                        missiles.remove(missile)
                        interceptors.remove(interceptor)
                        recycle_missile(missile)
                        recycle_missile(interceptor)
                        break

            if not interceptor.active and interceptor in interceptors:
                interceptors.remove(interceptor)
                recycle_missile(interceptor)

        # Update explosions
        for explosion in explosions[:]:
            if explosion.update():
                explosions.remove(explosion)

        # Update equations
        equations_solved_this_frame = 0
        for equation in equations[:]:
            equation.update()
            if equation.solved:
                equations_solved_this_frame += 1
                equations.remove(equation)
                # Add new equation
                new_y = 100 + len(equations) * 130
                equations.append(PhysicsEquation(WIDTH // 2 + 50, new_y))

        # Update metrics
        metrics.update(len(missiles), len(equations), equations_solved_this_frame)

        # Clear screen with enhanced background
        screen.fill(COLORS["background"])

        # Draw animated grid background
        grid_offset_x = (current_time // 50) % 40
        grid_offset_y = (current_time // 50) % 40

        for x in range(-grid_offset_x, WIDTH + 40, 40):
            pygame.draw.line(screen, COLORS["grid"], (x, 0), (x, HEIGHT), 1)
        for y in range(-grid_offset_y, HEIGHT + 40, 40):
            pygame.draw.line(screen, COLORS["grid"], (0, y), (WIDTH, y), 1)

        # Draw terrain
        terrain_points = [(0, HEIGHT)] + terrain + [(WIDTH, HEIGHT)]
        pygame.draw.polygon(screen, COLORS["terrain"], terrain_points)

        # Draw terrain details
        for i in range(0, len(terrain) - 1, 3):
            x, y = terrain[i]
            pygame.draw.line(screen, (20, 90, 40), (x, y), (x, y - 10), 1)

        # Draw main UI panels
        left_panel_area = draw_enhanced_panel(
            screen,
            20,
            20,
            420,
            HEIGHT - 40,
            "SUCCEDRA DEFENSE SYSTEM",
            "Advanced Algorithmic Missile Defense",
        )

        right_panel_area = draw_enhanced_panel(
            screen,
            WIDTH - 520,
            20,
            500,
            HEIGHT - 40,
            "COMPUTATIONAL PHYSICS ENGINE",
            "Real-time Trajectory Analysis",
        )

        # Draw radar in left panel
        radar.draw(screen)

        # Draw threat summary
        threat_text = FONTS["header"].render("THREAT SUMMARY", True, COLORS["accent"])
        screen.blit(threat_text, (left_panel_area[0], 250))

        # Draw threat type indicators
        pygame.draw.rect(screen, COLORS["hostile"], (left_panel_area[0], 290, 15, 15))
        missile_text = FONTS["small"].render(
            f"Missiles: {sum(1 for m in missiles if m.threat_type=='missile')}",
            True,
            COLORS["text_primary"],
        )
        screen.blit(missile_text, (left_panel_area[0] + 25, 290))

        pygame.draw.rect(screen, COLORS["drone"], (left_panel_area[0], 315, 15, 15))
        drone_text = FONTS["small"].render(
            f"Drones: {sum(1 for m in missiles if m.threat_type=='drone')}",
            True,
            COLORS["text_primary"],
        )
        screen.blit(drone_text, (left_panel_area[0] + 25, 315))

        pygame.draw.rect(screen, COLORS["aircraft"], (left_panel_area[0], 340, 15, 15))
        aircraft_text = FONTS["small"].render(
            f"Aircraft: {sum(1 for m in missiles if m.threat_type=='aircraft')}",
            True,
            COLORS["text_primary"],
        )
        screen.blit(aircraft_text, (left_panel_area[0] + 25, 340))

        # Draw system metrics
        metrics_start_y = 380

        draw_metric_display(
            screen,
            left_panel_area[0],
            metrics_start_y,
            left_panel_area[2],
            45,
            "Active Targets",
            len(missiles),
            20,
            "",
            (5, 15),
        )

        draw_metric_display(
            screen,
            left_panel_area[0],
            metrics_start_y + 55,
            left_panel_area[2],
            45,
            "CPU Usage",
            metrics.cpu_usage,
            100,
            "%",
            (60, 80),
        )

        draw_metric_display(
            screen,
            left_panel_area[0],
            metrics_start_y + 110,
            left_panel_area[2],
            45,
            "GPU Processing",
            metrics.gpu_usage,
            100,
            "%",
            (60, 80),
        )

        draw_metric_display(
            screen,
            left_panel_area[0],
            metrics_start_y + 165,
            left_panel_area[2],
            45,
            "Equations Solved",
            metrics.equations_solved,
            1000,
            "",
            None,
        )

        draw_metric_display(
            screen,
            left_panel_area[0],
            metrics_start_y + 220,
            left_panel_area[2],
            45,
            "Processing Speed",
            metrics.processing_speed,
            100,
            "%",
            (40, 70),
        )

        # Draw defense stats
        draw_metric_display(
            screen,
            left_panel_area[0],
            metrics_start_y + 275,
            left_panel_area[2] // 2 - 5,
            45,
            "Intercepted",
            metrics.missiles_intercepted,
            metrics.total_threats,
            "",
            None,
        )

        draw_metric_display(
            screen,
            left_panel_area[0] + left_panel_area[2] // 2 + 5,
            metrics_start_y + 275,
            left_panel_area[2] // 2 - 5,
            45,
            "Evaded",
            metrics.missiles_evaded,
            metrics.total_threats,
            "",
            (5, 10),
        )

        # Draw control buttons
        button_y = metrics_start_y + 330
        button_width = left_panel_area[2] // 3 - 10

        auto_button = draw_enhanced_button(
            screen,
            left_panel_area[0],
            button_y,
            button_width,
            35,
            "AUTO",
            auto_mode,
            "success" if auto_mode else "default",
        )

        threat_colors = ["success", "warning", "danger"]
        threat_labels = ["LOW", "MED", "HIGH"]
        for i in range(3):
            button_x = left_panel_area[0] + (i + 1) * (button_width + 10)
            if i < 2:  # Only show LOW and MED buttons if we have space
                button_x = (
                    left_panel_area[0] + button_width + 15 + i * (button_width + 10)
                )
                threat_button = draw_enhanced_button(
                    screen,
                    button_x,
                    button_y,
                    button_width,
                    35,
                    threat_labels[i],
                    threat_level == i,
                    threat_colors[i],
                )

        # Draw HIGH threat button on next row
        high_button = draw_enhanced_button(
            screen,
            left_panel_area[0],
            button_y + 45,
            button_width,
            35,
            "HIGH",
            threat_level == 2,
            "danger",
        )

        # Draw status information
        status_y = button_y + 90
        status_texts = [
            f"Threat Level: {['LOW', 'MEDIUM', 'HIGH'][threat_level]}",
            f"Active Missiles: {len([m for m in missiles if m.active and m.threat_type=='missile'])}",
            f"Active Drones: {len([m for m in missiles if m.active and m.threat_type=='drone'])}",
            f"Interceptors: {len([i for i in interceptors if i.active])}",
            f"Defense Mode: {'AUTOMATIC' if auto_mode else 'MANUAL'}",
            f"System Status: {'OPERATIONAL' if len(missiles) < 15 else 'OVERLOADED'}",
        ]

        for i, text in enumerate(status_texts):
            color = COLORS["text_primary"]
            if "OVERLOADED" in text:
                color = COLORS["danger"]
            elif "OPERATIONAL" in text:
                color = COLORS["success"]

            status_surf = FONTS["small"].render(text, True, color)
            screen.blit(status_surf, (left_panel_area[0], status_y + i * 22))

        # Draw physics equations in right panel
        for equation in equations:
            equation.draw(screen)

        # Draw game objects
        base.draw(screen)

        # Draw missiles and interceptors
        for missile in missiles:
            missile.draw(screen)

        for interceptor in interceptors:
            interceptor.draw(screen)

        # Draw explosions
        for explosion in explosions:
            explosion.draw(screen)

        # Draw radar sweep lines from base to missiles
        for missile in missiles:
            if missile.active and missile.is_hostile:
                # Draw tracking line
                pygame.draw.line(
                    screen,
                    COLORS["accent"],
                    (base.x, base.y),
                    (missile.x, missile.y),
                    1,
                )

                # Draw missile info
                info_texts = [
                    f"{missile.threat_type.upper()}",
                    f"M:{missile.mass}kg",
                    f"V:{missile.velocity}m/s",
                    f"A:{missile.altitude}m",
                ]

                for i, info_text in enumerate(info_texts):
                    info_surf = FONTS["tiny"].render(
                        info_text, True, COLORS["text_secondary"]
                    )
                    screen.blit(info_surf, (missile.x + 15, missile.y - 30 + i * 12))

        # Draw performance info
        frame_count += 1
        if frame_count % 30 == 0:  # Update every 30 frames
            fps_display = int(clock.get_fps())

        fps_text = FONTS["small"].render(
            f"FPS: {fps_display}", True, COLORS["text_secondary"]
        )
        screen.blit(fps_text, (WIDTH - 100, HEIGHT - 30))

        # Draw instructions
        instructions = [
            "CONTROLS:",
            "A - Toggle Auto Mode",
            "1/2/3 - Threat Levels",
            "SPACE - Manual Launch",
            "ESC - Exit",
        ]

        instruction_y = HEIGHT - 140
        for i, instruction in enumerate(instructions):
            color = COLORS["accent"] if i == 0 else COLORS["text_secondary"]
            font = FONTS["small"] if i == 0 else FONTS["tiny"]
            inst_surf = font.render(instruction, True, color)
            screen.blit(inst_surf, (20, instruction_y + i * 16))

        # Draw alert messages
        if len(missiles) > 10:
            alert_text = "⚠ CRITICAL: Multiple Incoming Threats!"
            alert_surf = FONTS["header"].render(alert_text, True, COLORS["danger"])
            alert_rect = alert_surf.get_rect(center=(WIDTH // 2, 50))

            # Draw alert background
            pygame.draw.rect(
                screen,
                (80, 20, 20, 180),
                (
                    alert_rect.x - 20,
                    alert_rect.y - 10,
                    alert_rect.width + 40,
                    alert_rect.height + 20,
                ),
                border_radius=8,
            )
            screen.blit(alert_surf, alert_rect)

        elif len(missiles) > 5:
            warning_text = "⚡ WARNING: High Threat Activity"
            warning_surf = FONTS["main"].render(warning_text, True, COLORS["warning"])
            warning_rect = warning_surf.get_rect(center=(WIDTH // 2, 50))
            screen.blit(warning_surf, warning_rect)

        # Draw title and version
        title_surf = FONTS["title"].render("SUCCEDRA v2.1", True, COLORS["accent"])
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, HEIGHT - 45))

        subtitle_surf = FONTS["small"].render(
            "Advanced Algorithmic Defense Matrix", True, COLORS["text_secondary"]
        )
        screen.blit(
            subtitle_surf, (WIDTH // 2 - subtitle_surf.get_width() // 2, HEIGHT - 25)
        )

        # Update display
        pygame.display.flip()
        clock.tick(60)

    # Cleanup
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
