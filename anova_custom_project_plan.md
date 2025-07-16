# Anova Custom Integration Modernization Plan

## Context

- **Custom integration path:** `homeassistant/components/anova_custom`
- **Test files path:** `tests/components/anova_custom`
- **Official integration (read-only, for reference):** `homeassistant/components/anova`

## Analysis

### Key Issues
- Previously relied on `anova_wifi` library, which was outdated and incompatible.
- Now includes a vendored, modernized Anova WiFi implementation within the integration.
- Entity setup and coordinator patterns may not fully match latest Home Assistant standards.
- Config flow, device registry, diagnostics, and translation support may be incomplete or outdated.
- Test coverage and structure may not meet current requirements.
- Manifest and quality scale compliance need review.

### Required Features
- Device control (temperature, time, start/stop cooking)
- Real-time status monitoring
- Binary sensors for device state
- Climate entity for temperature control
- Modern config flow, update coordinator, unique IDs, device registry, diagnostics, translations

---

## Project Plan

| Task # | Task Description | Status |
|--------|------------------|--------|
| 1 | Audit and update `manifest.json` for required fields and compliance | Done |
| 2 | Refactor config flow for latest standards (unique ID, error handling, reauth, etc.) | Done |
| 3 | Update coordinator pattern for async, non-blocking, and device registry support | Done |
| 4 | Refactor entity setup for binary sensors, climate, and sensors (unique IDs, device info, translation keys) | Done |
| 5 | Implement diagnostics and repair issue reporting | Done |
| 6 | Review and update translation files (`strings.json`) | Done |
| 7 | Ensure all code uses type hints, docstrings, and follows async best practices | Done |
| 8 | Update and expand tests for >95% coverage, including config flow, entity tests and the custom anova_wifi_set module | Done |
| 9 | Review and update documentation | Not started |
| 10 | Validate with Home Assistant tools (hassfest, ruff, pylint, mypy, pytest) | Done |

---

## Progress Notes

- Plan created and confirmed by user on July 14, 2025.
- All code, config flow, coordinator, entities, diagnostics, translations, and type hints are complete and compliant.
- All tests are passing and coverage is above 95%.
- Validation with Home Assistant tools (hassfest, ruff, pylint, mypy, pytest) is complete and successful.
- Only documentation review and update remains.
