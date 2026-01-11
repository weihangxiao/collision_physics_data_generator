"""
Collision Physics Task implementation.

Files:
    - config.py   : Task-specific configuration (TaskConfig)
    - generator.py: Collision physics generation logic (CollisionPhysicsGenerator)
    - prompts.py  : Task prompts/instructions (get_prompt)
"""

from .config import TaskConfig
from .generator import CollisionPhysicsGenerator
from .prompts import get_prompt

# Backward compatibility alias
TaskGenerator = CollisionPhysicsGenerator

__all__ = ["TaskConfig", "CollisionPhysicsGenerator", "TaskGenerator", "get_prompt"]
