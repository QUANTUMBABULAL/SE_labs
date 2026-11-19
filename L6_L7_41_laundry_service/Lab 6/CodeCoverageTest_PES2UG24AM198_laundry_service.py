# Lab 6 - Code (line) coverage tests
# Name: CHINMAI A S | SRN: PES2UG24AM198 | Section: C
import pytest
from laundry_service import extra_weight_charge, order_acceptable, dropoff_status


# ---------- extra_weight_charge ----------
def test_within_included_weight():
    assert extra_weight_charge("regular", 4, "standard", False) == 0


def test_unknown_garment_raises():
    with pytest.raises(ValueError, match="unknown garment type"):
        extra_weight_charge("silk", 4, "standard", False)


def test_negative_weight_raises():
    with pytest.raises(ValueError, match="invalid weight"):
        extra_weight_charge("regular", -1, "standard", False)


def test_member_gets_extra_allowance():
    # regular 5 + 2 (member) = 7 included -> 9 kg gives 2 extra * 30
    assert extra_weight_charge("regular", 9, "standard", True) == 60


def test_express_small_extra():
    # delicate 3 included -> 5 kg gives 2 extra * 50
    assert extra_weight_charge("delicate", 5, "express", False) == 100


def test_express_heavy_extra_surcharge():
    # regular 5 included -> 20 kg gives 15 extra, rate 50 + 15 + 10 = 75
    assert extra_weight_charge("regular", 20, "express", False) == 15 * 75


# ---------- order_acceptable ----------
def test_order_acceptable():
    assert order_acceptable(10, 20, False) is True


def test_delicate_order():
    assert order_acceptable(10, 5, True) is True


def test_overweight_order_rejected():
    assert order_acceptable(30, 10, False) is False


# ---------- dropoff_status ----------
def test_bedding_express_accepted():
    # cutoff 90 + 30 = 120
    assert dropoff_status(130, True, True) == "accepted"


def test_regular_late():
    # cutoff 60, late window 40..59
    assert dropoff_status(50, False, False) == "late"


def test_regular_rejected():
    assert dropoff_status(10, False, False) == "rejected"
