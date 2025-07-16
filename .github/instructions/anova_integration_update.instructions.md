---
applyTo: '**'
---

# Anova Integration Update Instructions

## Objective
Update the custom Anova integration to fully comply with the latest Home Assistant standards and best practices. The integration must be reliable, maintainable, and user-friendly.

## Context
There is an official Anova integration in Home Assistant (`homeassistant/components/anova`), but it is read-only and cannot control the device. You may use it for inspiration, but note that its architecture and capabilities differ from the custom integration.

The custom integration to be updated is located at `homeassistant/components/anova_custom`. This integration is currently broken and needs to be modernized to support device control.

Test files for the custom integration are located at `tests/components/anova_custom`.

## Background
The current integration is broken in recent Home Assistant releases and cannot be used to schedule or control the Anova cooker. The Anova is a sous-vide device, and users need to set temperature, cooking time, and monitor device status from Home Assistant.

## Requirements
- Implement temperature and time control for cooking
- Provide real-time status monitoring of the cooker
- Support binary sensors for cooker status (e.g., running, finished, error)
- Expose a climate entity for temperature control
- Use Home Assistant's latest integration architecture and patterns (config flow, update coordinator, unique IDs, device registry, diagnostics, translations, etc.)
- Follow all relevant quality scale rules for the integration's tier

## Coding Guidelines
- Use clear, descriptive names for all entities and variables
- Add type hints and docstrings to all functions and classes
- Write concise, user-focused comments explaining the "why" behind decisions
- Ensure all code is asynchronous and non-blocking
- Use Home Assistant constants and helpers where available
- Structure code according to Home Assistant integration templates
- Provide tests with >95% coverage for all modules

## Style & Documentation
- Use American English for all code, comments, and documentation
- Write for clarity and inclusivity; avoid abbreviations and jargon
- Format user-facing messages for non-native English speakers
- Add translation keys for all entities and errors

## Deliverables
- Updated integration code in the correct directory structure
- Manifest and quality_scale.yaml reflecting compliance
- Comprehensive tests in the appropriate test directory
- Updated documentation and translation files

