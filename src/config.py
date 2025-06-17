WIDTH, HEIGHT = 1400, 900


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
