# Collision Physics Task Generator ⚛️

A data generator for creating synthetic physics reasoning tasks where two balls collide elastically. This task tests a model's ability to understand momentum conservation, energy conservation, and predict collision outcomes through visual animation.

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/vm-dataset/collision-physics-data-generator.git
cd collision-physics-data-generator

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# 4. Generate tasks
python examples/generate.py --num-samples 50
```

---

## 📋 Task Description

The **Collision Physics Task** is a physics reasoning task where:

- **Initial State**: Two balls with different masses and velocities approaching each other
- **Goal**: Predict the collision outcome following elastic collision physics
- **Animation**: Balls approach, collide, and separate with new velocities
- **Solution**: Exactly **one unique solution** - determined by conservation of momentum and energy

### Key Features

- ✅ **Unique Solution**: Physics equations guarantee one correct outcome for given initial conditions
- ✅ **Clear Visual Reasoning**: Shows masses (via labels and size), velocities (via arrows), and collision dynamics
- ✅ **Scalable**: 1000+ unique samples with varying masses and velocities
- ✅ **Fast Generation**: ~1-2 samples/second using pymunk physics engine
- ✅ **Short Videos**: ~3 seconds per video (well under 10s limit)

---

## 📁 Project Structure

```
collision-physics-data-generator/
├── core/                    # Core utilities (framework code)
│   ├── base_generator.py   # Abstract base class
│   ├── schemas.py          # Pydantic models
│   ├── image_utils.py      # Image rendering helpers
│   ├── video_utils.py      # Video generation utilities
│   └── output_writer.py    # File output management
├── src/                     # Task-specific implementation
│   ├── generator.py        # Collision physics task generator
│   ├── prompts.py          # Task instruction prompts
│   └── config.py           # Task configuration
├── examples/
│   └── generate.py         # Entry point script
└── data/                    # Generated output
    └── questions/
        └── collision_physics_task/
            └── collision_physics_0000/
                ├── first_frame.png
                ├── final_frame.png
                ├── prompt.txt
                └── ground_truth.mp4
```

---

## 📦 Output Format

Each generated task produces:

```
data/questions/collision_physics_task/{task_id}/
├── first_frame.png          # Initial state: balls before collision with velocity arrows
├── final_frame.png          # Final state: balls after collision (both visible)
├── prompt.txt               # Task instructions with specific parameters
└── ground_truth.mp4         # Solution animation video (~3 seconds)
```

### Output Details

- **first_frame.png**: Shows the initial positions of two balls with:
  - Ball colors (red and blue)
  - Mass labels (e.g., "2.5kg")
  - Ball size proportional to mass
  - Velocity arrows indicating direction and speed

- **final_frame.png**: Shows the post-collision state with:
  - Balls separated and both visible in frame
  - Post-collision velocity arrows
  - Same mass labels for reference

- **prompt.txt**: Contains specific collision parameters:
  ```
  Ball A (4.8kg, 4.8 m/s right) and Ball B (2.3kg, 3.5 m/s left)
  undergo an elastic collision. Show the final velocities after impact.
  ```

- **ground_truth.mp4**: Animated video showing:
  - Balls approaching (approach phase)
  - Elastic collision (collision moment)
  - Balls separating with new velocities (separation phase)
  - **Total duration: ~3.0 seconds at 10 FPS**

---

## ⚙️ Configuration

All task parameters are configured in `src/config.py`:

```python
class TaskConfig(GenerationConfig):
    domain: str = "collision_physics"
    image_size: tuple[int, int] = (800, 300)

    # Ball properties
    min_mass: float = 1.0              # Minimum ball mass (kg)
    max_mass: float = 5.0              # Maximum ball mass (kg)
    min_velocity: float = 2.0          # Minimum initial velocity (m/s)
    max_velocity: float = 8.0          # Maximum initial velocity (m/s)

    # Visual settings
    ball_radius_base: int = 30         # Base ball radius in pixels
    show_velocity_arrows: bool = True  # Show velocity arrows
    show_mass_labels: bool = True      # Show mass labels on balls

    # Animation settings
    collision_type: str = "elastic"    # Type of collision
    simulation_duration: float = 3.0   # Simulation duration in seconds
    video_fps: int = 10                # Video frame rate
```

---

## 🎬 Generation Algorithm

The generator uses pymunk physics engine for accurate simulation:

1. **Random Parameter Generation**:
   - Mass A: 1.0-5.0 kg
   - Mass B: 1.0-5.0 kg
   - Velocity A: 2.0-8.0 m/s (rightward)
   - Velocity B: -2.0 to -8.0 m/s (leftward, to ensure collision)

2. **Physics Simulation**:
   - Create pymunk space with zero gravity
   - Add two ball bodies with calculated properties
   - Set elasticity = 1.0 (perfect elastic collision)
   - Run simulation for 3 seconds at 10 FPS (30 frames)

3. **Smart Final Frame Selection**:
   - Detect collision moment (minimum distance)
   - Find frame where balls are separated by 2m and both visible
   - Ensures meaningful final state (not empty frame)

4. **Rendering**:
   - Ball size scales with mass (visual cue)
   - Velocity arrows show direction and magnitude
   - Mass labels provide explicit information

### Key Physics Features

- ✅ **Conservation of Momentum**: `m₁v₁ + m₂v₂ = m₁v₁' + m₂v₂'`
- ✅ **Conservation of Energy**: `½m₁v₁² + ½m₂v₂² = ½m₁v₁'² + ½m₂v₂'²`
- ✅ **Elastic Collision**: Coefficient of restitution = 1.0
- ✅ **1D Collision**: Horizontal motion only (simplified but clear)

---

## 📝 Usage Examples

### Generate 100 tasks (default settings)

```bash
python examples/generate.py --num-samples 100
```

### Generate 500 tasks with custom output directory

```bash
python examples/generate.py --num-samples 500 --output data/my_output
```

### Generate with specific random seed (reproducibility)

```bash
python examples/generate.py --num-samples 200 --seed 42
```

### Generate without videos (faster, images only)

```bash
python examples/generate.py --num-samples 1000 --no-videos
```

---

## 🔧 Command Line Options

```bash
python examples/generate.py --help
```

Options:
- `--num-samples`: Number of task samples to generate (required)
- `--output`: Output directory (default: `data/questions`)
- `--seed`: Random seed for reproducibility (optional)
- `--no-videos`: Disable video generation (faster)

---

## 📚 Dependencies

See `requirements.txt` for the complete list. Main dependencies:

- `numpy`: Numerical operations
- `Pillow`: Image processing and rendering
- `pydantic`: Configuration management
- `opencv-python`: Video generation
- `pymunk`: 2D physics simulation engine (elastic collisions)

The pymunk library provides accurate rigid-body physics simulation, ensuring realistic collision outcomes.

---

## 🎯 Task Characteristics

### Scalability Analysis

- **Parameter Space**:
  - 5 mass values (1-5 kg) × 5 mass values × 7 velocity values × 7 velocity values
  - = **1225+ unique combinations**
- **Measured uniqueness**: 100% unique (physics is deterministic)
- **Actual samples**: Continuous ranges provide **infinite variations**

### Video Specifications

- **Frame breakdown**:
  - Approach phase: ~10-15 frames
  - Collision: ~1-2 frames
  - Separation phase: ~15-20 frames
- **Total**: 30 frames at 10 FPS = **3.0 seconds**
- **Status**: ✅ Well under 10-second limit

### Prompt Specifications

- **Average length**: ~35 words
- **Format**: "Ball A (mass X kg, velocity Y m/s direction) and Ball B (mass Z kg, velocity W m/s direction) undergo an elastic collision. Show the final velocities after impact."
- **Variation**: 4 different prompt templates
- **Status**: ✅ Well under 200-word limit

---

## 🎨 Visual Design

- **Background**: Pure white (255, 255, 255)
- **Ball Colors**: Red (220, 60, 60) and Blue (60, 60, 220)
- **Arrow Color**: Green (60, 180, 60) for velocity indicators
- **Ball Size**: 21-39 pixels radius (scales with mass)
- **Velocity Arrows**: Length proportional to speed (10 pixels per m/s)
- **Mass Labels**: White text on colored balls

---

## 📊 Quality Metrics

Based on 100-sample test:

| Metric | Result | Target | Status |
|--------|--------|--------|--------|
| Uniqueness | 100% | >95% | ✅ Pass |
| Video Length | 3.0s | <10s | ✅ Pass |
| Prompt Length | 35 words | <200 words | ✅ Pass |
| Generation Speed | ~1-2 samples/sec | N/A | ✅ Fast |
| Solution Uniqueness | 100% | 100% | ✅ Pass |
| Final Frame Quality | Both balls visible | N/A | ✅ Pass |

---

## 🏷️ Task Type

**Physics Worlds → CollisionPhysics → Elastic Collision**

- **Task Name**: Elastic Collision Prediction
- **Description**: Predict the outcome of an elastic collision between two balls with different masses and velocities
- **Reasoning Type**: Physics reasoning through momentum and energy conservation

---

## 🔬 Physics Accuracy

The simulation uses pymunk's rigid-body physics engine, which provides:
- Accurate elastic collision response
- Proper momentum conservation
- Energy conservation (within numerical precision)
- Realistic motion dynamics

This ensures that the ground truth videos show physically correct collision outcomes that can be verified using classical mechanics equations.

---

## 📄 License

See `LICENSE` file for details.