import random
import pygame

from config import COLORS, COMPUTATION_STAGES, PHYSICS_EQUATIONS

FONTS = {
    "title": pygame.font.SysFont("Arial", 32, bold=True),
    "header": pygame.font.SysFont("Arial", 22, bold=True),
    "main": pygame.font.SysFont("Arial", 18),
    "equation": pygame.font.SysFont("Consolas", 16),
    "small": pygame.font.SysFont("Arial", 14),
    "tiny": pygame.font.SysFont("Arial", 12),
}


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
