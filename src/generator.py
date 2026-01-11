"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     COLLISION PHYSICS TASK GENERATOR                          ║
║                                                                               ║
║  Generates elastic collision physics tasks using pymunk physics engine.        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import pymunk

from core import BaseGenerator, TaskPair, ImageRenderer
from core.video_utils import VideoGenerator
from .config import TaskConfig
from .prompts import get_prompt


class CollisionPhysicsGenerator(BaseGenerator):
    """
    Collision Physics Task Generator.

    Generates 1D elastic collision scenarios with two balls.
    """

    def __init__(self, config: TaskConfig):
        super().__init__(config)
        self.renderer = ImageRenderer(image_size=config.image_size)

        # Initialize video generator if enabled
        self.video_generator = None
        if config.generate_videos and VideoGenerator.is_available():
            self.video_generator = VideoGenerator(fps=config.video_fps, output_format="mp4")

        # Visual settings
        self.bg_color = (255, 255, 255)  # White background
        self.ball_colors = [(220, 60, 60), (60, 60, 220)]  # Red and Blue
        self.arrow_color = (60, 180, 60)  # Green for velocity arrows
        self.text_color = (40, 40, 40)

    def generate_task_pair(self, task_id: str) -> TaskPair:
        """Generate one collision physics task."""

        # Generate random collision scenario
        collision_data = self._generate_collision_scenario()

        # Run physics simulation to get trajectories
        trajectories = self._simulate_collision(collision_data)

        # Render first and final frames
        first_image = self._render_initial_state(collision_data)
        final_image = self._render_final_state(collision_data, trajectories)

        # Generate video if enabled
        video_path = None
        if self.config.generate_videos and self.video_generator:
            video_path = self._generate_video(collision_data, trajectories, task_id)

        # Get prompt with specific parameters
        prompt = get_prompt(
            collision_data["mass_a"],
            collision_data["velocity_a"],
            collision_data["mass_b"],
            collision_data["velocity_b"],
            self.config.collision_type
        )

        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=prompt,
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=video_path
        )

    # ══════════════════════════════════════════════════════════════════════════
    #  PHYSICS SIMULATION
    # ══════════════════════════════════════════════════════════════════════════

    def _generate_collision_scenario(self) -> dict:
        """Generate random collision parameters."""

        # Random masses
        mass_a = random.uniform(self.config.min_mass, self.config.max_mass)
        mass_b = random.uniform(self.config.min_mass, self.config.max_mass)

        # Random velocities (ensure they will collide)
        # Ball A starts on left, Ball B starts on right
        # Ball A moves right (positive), Ball B moves left (negative) to ensure collision
        velocity_a = random.uniform(self.config.min_velocity, self.config.max_velocity)
        velocity_b = -random.uniform(self.config.min_velocity, self.config.max_velocity)

        # Calculate ball radii based on mass (visual indication)
        radius_a = self._mass_to_radius(mass_a)
        radius_b = self._mass_to_radius(mass_b)

        # Initial positions (in meters)
        # Place balls so they will collide in the middle of the simulation
        pos_a = 2.0  # Ball A starts at 2m from left
        pos_b = 12.0  # Ball B starts at 12m from left (14m total width)

        return {
            "mass_a": mass_a,
            "mass_b": mass_b,
            "velocity_a": velocity_a,
            "velocity_b": velocity_b,
            "radius_a": radius_a,
            "radius_b": radius_b,
            "pos_a": pos_a,
            "pos_b": pos_b,
        }

    def _mass_to_radius(self, mass: float) -> float:
        """Convert mass to visual radius (in pixels)."""
        # Linearly scale radius with mass
        min_radius = self.config.ball_radius_base * 0.7
        max_radius = self.config.ball_radius_base * 1.3
        min_mass = self.config.min_mass
        max_mass = self.config.max_mass

        # Linear interpolation
        ratio = (mass - min_mass) / (max_mass - min_mass)
        radius = min_radius + (max_radius - min_radius) * ratio

        return int(radius)

    def _simulate_collision(self, scenario: dict) -> dict:
        """
        Simulate collision using pymunk physics engine.

        Returns trajectories (positions and velocities over time).
        """
        # Create pymunk space
        space = pymunk.Space()
        space.gravity = (0, 0)  # No gravity (1D horizontal collision)

        # Create balls as pymunk bodies
        # Ball A
        moment_a = pymunk.moment_for_circle(scenario["mass_a"], 0, scenario["radius_a"] / self.config.pixels_per_meter)
        body_a = pymunk.Body(scenario["mass_a"], moment_a)
        body_a.position = (scenario["pos_a"], 0)
        body_a.velocity = (scenario["velocity_a"], 0)
        shape_a = pymunk.Circle(body_a, scenario["radius_a"] / self.config.pixels_per_meter)
        shape_a.elasticity = 1.0 if self.config.collision_type == "elastic" else 0.5
        shape_a.friction = 0.0
        space.add(body_a, shape_a)

        # Ball B
        moment_b = pymunk.moment_for_circle(scenario["mass_b"], 0, scenario["radius_b"] / self.config.pixels_per_meter)
        body_b = pymunk.Body(scenario["mass_b"], moment_b)
        body_b.position = (scenario["pos_b"], 0)
        body_b.velocity = (scenario["velocity_b"], 0)
        shape_b = pymunk.Circle(body_b, scenario["radius_b"] / self.config.pixels_per_meter)
        shape_b.elasticity = 1.0 if self.config.collision_type == "elastic" else 0.5
        shape_b.friction = 0.0
        space.add(body_b, shape_b)

        # Run simulation
        dt = 1.0 / self.config.video_fps  # Time step per frame
        num_steps = int(self.config.simulation_duration * self.config.video_fps)

        trajectories = {
            "positions_a": [],
            "positions_b": [],
            "velocities_a": [],
            "velocities_b": [],
        }

        for _ in range(num_steps):
            space.step(dt)
            trajectories["positions_a"].append(body_a.position[0])
            trajectories["positions_b"].append(body_b.position[0])
            trajectories["velocities_a"].append(body_a.velocity[0])
            trajectories["velocities_b"].append(body_b.velocity[0])

        return trajectories

    # ══════════════════════════════════════════════════════════════════════════
    #  RENDERING
    # ══════════════════════════════════════════════════════════════════════════

    def _render_initial_state(self, scenario: dict) -> Image.Image:
        """Render initial state with velocity arrows."""
        img = Image.new("RGB", self.config.image_size, self.bg_color)
        draw = ImageDraw.Draw(img)

        # Get positions in pixels
        width, height = self.config.image_size
        center_y = height // 2

        x_a = self._meters_to_pixels(scenario["pos_a"])
        x_b = self._meters_to_pixels(scenario["pos_b"])

        # Draw balls
        self._draw_ball(draw, x_a, center_y, scenario["radius_a"],
                       self.ball_colors[0], scenario["mass_a"])
        self._draw_ball(draw, x_b, center_y, scenario["radius_b"],
                       self.ball_colors[1], scenario["mass_b"])

        # Draw velocity arrows
        if self.config.show_velocity_arrows:
            self._draw_velocity_arrow(draw, x_a, center_y, scenario["velocity_a"],
                                     scenario["radius_a"])
            self._draw_velocity_arrow(draw, x_b, center_y, scenario["velocity_b"],
                                     scenario["radius_b"])

        return img

    def _render_final_state(self, scenario: dict, trajectories: dict) -> Image.Image:
        """Render final state after collision (when balls are separated but still visible)."""
        img = Image.new("RGB", self.config.image_size, self.bg_color)
        draw = ImageDraw.Draw(img)

        # Find the best frame for final state:
        # After collision, when balls are separated but both still visible
        final_frame_idx = self._find_final_frame_index(scenario, trajectories)

        # Get positions at that frame
        width, height = self.config.image_size
        center_y = height // 2

        final_x_a = self._meters_to_pixels(trajectories["positions_a"][final_frame_idx])
        final_x_b = self._meters_to_pixels(trajectories["positions_b"][final_frame_idx])

        # Draw balls
        self._draw_ball(draw, final_x_a, center_y, scenario["radius_a"],
                       self.ball_colors[0], scenario["mass_a"])
        self._draw_ball(draw, final_x_b, center_y, scenario["radius_b"],
                       self.ball_colors[1], scenario["mass_b"])

        # Optionally draw final velocity arrows
        if self.config.show_velocity_arrows:
            final_vel_a = trajectories["velocities_a"][final_frame_idx]
            final_vel_b = trajectories["velocities_b"][final_frame_idx]
            self._draw_velocity_arrow(draw, final_x_a, center_y, final_vel_a,
                                     scenario["radius_a"])
            self._draw_velocity_arrow(draw, final_x_b, center_y, final_vel_b,
                                     scenario["radius_b"])

        return img

    def _find_final_frame_index(self, scenario: dict, trajectories: dict) -> int:
        """
        Find the best frame for the final state image.

        Criteria:
        1. After collision (balls moving apart)
        2. Both balls still visible in frame
        3. Balls are well-separated

        Returns the frame index to use for the final state.
        """
        positions_a = trajectories["positions_a"]
        positions_b = trajectories["positions_b"]

        # World boundaries (with margin for ball radius)
        world_width = 14.0
        radius_margin_a = (scenario["radius_a"] / self.config.pixels_per_meter)
        radius_margin_b = (scenario["radius_b"] / self.config.pixels_per_meter)

        # Find when collision happens (minimum distance between ball centers)
        distances = [abs(positions_b[i] - positions_a[i]) for i in range(len(positions_a))]
        collision_idx = distances.index(min(distances))

        # After collision, find a good frame where:
        # - Balls are separated by at least 2m (well separated)
        # - Both balls are still in frame
        separation_threshold = 2.0  # meters

        for i in range(collision_idx, len(positions_a)):
            pos_a = positions_a[i]
            pos_b = positions_b[i]

            # Check if both balls are in frame
            in_frame_a = (radius_margin_a <= pos_a <= world_width - radius_margin_a)
            in_frame_b = (radius_margin_b <= pos_b <= world_width - radius_margin_b)

            # Check if separated enough
            distance = abs(pos_b - pos_a)
            well_separated = distance >= separation_threshold

            if in_frame_a and in_frame_b and well_separated:
                return i

        # Fallback: use last frame where both balls are visible
        for i in range(len(positions_a) - 1, collision_idx, -1):
            pos_a = positions_a[i]
            pos_b = positions_b[i]

            in_frame_a = (radius_margin_a <= pos_a <= world_width - radius_margin_a)
            in_frame_b = (radius_margin_b <= pos_b <= world_width - radius_margin_b)

            if in_frame_a and in_frame_b:
                return i

        # Last resort: use frame right after collision
        return min(collision_idx + 10, len(positions_a) - 1)

    def _draw_ball(self, draw: ImageDraw.Draw, x: float, y: float,
                   radius: float, color: tuple, mass: float):
        """Draw a ball with optional mass label."""
        # Draw circle
        draw.ellipse([x - radius, y - radius, x + radius, y + radius],
                    fill=color, outline=(0, 0, 0), width=2)

        # Draw mass label
        if self.config.show_mass_labels:
            font = self._get_font(int(radius * 0.5))
            text = f"{mass:.1f}kg"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = x - text_width // 2
            text_y = y - text_height // 2
            draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)

    def _draw_velocity_arrow(self, draw: ImageDraw.Draw, x: float, y: float,
                            velocity: float, radius: float):
        """Draw a velocity arrow."""
        # Arrow length proportional to velocity
        arrow_scale = 10  # pixels per m/s
        arrow_length = velocity * arrow_scale

        # Arrow starts from edge of ball
        start_x = x + radius if velocity > 0 else x - radius
        end_x = start_x + arrow_length

        # Don't draw if velocity is too small
        if abs(arrow_length) < 5:
            return

        # Draw arrow line
        draw.line([start_x, y, end_x, y], fill=self.arrow_color, width=3)

        # Draw arrowhead
        arrow_size = 8
        if velocity > 0:  # Right arrow
            draw.polygon([
                (end_x, y),
                (end_x - arrow_size, y - arrow_size // 2),
                (end_x - arrow_size, y + arrow_size // 2)
            ], fill=self.arrow_color)
        else:  # Left arrow
            draw.polygon([
                (end_x, y),
                (end_x + arrow_size, y - arrow_size // 2),
                (end_x + arrow_size, y + arrow_size // 2)
            ], fill=self.arrow_color)

        # Draw velocity label
        font = self._get_font(14)
        vel_text = f"{abs(velocity):.1f}m/s"
        label_y = y - 25
        bbox = draw.textbbox((0, 0), vel_text, font=font)
        text_width = bbox[2] - bbox[0]
        label_x = (start_x + end_x) / 2 - text_width / 2
        draw.text((label_x, label_y), vel_text, fill=self.arrow_color, font=font)

    def _meters_to_pixels(self, meters: float) -> float:
        """Convert meters to pixel coordinates."""
        # Map world coordinates to image coordinates
        # Assume world is 14m wide, centered in image
        width = self.config.image_size[0]
        world_width = 14.0  # meters
        return (meters / world_width) * width

    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get a font for text rendering."""
        font_paths = [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "Arial.ttf",
        ]

        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, size)
            except (OSError, IOError):
                continue

        return ImageFont.load_default()

    # ══════════════════════════════════════════════════════════════════════════
    #  VIDEO GENERATION
    # ══════════════════════════════════════════════════════════════════════════

    def _generate_video(self, scenario: dict, trajectories: dict, task_id: str) -> str:
        """Generate ground truth video showing collision."""
        temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        video_path = temp_dir / f"{task_id}_ground_truth.mp4"

        # Create animation frames
        frames = self._create_animation_frames(scenario, trajectories)

        result = self.video_generator.create_video_from_frames(frames, video_path)
        return str(result) if result else None

    def _create_animation_frames(self, scenario: dict, trajectories: dict) -> list:
        """Create animation frames showing the collision."""
        frames = []
        width, height = self.config.image_size
        center_y = height // 2

        num_frames = len(trajectories["positions_a"])

        for i in range(num_frames):
            # Create frame
            img = Image.new("RGB", self.config.image_size, self.bg_color)
            draw = ImageDraw.Draw(img)

            # Get positions for this frame
            x_a = self._meters_to_pixels(trajectories["positions_a"][i])
            x_b = self._meters_to_pixels(trajectories["positions_b"][i])

            # Draw balls
            self._draw_ball(draw, x_a, center_y, scenario["radius_a"],
                           self.ball_colors[0], scenario["mass_a"])
            self._draw_ball(draw, x_b, center_y, scenario["radius_b"],
                           self.ball_colors[1], scenario["mass_b"])

            frames.append(img)

        return frames
