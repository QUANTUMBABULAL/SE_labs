# Lab 7 - Fuzz testing with Hypothesis
# Name: CHINMAI A S | SRN: PES2UG24AM198 | Section: C
import math

from hypothesis import given, settings, strategies as st
from laundry_service import parse_order, weight_average, payable_charge

# Strategy that mixes fully random text with "almost valid" inputs built from
# the characters each parser cares about, so edge cases are hit more often.
garment_like = st.text(alphabet="abcRD :.-1234567890eEinfa", max_size=20)
csv_like = st.text(alphabet="0123456789,- .+", max_size=20)
pipe_like = st.text(alphabet="0123456789|.-eEinfa ", max_size=20)


@settings(max_examples=300)
@given(st.text() | st.none() | garment_like)
def test_parse_order_no_crash(s):
    try:
        result = parse_order(s)
    except Exception as e:
        assert False, f"parse_order crashed with: {e!r}"
    if result is not None:
        garment, kg = result
        assert garment and isinstance(kg, float)
        assert math.isfinite(kg) and kg >= 0


@settings(max_examples=300)
@given(st.text() | st.none() | csv_like)
def test_weight_average_no_crash(s):
    try:
        result = weight_average(s)
    except Exception as e:
        assert False, f"weight_average crashed with: {e!r}"
    if result is not None:
        assert isinstance(result, int) and result >= 0


@settings(max_examples=300)
@given(st.text() | st.none() | pipe_like)
def test_payable_charge_no_crash(s):
    try:
        result = payable_charge(s)
    except Exception as e:
        assert False, f"payable_charge crashed with: {e!r}"
    if result is not None:
        assert math.isfinite(result) and result >= 0


# ----- valid inputs must still give correct answers -----
@given(st.sampled_from(["regular", "delicate", "bedding"]),
       st.integers(min_value=0, max_value=1000))
def test_parse_order_valid(garment, kg):
    assert parse_order(f"{garment}:{kg}") == (garment.title(), float(kg))


@given(st.lists(st.integers(min_value=0, max_value=1000), min_size=1, max_size=20))
def test_weight_average_valid(weights):
    csv = ",".join(map(str, weights))
    assert weight_average(csv) == sum(weights) // len(weights)


@given(st.integers(min_value=0, max_value=100000),
       st.integers(min_value=0, max_value=100000))
def test_payable_charge_valid(charge, discount):
    expected = max(charge * 1.18 - discount, 0)
    assert math.isclose(payable_charge(f"{charge}|{discount}"), expected, abs_tol=1e-6)
