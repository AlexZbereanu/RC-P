
####################
# misc bit functions
####################
def test_bit(value, offset):
    """Test a bit at offset position"""
    mask = 1 << offset
    return bool(value & mask)


def set_bit(value, offset):
    """Set a bit at offset position"""
    mask = 1 << offset
    return int(value | mask)


def reset_bit(value, offset):
    """Reset a bit at offset position"""
    mask = ~(1 << offset)
    return int(value & mask)


def toggle_bit(value, offset):
    """Return an integer with the bit at offset position inverted"""
    mask = 1 << offset
    return int(value ^ mask)
