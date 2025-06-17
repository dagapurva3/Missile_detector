from collections import deque
import random
import math
import pygame

from config import COLORS

FONTS = {
    "title": pygame.font.SysFont("Arial", 32, bold=True),
    "header": pygame.font.SysFont("Arial", 22, bold=True),
    "main": pygame.font.SysFont("Arial", 18),
    "equation": pygame.font.SysFont("Consolas", 16),
    "small": pygame.font.SysFont("Arial", 14),
    "tiny": pygame.font.SysFont("Arial", 12),
}


class SystemMetrics:
    def __init__(self):
        self.equations_solved = 0
        self.targets_tracked = 0
        self.cpu_usage = 0
        self.gpu_usage = 0
        self.processing_speed = 0
        self.threat_level = 1
        self.last_update = pygame.time.get_ticks()
        self.missiles_intercepted = 0
        self.missiles_evaded = 0
        self.total_threats = 0

    def update(self, missiles_count, equations_count, solved_count):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_update > 500:
            self.targets_tracked = missiles_count
            self.equations_solved += solved_count
            self.processing_speed = min(100, solved_count * 10 + random.randint(0, 20))
            self.cpu_usage = min(95, 25 + missiles_count * 8 + random.randint(-5, 10))
            self.gpu_usage = min(90, 30 + equations_count * 5 + random.randint(-5, 8))
            self.last_update = current_time


def draw_enhanced_panel(surface, x, y, width, height, title, subtitle=""):
    # Draw panel with gradient effect
    panel_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, COLORS["panel_bg"], panel_rect, border_radius=12)
    pygame.draw.rect(surface, COLORS["panel_border"], panel_rect, 2, border_radius=12)

    # Draw title
    title_surf = FONTS["header"].render(title, True, COLORS["accent"])
    surface.blit(title_surf, (x + 20, y + 15))

    # Draw subtitle if provided
    if subtitle:
        subtitle_surf = FONTS["small"].render(subtitle, True, COLORS["text_secondary"])
        surface.blit(subtitle_surf, (x + 20, y + 40))

    return (
        x + 15,
        y + (65 if subtitle else 50),
        width - 30,
        height - (80 if subtitle else 65),
    )


def draw_metric_display(
    surface, x, y, width, height, title, value, max_value, unit="", color_threshold=None
):
    # Draw metric background
    pygame.draw.rect(surface, (20, 30, 50), (x, y, width, height), border_radius=6)

    # Determine color based on value
    if color_threshold:
        if value < color_threshold[0]:
            bar_color = COLORS["success"]
        elif value < color_threshold[1]:
            bar_color = COLORS["warning"]
        else:
            bar_color = COLORS["danger"]
    else:
        bar_color = COLORS["accent"]

    # Draw title
    title_surf = FONTS["small"].render(title, True, COLORS["text_primary"])
    surface.blit(title_surf, (x + 10, y + 8))

    # Draw value
    if isinstance(value, float):
        value_text = f"{value:.1f}{unit}"
    elif isinstance(value, int):
        value_text = f"{value}{unit}"
    else:
        value_text = str(value)

    value_surf = FONTS["main"].render(value_text, True, bar_color)
    surface.blit(value_surf, (x + width - value_surf.get_width() - 10, y + 5))

    # Draw progress bar
    bar_height = 6
    bar_y = y + height - bar_height - 8
    pygame.draw.rect(
        surface, (40, 50, 80), (x + 10, bar_y, width - 20, bar_height), border_radius=3
    )

    if max_value > 0:
        bar_width = (width - 20) * min(1.0, value / max_value)
        pygame.draw.rect(
            surface, bar_color, (x + 10, bar_y, bar_width, bar_height), border_radius=3
        )


def draw_enhanced_button(
    surface, x, y, width, height, text, active=False, color_scheme="default"
):
    colors = {
        "default": (70, 90, 140),
        "success": (40, 120, 80),
        "warning": (140, 100, 40),
        "danger": (140, 60, 60),
    }

    base_color = colors.get(color_scheme, colors["default"])
    button_color = tuple(min(255, c + 40) for c in base_color) if active else base_color

    # Draw button
    button_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, button_color, button_rect, border_radius=6)
    pygame.draw.rect(surface, COLORS["panel_border"], button_rect, 2, border_radius=6)

    # Draw text
    text_surf = FONTS["small"].render(text, True, COLORS["text_primary"])
    text_x = x + width // 2 - text_surf.get_width() // 2
    text_y = y + height // 2 - text_surf.get_height() // 2
    surface.blit(text_surf, (text_x, text_y))

    return button_rect


def draw_3d_globe(surface, center_x, center_y, radius):
    # Draw globe base
    pygame.draw.circle(surface, (15, 30, 60), (center_x, center_y), radius)

    # Draw continents with more detail
    continents = [
        (center_x - radius * 0.6, center_y - radius * 0.4, radius * 0.4, radius * 0.3),
        (center_x - radius * 0.1, center_y - radius * 0.7, radius * 0.6, radius * 0.4),
        (center_x + radius * 0.2, center_y + radius * 0.1, radius * 0.5, radius * 0.4),
        (center_x - radius * 0.8, center_y + radius * 0.3, radius * 0.3, radius * 0.2),
    ]

    for continent in continents:
        pygame.draw.ellipse(surface, (40, 100, 60), continent)

    # Draw latitude lines
    for i in range(-4, 5):
        y_offset = i * radius // 6
        if abs(y_offset) < radius:
            line_width = int(math.sqrt(radius * radius - y_offset * y_offset))
            pygame.draw.arc(
                surface,
                COLORS["grid"],
                (center_x - line_width, center_y + y_offset - 1, line_width * 2, 2),
                0,
                math.pi,
                1,
            )

    # Draw longitude lines
    for i in range(8):
        angle = i * math.pi / 4
        start_x = center_x + radius * 0.8 * math.cos(angle)
        start_y = center_y + radius * 0.8 * math.sin(angle)
        end_x = center_x - radius * 0.8 * math.cos(angle)
        end_y = center_y - radius * 0.8 * math.sin(angle)
        pygame.draw.line(surface, COLORS["grid"], (start_x, start_y), (end_x, end_y), 1)

    # Draw outer border with glow
    pygame.draw.circle(surface, COLORS["panel_border"], (center_x, center_y), radius, 2)
    pygame.draw.circle(surface, COLORS["glow"], (center_x, center_y), radius + 3, 1)


def generate_terrain(width, height, base_height, roughness=0.5):
    """Generate procedural terrain using midpoint displacement algorithm"""
    terrain = []
    points = deque()

    # Start with left and right points
    points.append((0, base_height + random.randint(-20, 20)))
    points.append((width, base_height + random.randint(-20, 20)))

    # Midpoint displacement
    while points:
        left = points.popleft()
        right = points[0] if points else None

        if right and right[0] - left[0] > 10:
            mid_x = (left[0] + right[0]) / 2
            mid_y = (left[1] + right[1]) / 2 + random.randint(
                -int(roughness * 20), int(roughness * 20)
            )
            points.append(left)
            points.append((mid_x, mid_y))
            points.append((mid_x, mid_y))
            points.append(right)
        else:
            terrain.append(left)

    return terrain
