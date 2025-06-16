import pygame
import math
import random
import sys
from pygame import gfxdraw
from collections import deque

# Initialize Pygame
pygame.init()
pygame.font.init()

# Screen dimensions
WIDTH, HEIGHT = 1400, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SUCCEDRA: Advanced Algorithmic Missile Defense System")

# Enhanced Color Palette
COLORS = {
    "background": (8, 12, 24),
    "panel_bg": (15, 20, 35, 220),
    "panel_border": (40, 80, 140),
    "text_primary": (220, 235, 255),
    "text_secondary": (160, 180, 220),
    "accent": (0, 180, 255),
    "success": (80, 220, 120),
    "warning": (255, 180, 40),
    "danger": (255, 80, 80),
    "hostile": (255, 60, 60),
    "interceptor": (60, 160, 255),
    "base": (40, 200, 120),
    "solved": (120, 255, 150),
    "processing": (255, 200, 50),
    "grid": (25, 35, 55),
    "glow": (100, 200, 255, 100),
    "drone": (255, 150, 40),
    "aircraft": (180, 180, 220),
    "terrain": (30, 120, 60),
}

# Enhanced Fonts
FONTS = {
    "title": pygame.font.SysFont("Arial", 32, bold=True),
    "header": pygame.font.SysFont("Arial", 22, bold=True),
    "main": pygame.font.SysFont("Arial", 18),
    "equation": pygame.font.SysFont("Consolas", 16),
    "small": pygame.font.SysFont("Arial", 14),
    "tiny": pygame.font.SysFont("Arial", 12),
}

# Enhanced Equation Templates with Real Physics
PHYSICS_EQUATIONS = [
    {
        "eq": "F = ma",
        "context": "Force calculation",
        "vars": {"m": "2500kg", "a": "45m/s²"},
        "solution": "F = 112,500 N",
    },
    {
        "eq": "v² = u² + 2as",
        "context": "Kinematic motion",
        "vars": {"u": "0m/s", "a": "9.8m/s²", "s": "1200m"},
        "solution": "v = 153.3 m/s",
    },
    {
        "eq": "x = x₀ + v₀t + ½at²",
        "context": "Position tracking",
        "vars": {"x₀": "0m", "v₀": "850m/s", "a": "-9.8m/s²"},
        "solution": "x = 850t - 4.9t²",
    },
    {
        "eq": "E = ½mv²",
        "context": "Kinetic energy",
        "vars": {"m": "1800kg", "v": "3400m/s"},
        "solution": "E = 10.404 GJ",
    },
    {
        "eq": "p = mv",
        "context": "Momentum calculation",
        "vars": {"m": "2200kg", "v": "2800m/s"},
        "solution": "p = 6.16e6 kg·m/s",
    },
    {
        "eq": "Δx = v₀t + ½at²",
        "context": "Trajectory computation",
        "vars": {"v₀": "450m/s", "a": "32m/s²"},
        "solution": "Δx = 450t + 16t²",
    },
    {
        "eq": "θ = arctan(y/x)",
        "context": "Angle determination",
        "vars": {"y": "1250m", "x": "2100m"},
        "solution": "θ = 30.76°",
    },
    {
        "eq": "t = (v - u)/a",
        "context": "Time to intercept",
        "vars": {"v": "3200m/s", "u": "0m/s", "a": "85m/s²"},
        "solution": "t = 37.65 s",
    },
    {
        "eq": "R = v²sin(2θ)/g",
        "context": "Range calculation",
        "vars": {"v": "2800m/s", "θ": "45°", "g": "9.8m/s²"},
        "solution": "R = 800 km",
    },
    {
        "eq": "h = v²sin²(θ)/2g",
        "context": "Max height",
        "vars": {"v": "1900m/s", "θ": "60°", "g": "9.8m/s²"},
        "solution": "h = 147.2 km",
    },
]

COMPUTATION_STAGES = [
    "Initializing parameters",
    "Parsing equation structure",
    "Variable substitution",
    "Mathematical transformation",
    "Numerical computation",
    "Solution verification",
    "Result validation",
    "Output generation",
]

# Object pools for performance
PARTICLE_POOL = []
MISSILE_POOL = []


def get_particle(x, y, color, particle_type="default"):
    """Get particle from pool or create new one"""
    if PARTICLE_POOL:
        particle = PARTICLE_POOL.pop()
        particle.__init__(x, y, color, particle_type)
        return particle
    return EnhancedParticle(x, y, color, particle_type)


def recycle_particle(particle):
    """Return particle to pool"""
    PARTICLE_POOL.append(particle)


def get_missile(
    start_x, start_y, target_x, target_y, is_hostile=True, threat_type="missile"
):
    """Get missile from pool or create new one"""
    if MISSILE_POOL:
        missile = MISSILE_POOL.pop()
        missile.__init__(start_x, start_y, target_x, target_y, is_hostile, threat_type)
        return missile
    return EnhancedMissile(
        start_x, start_y, target_x, target_y, is_hostile, threat_type
    )


def recycle_missile(missile):
    """Return missile to pool"""
    missile.active = False
    missile.particles = []
    missile.trail = []
    MISSILE_POOL.append(missile)


class EnhancedParticle:
    def __init__(self, x, y, color, particle_type="default"):
        self.x = x
        self.y = y
        self.color = color
        self.type = particle_type
        self.size = random.uniform(0.5, 3.0)
        self.life = random.randint(80, 150)
        self.max_life = self.life

        if particle_type == "engine":
            self.vx = random.uniform(-3, 3)
            self.vy = random.uniform(-3, 3)
            self.size = random.uniform(1, 4)
        elif particle_type == "explosion":
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 12)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            self.size = random.uniform(2, 6)
        else:
            self.vx = random.uniform(-1, 1)
            self.vy = random.uniform(-1, 1)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 2

        if self.type == "explosion":
            self.vx *= 0.98
            self.vy *= 0.98

        self.size = max(0, self.size - 0.03)
        return self.life <= 0

    def draw(self, surface):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            color = (*self.color[:3], min(255, alpha))

            if self.size > 0:
                try:
                    pygame.gfxdraw.filled_circle(
                        surface, int(self.x), int(self.y), int(self.size), color
                    )
                except (ValueError, OverflowError):
                    pass


class EnhancedMissile:
    def __init__(
        self,
        start_x,
        start_y,
        target_x,
        target_y,
        is_hostile=True,
        threat_type="missile",
    ):
        self.x = start_x
        self.y = start_y
        self.start_x = start_x
        self.start_y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.is_hostile = is_hostile
        self.threat_type = threat_type
        self.active = True
        self.particles = []
        self.trail = []
        self.fuel = 100.0
        self.gravity = 0.1 if threat_type == "missile" else 0.05
        self.acceleration = 0.05 if not is_hostile else 0.02
        self.velocity_x = 0
        self.velocity_y = 0

        # Enhanced missile properties based on threat type
        if threat_type == "missile":
            self.speed = (
                random.uniform(2.0, 3.5) if is_hostile else random.uniform(3.0, 4.5)
            )
            self.color = COLORS["hostile"] if is_hostile else COLORS["interceptor"]
            self.size = 6
            self.mass = random.randint(800, 2500)  # kg
            self.velocity = random.randint(800, 3500)  # m/s
            self.altitude = random.randint(1000, 15000)  # m
        elif threat_type == "drone":
            self.speed = random.uniform(1.0, 2.0)
            self.color = COLORS["drone"]
            self.size = 4
            self.mass = random.randint(50, 200)  # kg
            self.velocity = random.randint(100, 300)  # m/s
            self.altitude = random.randint(100, 1000)  # m
        else:  # aircraft
            self.speed = random.uniform(0.5, 1.5)
            self.color = COLORS["aircraft"]
            self.size = 8
            self.mass = random.randint(5000, 20000)  # kg
            self.velocity = random.randint(200, 800)  # m/s
            self.altitude = random.randint(5000, 12000)  # m

        # Calculate initial direction
        dx = target_x - start_x
        dy = target_y - start_y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            self.vx = dx / dist * self.speed
            self.vy = dy / dist * self.speed
        else:
            self.vx = self.vy = 0

        self.launch_time = pygame.time.get_ticks()
        self.last_particle_time = 0

    def update(self):
        if not self.active:
            return False

        # Apply gravity
        self.vy += self.gravity

        # Apply acceleration
        self.vx *= 1 + self.acceleration
        self.vy *= 1 + self.acceleration

        # Consume fuel
        self.fuel = max(0, self.fuel - 0.1)
        if self.fuel <= 0 and self.is_hostile:
            self.active = False
            return False

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Add to trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 80:
            self.trail.pop(0)

        # Create engine particles
        current_time = pygame.time.get_ticks()
        if current_time - self.last_particle_time > 50 and self.fuel > 0:
            self.last_particle_time = current_time
            particle_color = (255, 120, 30) if self.is_hostile else (80, 180, 255)
            px = self.x - self.vx * 8 + random.uniform(-3, 3)
            py = self.y - self.vy * 8 + random.uniform(-3, 3)
            self.particles.append(get_particle(px, py, particle_color, "engine"))

        # Update particles
        for particle in self.particles[:]:
            if particle.update():
                self.particles.remove(particle)
                recycle_particle(particle)

        # Check if reached target
        dist_to_target = math.sqrt(
            (self.target_x - self.x) ** 2 + (self.target_y - self.y) ** 2
        )
        if dist_to_target < 8:
            self.active = False
            return True

        # Check bounds
        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.active = False

        return False

    def draw(self, surface):
        if not self.active:
            return

        # Draw trail with fade effect
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)) * 0.7)
            trail_color = (*self.color[:3], alpha)
            size = max(1, int(3 * (i / len(self.trail))))

            try:
                pygame.gfxdraw.filled_circle(
                    surface, int(trail_x), int(trail_y), size, trail_color
                )
            except (ValueError, OverflowError):
                pass

        # Draw particles
        for particle in self.particles:
            particle.draw(surface)

        # Draw missile body with shape based on threat type
        if self.threat_type == "missile":
            pygame.gfxdraw.filled_circle(
                surface, int(self.x), int(self.y), self.size, self.color
            )

            # Draw directional indicator
            angle = math.atan2(self.vy, self.vx)
            tip_x = self.x + 15 * math.cos(angle)
            tip_y = self.y + 15 * math.sin(angle)
            pygame.draw.line(surface, self.color, (self.x, self.y), (tip_x, tip_y), 3)
        elif self.threat_type == "drone":
            # Draw drone as a diamond shape
            points = [
                (self.x, self.y - self.size * 1.5),
                (self.x + self.size, self.y),
                (self.x, self.y + self.size * 1.5),
                (self.x - self.size, self.y),
            ]
            pygame.draw.polygon(surface, self.color, points)
        else:  # aircraft
            # Draw aircraft as a winged shape
            pygame.draw.ellipse(
                surface,
                self.color,
                (
                    self.x - self.size * 1.5,
                    self.y - self.size // 2,
                    self.size * 3,
                    self.size,
                ),
            )
            pygame.draw.polygon(
                surface,
                self.color,
                [
                    (self.x + self.size * 1.5, self.y),
                    (self.x + self.size * 3, self.y),
                    (self.x + self.size * 1.5, self.y + self.size),
                ],
            )
            pygame.draw.polygon(
                surface,
                self.color,
                [
                    (self.x + self.size * 1.5, self.y),
                    (self.x + self.size * 3, self.y),
                    (self.x + self.size * 1.5, self.y - self.size),
                ],
            )

        # Draw glow effect
        glow_color = (*self.color[:3], 50)
        try:
            pygame.gfxdraw.filled_circle(
                surface, int(self.x), int(self.y), self.size + 4, glow_color
            )
        except (ValueError, OverflowError):
            pass

        # Draw fuel gauge
        if self.fuel < 50 and not self.is_hostile:
            pygame.draw.rect(surface, (40, 40, 50), (self.x - 10, self.y - 15, 20, 4))
            pygame.draw.rect(
                surface,
                COLORS["warning"] if self.fuel < 20 else COLORS["success"],
                (self.x - 10, self.y - 15, 20 * (self.fuel / 100), 4),
            )


class PhysicsEquation:
    def __init__(self, x, y, width=380, height=120):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.equation_data = random.choice(PHYSICS_EQUATIONS)
        self.stage = 0
        self.progress = 0
        self.solved = False
        self.stage_timer = 0
        self.stage_duration = random.randint(45, 90)
        self.computation_speed = random.uniform(0.8, 1.5)
        self.start_time = pygame.time.get_ticks()
        self.solution_steps = []
        self.current_step = 0
        self.generate_solution_steps()

    def generate_solution_steps(self):
        # Generate simulated solution steps
        self.solution_steps = [
            f"Analyzing: {self.equation_data['eq']}",
            f"Context: {self.equation_data['context']}",
            "Processing variables...",
        ]

        for var, val in self.equation_data["vars"].items():
            self.solution_steps.append(f"Substituting: {var} = {val}")

        self.solution_steps.append("Applying kinematic equations...")
        self.solution_steps.append("Solving differential equations...")
        self.solution_steps.append("Verifying with numerical methods...")
        self.solution_steps.append(f"Result: {self.equation_data['solution']}")

    def update(self):
        if self.solved:
            return

        self.stage_timer += 1
        self.progress = min(100, self.progress + self.computation_speed)

        # Progress through solution steps
        if self.progress > (self.current_step + 1) * (100 / len(self.solution_steps)):
            self.current_step = min(len(self.solution_steps) - 1, self.current_step + 1)

        if self.progress >= 100:
            self.solved = True

    def draw(self, surface):
        # Draw main panel
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, COLORS["panel_bg"], panel_rect, border_radius=8)
        pygame.draw.rect(
            surface, COLORS["panel_border"], panel_rect, 2, border_radius=8
        )

        # Draw equation
        eq_text = FONTS["equation"].render(
            f"{self.equation_data['eq']}", True, COLORS["text_primary"]
        )
        surface.blit(eq_text, (self.x + 15, self.y + 10))

        # Draw context
        context_text = FONTS["small"].render(
            f"{self.equation_data['context']}", True, COLORS["text_secondary"]
        )
        surface.blit(context_text, (self.x + 15, self.y + 32))

        # Draw solution steps
        if self.current_step < len(self.solution_steps):
            step_text = self.solution_steps[self.current_step]
            step_surf = FONTS["tiny"].render(
                step_text,
                True,
                COLORS["solved"] if self.solved else COLORS["processing"],
            )
            surface.blit(step_surf, (self.x + 15, self.y + 52))

        # Draw progress bar
        bar_rect = pygame.Rect(
            self.x + 15, self.y + self.height - 20, self.width - 30, 12
        )
        pygame.draw.rect(surface, (30, 40, 60), bar_rect, border_radius=6)

        progress_width = (self.width - 30) * (self.progress / 100)
        progress_rect = pygame.Rect(
            self.x + 15, self.y + self.height - 20, progress_width, 12
        )
        progress_color = COLORS["solved"] if self.solved else COLORS["processing"]
        pygame.draw.rect(surface, progress_color, progress_rect, border_radius=6)

        # Draw status
        status_text = FONTS["small"].render(
            "SOLVED" if self.solved else f"Stage: {COMPUTATION_STAGES[self.stage]}",
            True,
            COLORS["solved"] if self.solved else COLORS["processing"],
        )
        surface.blit(
            status_text,
            (self.x + self.width - status_text.get_width() - 15, self.y + 10),
        )


class DefenseBase:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 25
        self.particles = []
        self.radar_angle = 0
        self.activity_level = 0
        self.last_radar_time = 0

    def update(self):
        current_time = pygame.time.get_ticks()

        # Update radar at a slower rate
        if current_time - self.last_radar_time > 50:
            self.radar_angle = (self.radar_angle + 5) % 360
            self.last_radar_time = current_time

        # Generate base activity particles
        if random.random() < 0.3:
            px = self.x + random.randint(-20, 20)
            py = self.y + random.randint(0, 30)
            self.particles.append(get_particle(px, py, COLORS["base"]))

        # Update particles
        for particle in self.particles[:]:
            if particle.update():
                self.particles.remove(particle)
                recycle_particle(particle)

    def draw(self, surface):
        # Draw base structure
        pygame.draw.circle(surface, (20, 60, 40), (self.x, self.y + 10), 25)
        pygame.draw.rect(surface, COLORS["base"], (self.x - 20, self.y + 15, 40, 20))

        # Draw radar dish
        pygame.draw.circle(surface, COLORS["base"], (self.x, self.y), self.radius, 3)
        pygame.draw.circle(surface, (40, 120, 80), (self.x, self.y), self.radius - 10)

        # Draw radar sweep
        end_x = self.x + (self.radius + 15) * math.cos(math.radians(self.radar_angle))
        end_y = self.y + (self.radius + 15) * math.sin(math.radians(self.radar_angle))
        pygame.draw.line(
            surface, COLORS["success"], (self.x, self.y), (end_x, end_y), 2
        )

        # Draw particles
        for particle in self.particles:
            particle.draw(surface)

        # Draw base label
        label_text = FONTS["tiny"].render(
            "DEFENSE BASE", True, COLORS["text_secondary"]
        )
        surface.blit(label_text, (self.x - 35, self.y + 40))


class EnhancedExplosion:
    def __init__(self, x, y, size=1.0):
        self.x = x
        self.y = y
        self.particles = []
        self.radius = 0
        self.max_radius = 50 * size
        self.active = True

        # Create explosion particles
        particle_count = int(150 * size)
        for _ in range(particle_count):
            self.particles.append(get_particle(x, y, (255, 150, 50), "explosion"))

        # Add some bright white core particles
        for _ in range(int(50 * size)):
            self.particles.append(get_particle(x, y, (255, 255, 255), "explosion"))

    def update(self):
        self.radius = min(self.max_radius, self.radius + 2.5)
        for particle in self.particles[:]:
            if particle.update():
                self.particles.remove(particle)
                recycle_particle(particle)

        if len(self.particles) == 0 and self.radius >= self.max_radius:
            self.active = False

        return not self.active

    def draw(self, surface):
        # Draw particles
        for particle in self.particles:
            particle.draw(surface)

        # Draw shockwave
        if self.radius < self.max_radius:
            for i in range(3):
                ring_radius = self.radius - i * 8
                if ring_radius > 0:
                    alpha = max(0, 100 - i * 30)
                    color = (255, 200, 100, alpha)
                    try:
                        pygame.gfxdraw.aacircle(
                            surface, int(self.x), int(self.y), int(ring_radius), color
                        )
                    except (ValueError, OverflowError):
                        pass


class ThreatRadar:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.blips = []
        self.radar_sweep_angle = 0
        self.last_sweep_time = 0

    def add_blip(self, threat_type, angle, distance):
        # Different symbols for different threats
        symbols = {"missile": "▲", "drone": "◇", "aircraft": "○"}
        self.blips.append(
            {
                "symbol": symbols[threat_type],
                "type": threat_type,
                "angle": angle,
                "distance": distance,
                "life": 200,  # Frames to display the blip
            }
        )

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_sweep_time > 30:
            self.radar_sweep_angle = (self.radar_sweep_angle + 4) % 360
            self.last_sweep_time = current_time

        # Update blip lifetimes
        for blip in self.blips[:]:
            blip["life"] -= 1
            if blip["life"] <= 0:
                self.blips.remove(blip)

    def draw(self, surface):
        # Draw radar background
        pygame.draw.circle(surface, (20, 30, 60), (self.x, self.y), self.radius)
        pygame.draw.circle(
            surface, COLORS["panel_border"], (self.x, self.y), self.radius, 2
        )

        # Draw range rings
        for r in range(1, 4):
            pygame.draw.circle(
                surface, COLORS["grid"], (self.x, self.y), self.radius * r / 4, 1
            )

        # Draw radar sweep
        sweep_x = self.x + self.radius * math.cos(math.radians(self.radar_sweep_angle))
        sweep_y = self.y + self.radius * math.sin(math.radians(self.radar_sweep_angle))
        pygame.draw.line(
            surface, COLORS["success"], (self.x, self.y), (sweep_x, sweep_y), 2
        )

        # Draw cardinal directions
        for angle in [0, 90, 180, 270]:
            rad = math.radians(angle)
            text = FONTS["tiny"].render(
                ["N", "E", "S", "W"][angle // 90], True, COLORS["text_secondary"]
            )
            x = self.x + (self.radius + 15) * math.cos(rad) - text.get_width() // 2
            y = self.y + (self.radius + 15) * math.sin(rad) - text.get_height() // 2
            surface.blit(text, (x, y))

        # Draw blips
        for blip in self.blips:
            rad = math.radians(blip["angle"])
            dist = blip["distance"] * self.radius
            x = self.x + dist * math.cos(rad)
            y = self.y + dist * math.sin(rad)

            # Determine color by threat type
            if blip["type"] == "missile":
                color = COLORS["hostile"]
            elif blip["type"] == "drone":
                color = COLORS["drone"]
            else:
                color = COLORS["aircraft"]

            text = FONTS["small"].render(blip["symbol"], True, color)
            surface.blit(text, (x - text.get_width() // 2, y - text.get_height() // 2))


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


def classify_threat(velocity, altitude):
    """Determine threat type based on characteristics"""
    if velocity > 2500:  # Hypersonic
        return "missile"
    elif altitude < 1000 and velocity < 300:
        return "drone"
    else:
        return "aircraft"


def calculate_intercept_point(start_x, start_y, target, speed):
    """Predict intercept point using relative velocity"""
    # Simple prediction: assume target continues on current vector
    dist = math.sqrt((target.x - start_x) ** 2 + (target.y - start_y) ** 2)
    time_to_intercept = dist / speed

    # Predict future position
    future_x = target.x + target.vx * time_to_intercept
    future_y = target.y + target.vy * time_to_intercept

    return future_x, future_y


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

            if not interceptor.active:
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
