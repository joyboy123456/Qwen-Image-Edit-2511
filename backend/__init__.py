# AI 商品视角转换 Web 应用 - Modal 后端
# Backend for AI Product View Transformation Web Application

from .types import (
    Perspective,
    GenerateRequest,
    GeneratedImage,
    GenerateResponse,
    ErrorResponse,
)

from .workflow_template import (
    get_workflow_template,
    INPUT_IMAGE_PLACEHOLDER,
    PROMPT_PLACEHOLDER,
    SEED_PLACEHOLDER,
    STEPS_PLACEHOLDER,
    CFG_PLACEHOLDER,
    OUTPUT_PREFIX_PLACEHOLDER,
    DEFAULT_STEPS,
    DEFAULT_CFG,
)

from .workflow_executor import (
    inject_workflow_parameters,
    create_workflow,
    save_workflow_to_file,
    load_workflow_from_file,
    validate_workflow_parameters,
    NODE_IDS,
)

__all__ = [
    # Types
    "Perspective",
    "GenerateRequest",
    "GeneratedImage",
    "GenerateResponse",
    "ErrorResponse",
    # Workflow template
    "get_workflow_template",
    "INPUT_IMAGE_PLACEHOLDER",
    "PROMPT_PLACEHOLDER",
    "SEED_PLACEHOLDER",
    "STEPS_PLACEHOLDER",
    "CFG_PLACEHOLDER",
    "OUTPUT_PREFIX_PLACEHOLDER",
    "DEFAULT_STEPS",
    "DEFAULT_CFG",
    # Workflow executor
    "inject_workflow_parameters",
    "create_workflow",
    "save_workflow_to_file",
    "load_workflow_from_file",
    "validate_workflow_parameters",
    "NODE_IDS",
]
