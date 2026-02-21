"""Tests for trv_internal_temperature attribute.

In offset-based calibration mode, the TRV reports displayed_temp = internal + offset.
This attribute exposes the raw internal temperature (before offset) for TRVs using
LOCAL_BASED calibration. Not available in external temperature mode.
"""

import pytest

from custom_components.smarter_thermostat.utils.const import (
    ATTR_TRV_INTERNAL_TEMPERATURE,
    CalibrationType,
)
from custom_components.smarter_thermostat.utils.helpers import get_trv_internal_temperatures


class TestTrvInternalTemperatureConstant:
    """Tests for the attribute constant."""

    def test_constant_defined(self):
        """ATTR_TRV_INTERNAL_TEMPERATURE is defined and used as attribute key."""
        assert ATTR_TRV_INTERNAL_TEMPERATURE == "trv_internal_temperature"
        assert isinstance(ATTR_TRV_INTERNAL_TEMPERATURE, str)


class TestGetTrvInternalTemperatures:
    """Tests for get_trv_internal_temperatures helper."""

    def test_computes_internal_from_reported_minus_offset(self):
        """internal = reported - offset."""
        real_trvs = {
            "climate.trv_1": {
                "advanced": {"calibration": CalibrationType.LOCAL_BASED},
                "current_temperature": 22.0,
                "last_calibration": 2.0,
            },
        }
        result = get_trv_internal_temperatures(real_trvs)
        assert result == {"climate.trv_1": 20.0}

    def test_excludes_target_temp_based_trvs(self):
        """TRVs with TARGET_TEMP_BASED calibration are excluded."""
        real_trvs = {
            "climate.trv_target": {
                "advanced": {"calibration": CalibrationType.TARGET_TEMP_BASED},
                "current_temperature": 22.0,
                "last_calibration": 2.0,
            },
        }
        result = get_trv_internal_temperatures(real_trvs)
        assert result == {}

    def test_excludes_direct_valve_based_trvs(self):
        """TRVs with DIRECT_VALVE_BASED calibration are excluded."""
        real_trvs = {
            "climate.trv_valve": {
                "advanced": {"calibration": CalibrationType.DIRECT_VALVE_BASED},
                "current_temperature": 22.0,
                "last_calibration": 2.0,
            },
        }
        result = get_trv_internal_temperatures(real_trvs)
        assert result == {}

    def test_excludes_trv_with_missing_current_temperature(self):
        """TRVs without current_temperature are excluded."""
        real_trvs = {
            "climate.trv_1": {
                "advanced": {"calibration": CalibrationType.LOCAL_BASED},
                "current_temperature": None,
                "last_calibration": 2.0,
            },
        }
        result = get_trv_internal_temperatures(real_trvs)
        assert result == {}

    def test_excludes_trv_with_missing_last_calibration(self):
        """TRVs without last_calibration are excluded."""
        real_trvs = {
            "climate.trv_1": {
                "advanced": {"calibration": CalibrationType.LOCAL_BASED},
                "current_temperature": 22.0,
                "last_calibration": None,
            },
        }
        result = get_trv_internal_temperatures(real_trvs)
        assert result == {}

    def test_multiple_local_based_trvs(self):
        """Multiple LOCAL_BASED TRVs each get their internal temp."""
        real_trvs = {
            "climate.trv_1": {
                "advanced": {"calibration": CalibrationType.LOCAL_BASED},
                "current_temperature": 22.0,
                "last_calibration": 2.0,
            },
            "climate.trv_2": {
                "advanced": {"calibration": CalibrationType.LOCAL_BASED},
                "current_temperature": 19.5,
                "last_calibration": -0.5,
            },
        }
        result = get_trv_internal_temperatures(real_trvs)
        assert result == {"climate.trv_1": 20.0, "climate.trv_2": 20.0}

    def test_mixed_calibration_types(self):
        """Only LOCAL_BASED TRVs are included when mixed with others."""
        real_trvs = {
            "climate.trv_offset": {
                "advanced": {"calibration": CalibrationType.LOCAL_BASED},
                "current_temperature": 21.0,
                "last_calibration": 1.0,
            },
            "climate.trv_target": {
                "advanced": {"calibration": CalibrationType.TARGET_TEMP_BASED},
                "current_temperature": 21.0,
                "last_calibration": 1.0,
            },
        }
        result = get_trv_internal_temperatures(real_trvs)
        assert result == {"climate.trv_offset": 20.0}

    def test_rounds_to_one_decimal(self):
        """Internal temperature is rounded to 1 decimal place."""
        real_trvs = {
            "climate.trv_1": {
                "advanced": {"calibration": CalibrationType.LOCAL_BASED},
                "current_temperature": 20.37,
                "last_calibration": 0.11,
            },
        }
        result = get_trv_internal_temperatures(real_trvs)
        assert result == {"climate.trv_1": 20.3}

    def test_handles_string_values(self):
        """String values for temp/offset are converted to float."""
        real_trvs = {
            "climate.trv_1": {
                "advanced": {"calibration": CalibrationType.LOCAL_BASED},
                "current_temperature": "22.0",
                "last_calibration": "2.0",
            },
        }
        result = get_trv_internal_temperatures(real_trvs)
        assert result == {"climate.trv_1": 20.0}

    def test_skips_invalid_values(self):
        """Invalid values (non-numeric) are skipped without raising."""
        real_trvs = {
            "climate.trv_bad": {
                "advanced": {"calibration": CalibrationType.LOCAL_BASED},
                "current_temperature": "not_a_number",
                "last_calibration": 2.0,
            },
        }
        result = get_trv_internal_temperatures(real_trvs)
        assert result == {}

    def test_empty_real_trvs(self):
        """Empty real_trvs returns empty dict."""
        assert get_trv_internal_temperatures({}) == {}

    def test_none_real_trvs(self):
        """None real_trvs returns empty dict."""
        assert get_trv_internal_temperatures(None) == {}
