import random
import math
import pygame
from pygame import gfxdraw

from config import COLORS, HEIGHT, MISSILE_POOL, PARTICLE_POOL, WIDTH
pygame.init()
pygame.font.init()
FONTS = {
    "title": pygame.font.SysFont("Arial", 32, bold=True),
    "header": pygame.font.SysFont("Arial", 22, bold=True),
    "main": pygame.font.SysFont("Arial", 18),
    "equation": pygame.font.SysFont("Consolas", 16),
    "small": pygame.font.SysFont("Arial", 14),
    "tiny": pygame.font.SysFont("Arial", 12),
}


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
                    gfxdraw.filled_circle(
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
                gfxdraw.filled_circle(
                    surface, int(trail_x), int(trail_y), size, trail_color
                )
            except (ValueError, OverflowError):
                pass

        # Draw particles
        for particle in self.particles:
            particle.draw(surface)

        # Draw missile body with shape based on threat type
        if self.threat_type == "missile":
            gfxdraw.filled_circle(
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
            gfxdraw.filled_circle(
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
                        gfxdraw.aacircle(
                            surface, int(self.x), int(self.y), int(ring_radius), color
                        )
                    except (ValueError, OverflowError):
                        pass


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
