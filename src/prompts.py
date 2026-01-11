"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           COLLISION PHYSICS PROMPTS                           ║
║                                                                               ║
║  Prompts for elastic collision physics tasks.                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random


def get_prompt(mass_a: float, velocity_a: float, mass_b: float, velocity_b: float,
               collision_type: str = "elastic") -> str:
    """
    Generate a prompt for collision physics task.

    Args:
        mass_a: Mass of ball A in kg
        velocity_a: Velocity of ball A in m/s (positive = right)
        mass_b: Mass of ball B in kg
        velocity_b: Velocity of ball B in m/s (positive = right)
        collision_type: Type of collision ("elastic" or "inelastic")

    Returns:
        Formatted prompt string with specific parameters
    """
    # Determine direction descriptions
    dir_a = "right" if velocity_a > 0 else "left"
    dir_b = "right" if velocity_b > 0 else "left"

    # Absolute velocities for display
    abs_vel_a = abs(velocity_a)
    abs_vel_b = abs(velocity_b)

    # Choose a random template
    templates = [
        f"Two balls collide {collision_type}ally. Ball A (mass {mass_a:.1f}kg) moves {dir_a} at {abs_vel_a:.1f} m/s. Ball B (mass {mass_b:.1f}kg) moves {dir_b} at {abs_vel_b:.1f} m/s. Predict the collision outcome.",

        f"Ball A ({mass_a:.1f}kg, {abs_vel_a:.1f} m/s {dir_a}) and Ball B ({mass_b:.1f}kg, {abs_vel_b:.1f} m/s {dir_b}) undergo an {collision_type} collision. Show the final velocities after impact.",

        f"In an {collision_type} collision, Ball A (mass={mass_a:.1f}kg, velocity={velocity_a:.1f} m/s) collides with Ball B (mass={mass_b:.1f}kg, velocity={velocity_b:.1f} m/s). Animate the collision and resulting motion.",

        f"Predict the result of an {collision_type} collision between two balls: Ball A ({mass_a:.1f}kg) traveling {dir_a} at {abs_vel_a:.1f} m/s, and Ball B ({mass_b:.1f}kg) traveling {dir_b} at {abs_vel_b:.1f} m/s.",
    ]

    return random.choice(templates)


def get_simple_prompt() -> str:
    """Get a simple generic prompt (for fallback)."""
    return "Two balls collide elastically. Predict the collision outcome following physics rules."
