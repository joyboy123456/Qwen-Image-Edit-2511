"""
Property-Based Tests for Workflow Parameter Injection

Feature: ai-product-view-webapp
Property 10: Workflow prompt injection
Property 11: Workflow parameter injection
Validates: Requirements 6.3, 6.4

These tests verify that user-provided parameters are correctly injected
into the ComfyUI workflow template.
"""

import copy
from hypothesis import given, settings, strategies as st

import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.workflow_executor import (
    inject_workflow_parameters,
    _inject_prompt,
    _inject_ksampler_params,
)
from backend.workflow_template import get_workflow_template


# ============================================================================
# Property 10: Workflow prompt injection
# Feature: ai-product-view-webapp, Property 10: Workflow prompt injection
# Validates: Requirements 6.3
#
# *For any* user-provided prompt string, THE Backend SHALL correctly inject
# it into the TextEncodeQwenImageEditPlus node's "text" input field in the
# workflow JSON.
# ============================================================================

@given(prompt=st.text(min_size=0, max_size=1000))
@settings(max_examples=100)
def test_property_10_workflow_prompt_injection(prompt: str):
    """
    Property 10: Workflow prompt injection
    
    For any user-provided prompt string, the Backend SHALL correctly inject
    it into the TextEncodeQwenImageEditPlus node's "text" input field.
    
    Feature: ai-product-view-webapp, Property 10: Workflow prompt injection
    Validates: Requirements 6.3
    """
    # Arrange: Get a fresh workflow template
    workflow = get_workflow_template()
    
    # Act: Inject the prompt
    result = _inject_prompt(copy.deepcopy(workflow), prompt)
    
    # Assert: The prompt is correctly injected into node 115
    assert "115" in result, "TextEncodeQwenImageEditPlus node (115) must exist"
    assert "inputs" in result["115"], "Node 115 must have inputs"
    assert "text" in result["115"]["inputs"], "Node 115 must have text input"
    assert result["115"]["inputs"]["text"] == prompt, \
        f"Prompt must be injected exactly. Expected '{prompt}', got '{result['115']['inputs']['text']}'"


@given(prompt=st.text(min_size=0, max_size=1000))
@settings(max_examples=100)
def test_property_10_full_workflow_prompt_injection(prompt: str):
    """
    Property 10: Workflow prompt injection (full workflow)
    
    Verifies prompt injection through the main inject_workflow_parameters function.
    
    Feature: ai-product-view-webapp, Property 10: Workflow prompt injection
    Validates: Requirements 6.3
    """
    # Arrange
    workflow = get_workflow_template()
    input_image = "test_image.png"
    
    # Act: Use the main injection function
    result = inject_workflow_parameters(
        workflow=workflow,
        input_image=input_image,
        prompt=prompt,
        steps=8,
        cfg=3.0,
        seed=12345,
    )
    
    # Assert: The prompt is correctly injected
    assert result["115"]["inputs"]["text"] == prompt, \
        f"Prompt must be injected via main function. Expected '{prompt}', got '{result['115']['inputs']['text']}'"


# ============================================================================
# Property 11: Workflow parameter injection
# Feature: ai-product-view-webapp, Property 11: Workflow parameter injection
# Validates: Requirements 6.4
#
# *For any* user-provided parameters (steps, cfg_scale, seed), THE Backend
# SHALL correctly inject them into the KSampler node's corresponding input
# fields in the workflow JSON.
# ============================================================================

@given(
    steps=st.integers(min_value=4, max_value=8),
    cfg=st.floats(min_value=1.0, max_value=5.0, allow_nan=False, allow_infinity=False),
    seed=st.integers(min_value=0, max_value=2**63 - 1)
)
@settings(max_examples=100)
def test_property_11_workflow_parameter_injection(steps: int, cfg: float, seed: int):
    """
    Property 11: Workflow parameter injection
    
    For any user-provided parameters (steps, cfg_scale, seed), the Backend
    SHALL correctly inject them into the KSampler node's corresponding input fields.
    
    Feature: ai-product-view-webapp, Property 11: Workflow parameter injection
    Validates: Requirements 6.4
    """
    # Arrange: Get a fresh workflow template
    workflow = get_workflow_template()
    
    # Act: Inject the KSampler parameters
    result = _inject_ksampler_params(copy.deepcopy(workflow), steps, cfg, seed)
    
    # Assert: All parameters are correctly injected into node 14 (KSampler)
    assert "14" in result, "KSampler node (14) must exist"
    assert "inputs" in result["14"], "Node 14 must have inputs"
    
    ksampler_inputs = result["14"]["inputs"]
    
    # Verify steps
    assert "steps" in ksampler_inputs, "KSampler must have steps input"
    assert ksampler_inputs["steps"] == steps, \
        f"Steps must be injected exactly. Expected {steps}, got {ksampler_inputs['steps']}"
    
    # Verify cfg
    assert "cfg" in ksampler_inputs, "KSampler must have cfg input"
    assert ksampler_inputs["cfg"] == cfg, \
        f"CFG must be injected exactly. Expected {cfg}, got {ksampler_inputs['cfg']}"
    
    # Verify seed
    assert "seed" in ksampler_inputs, "KSampler must have seed input"
    assert ksampler_inputs["seed"] == seed, \
        f"Seed must be injected exactly. Expected {seed}, got {ksampler_inputs['seed']}"


@given(
    steps=st.integers(min_value=4, max_value=8),
    cfg=st.floats(min_value=1.0, max_value=5.0, allow_nan=False, allow_infinity=False),
    seed=st.integers(min_value=0, max_value=2**63 - 1)
)
@settings(max_examples=100)
def test_property_11_full_workflow_parameter_injection(steps: int, cfg: float, seed: int):
    """
    Property 11: Workflow parameter injection (full workflow)
    
    Verifies parameter injection through the main inject_workflow_parameters function.
    
    Feature: ai-product-view-webapp, Property 11: Workflow parameter injection
    Validates: Requirements 6.4
    """
    # Arrange
    workflow = get_workflow_template()
    input_image = "test_image.png"
    prompt = "Next Scene：将镜头向左旋转45度"
    
    # Act: Use the main injection function
    result = inject_workflow_parameters(
        workflow=workflow,
        input_image=input_image,
        prompt=prompt,
        steps=steps,
        cfg=cfg,
        seed=seed,
    )
    
    # Assert: All KSampler parameters are correctly injected
    ksampler_inputs = result["14"]["inputs"]
    
    assert ksampler_inputs["steps"] == steps, \
        f"Steps must be injected via main function. Expected {steps}, got {ksampler_inputs['steps']}"
    assert ksampler_inputs["cfg"] == cfg, \
        f"CFG must be injected via main function. Expected {cfg}, got {ksampler_inputs['cfg']}"
    assert ksampler_inputs["seed"] == seed, \
        f"Seed must be injected via main function. Expected {seed}, got {ksampler_inputs['seed']}"


# ============================================================================
# Additional property tests for edge cases
# ============================================================================

@given(prompt=st.text(alphabet=st.characters(blacklist_categories=('Cs',)), min_size=0, max_size=500))
@settings(max_examples=100)
def test_property_10_unicode_prompt_injection(prompt: str):
    """
    Property 10 (edge case): Unicode prompt injection
    
    Verifies that prompts with various Unicode characters are correctly injected.
    
    Feature: ai-product-view-webapp, Property 10: Workflow prompt injection
    Validates: Requirements 6.3
    """
    workflow = get_workflow_template()
    
    result = inject_workflow_parameters(
        workflow=workflow,
        input_image="test.png",
        prompt=prompt,
        steps=8,
        cfg=3.0,
        seed=42,
    )
    
    assert result["115"]["inputs"]["text"] == prompt, \
        "Unicode prompts must be preserved exactly"


@given(seed=st.one_of(
    st.integers(min_value=0, max_value=2**63 - 1),
    st.just(None)
))
@settings(max_examples=100)
def test_property_11_seed_none_handling(seed):
    """
    Property 11 (edge case): Seed None handling
    
    Verifies that when seed is None, a random seed is generated.
    
    Feature: ai-product-view-webapp, Property 11: Workflow parameter injection
    Validates: Requirements 6.4
    """
    workflow = get_workflow_template()
    
    result = inject_workflow_parameters(
        workflow=workflow,
        input_image="test.png",
        prompt="test prompt",
        steps=8,
        cfg=3.0,
        seed=seed,
    )
    
    ksampler_seed = result["14"]["inputs"]["seed"]
    
    # Seed should always be an integer after injection
    assert isinstance(ksampler_seed, int), \
        f"Seed must be an integer after injection, got {type(ksampler_seed)}"
    
    # If seed was provided, it should match
    if seed is not None:
        assert ksampler_seed == seed, \
            f"Provided seed must be preserved. Expected {seed}, got {ksampler_seed}"
    else:
        # If seed was None, a random seed should be generated (just verify it's valid)
        assert 0 <= ksampler_seed < 2**63, \
            f"Generated seed must be in valid range, got {ksampler_seed}"
