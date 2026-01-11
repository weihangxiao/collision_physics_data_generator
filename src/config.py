"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           YOUR TASK CONFIGURATION                             ║
║                                                                               ║
║  CUSTOMIZE THIS FILE to define your task-specific settings.                   ║
║  Inherits common settings from core.GenerationConfig                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from pydantic import Field
from core import GenerationConfig


class TaskConfig(GenerationConfig):
    """
    Your task-specific configuration.
    
    CUSTOMIZE THIS CLASS to add your task's hyperparameters.
    
    Inherited from GenerationConfig:
        - num_samples: int          # Number of samples to generate
        - domain: str               # Task domain name
        - difficulty: Optional[str] # Difficulty level
        - random_seed: Optional[int] # For reproducibility
        - output_dir: Path          # Where to save outputs
        - image_size: tuple[int, int] # Image dimensions
    """
    
    # ══════════════════════════════════════════════════════════════════════════
    #  OVERRIDE DEFAULTS
    # ══════════════════════════════════════════════════════════════════════════

    domain: str = Field(default="collision_physics")
    image_size: tuple[int, int] = Field(default=(800, 300))
    
    # ══════════════════════════════════════════════════════════════════════════
    #  VIDEO SETTINGS
    # ══════════════════════════════════════════════════════════════════════════
    
    generate_videos: bool = Field(
        default=True,
        description="Whether to generate ground truth videos"
    )
    
    video_fps: int = Field(
        default=10,
        description="Video frame rate"
    )
    
    # ══════════════════════════════════════════════════════════════════════════
    #  TASK-SPECIFIC SETTINGS
    # ══════════════════════════════════════════════════════════════════════════

    # Ball properties
    min_mass: float = Field(default=1.0, description="Minimum ball mass (kg)")
    max_mass: float = Field(default=5.0, description="Maximum ball mass (kg)")
    min_velocity: float = Field(default=2.0, description="Minimum initial velocity (m/s)")
    max_velocity: float = Field(default=8.0, description="Maximum initial velocity (m/s)")

    # Visual settings
    ball_radius_base: int = Field(default=30, description="Base ball radius in pixels")
    show_velocity_arrows: bool = Field(default=True, description="Show velocity arrows on first frame")
    show_mass_labels: bool = Field(default=True, description="Show mass labels on balls")

    # Animation settings
    collision_type: str = Field(default="elastic", description="Type of collision: elastic or inelastic")
    simulation_duration: float = Field(default=3.0, description="Simulation duration in seconds")
    pixels_per_meter: float = Field(default=50.0, description="Pixels per meter for rendering")
