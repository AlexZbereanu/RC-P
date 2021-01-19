import struct


###############
# bits function
###############
def get_bits_from_int(val_int, val_size=16):
    """Get the list of bits of val_int integer (default size is 16 bits)"""
    # allocate a bit_nb size list
    bits = [None] * val_size
    # fill bits list with bit items
    for i, item in enumerate(bits):
        bits[i] = bool((val_int >> i) & 0x01)
    # return bits list
    return bits


#########################
# floating-point function
#########################
def decode_ieee(val_int):
    """Decode Python int (32 bits integer) as an IEEE single precision format"""
    return struct.unpack("f", struct.pack("I", val_int))[0]


def encode_ieee(val_float):
    """Encode Python float to int (32 bits integer) as an IEEE single precision"""
    return struct.unpack("I", struct.pack("f", val_float))[0]


################################
# long format (32 bits) function
################################
def word_list_to_long(val_list, big_endian=True):
    """Word list (16 bits int) to long list (32 bits int)"""
    # allocate list for long int
    long_list = [None] * int(len(val_list) / 2)
    # fill registers list with register items
    for i, item in enumerate(long_list):
        if big_endian:
            long_list[i] = (val_list[i * 2] << 16) + val_list[(i * 2) + 1]
        else:
            long_list[i] = (val_list[(i * 2) + 1] << 16) + val_list[i * 2]
    # return long list
    return long_list


def long_list_to_word(val_list, big_endian=True):
    """Long list (32 bits int) to word list (16 bits int)"""
    # allocate list for long int
    word_list = list()
    # fill registers list with register items
    for i, item in enumerate(val_list):
        if big_endian:
            word_list.append(val_list[i] >> 16)
            word_list.append(val_list[i] & 0xffff)
        else:
            word_list.append(val_list[i] & 0xffff)
            word_list.append(val_list[i] >> 16)
    # return long list
    return word_list


#########################################################
# 2's complement of int value (scalar and list) functions
#########################################################
def get_2comp(val_int, val_size=16):
    """Get the 2's complement of Python int val_int"""
    # test MSBit (1 for negative)
    if val_int & (1 << (val_size - 1)):
        # do complement
        val_int -= 1 << val_size
    return val_int


def get_list_2comp(val_list, val_size=16):
    """Get the 2's complement of Python list val_list"""
    return [get_2comp(val, val_size) for val in val_list]


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
