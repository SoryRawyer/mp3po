"""
huffman.py : a module for doing the Huffman decoding parts of MP3

pretty much a big ripoff from:
https://github.com/hajimehoshi/go-mp3/blob/master/internal/maindata/huffman.go
"""

from .util.utils import Bits

HUFFMAN_TABLE = [
    # 1
    0x0201, 0x0000, 0x0201, 0x0010, 0x0201, 0x0001, 0x0011,
    # 2
    0x0201, 0x0000, 0x0401, 0x0201, 0x0010, 0x0001, 0x0201, 0x0011, 0x0401, 0x0201, 0x0020,
    0x0021, 0x0201, 0x0012, 0x0201, 0x0002, 0x0022,
    # 3
    0x0401, 0x0201, 0x0000, 0x0001, 0x0201, 0x0011, 0x0201, 0x0010, 0x0401, 0x0201, 0x0020,
    0x0021, 0x0201, 0x0012, 0x0201, 0x0002, 0x0022,
    # 5
    0x0201, 0x0000, 0x0401, 0x0201, 0x0010, 0x0001, 0x0201, 0x0011, 0x0801, 0x0401, 0x0201,
    0x0020, 0x0002, 0x0201, 0x0021, 0x0012, 0x0801, 0x0401, 0x0201, 0x0022, 0x0030, 0x0201,
    0x0003, 0x0013, 0x0201, 0x0031, 0x0201, 0x0032, 0x0201, 0x0023, 0x0033,
    # 6
    0x0601, 0x0401, 0x0201, 0x0000, 0x0010, 0x0011, 0x0601, 0x0201, 0x0001, 0x0201, 0x0020,
    0x0021, 0x0601, 0x0201, 0x0012, 0x0201, 0x0002, 0x0022, 0x0401, 0x0201, 0x0031, 0x0013,
    0x0401, 0x0201, 0x0030, 0x0032, 0x0201, 0x0023, 0x0201, 0x0003, 0x0033,
    # 7
    0x0201, 0x0000, 0x0401, 0x0201, 0x0010, 0x0001, 0x0801, 0x0201, 0x0011, 0x0401, 0x0201,
    0x0020, 0x0002, 0x0021, 0x1201, 0x0601, 0x0201, 0x0012, 0x0201, 0x0022, 0x0030, 0x0401,
    0x0201, 0x0031, 0x0013, 0x0401, 0x0201, 0x0003, 0x0032, 0x0201, 0x0023, 0x0004, 0x0a01,
    0x0401, 0x0201, 0x0040, 0x0041, 0x0201, 0x0014, 0x0201, 0x0042, 0x0024, 0x0c01, 0x0601,
    0x0401, 0x0201, 0x0033, 0x0043, 0x0050, 0x0401, 0x0201, 0x0034, 0x0005, 0x0051, 0x0601,
    0x0201, 0x0015, 0x0201, 0x0052, 0x0025, 0x0401, 0x0201, 0x0044, 0x0035, 0x0401, 0x0201,
    0x0053, 0x0054, 0x0201, 0x0045, 0x0055,
    # 8
    0x0601, 0x0201, 0x0000, 0x0201, 0x0010, 0x0001, 0x0201, 0x0011, 0x0401, 0x0201, 0x0021,
    0x0012, 0x0e01, 0x0401, 0x0201, 0x0020, 0x0002, 0x0201, 0x0022, 0x0401, 0x0201, 0x0030,
    0x0003, 0x0201, 0x0031, 0x0013, 0x0e01, 0x0801, 0x0401, 0x0201, 0x0032, 0x0023, 0x0201,
    0x0040, 0x0004, 0x0201, 0x0041, 0x0201, 0x0014, 0x0042, 0x0c01, 0x0601, 0x0201, 0x0024,
    0x0201, 0x0033, 0x0050, 0x0401, 0x0201, 0x0043, 0x0034, 0x0051, 0x0601, 0x0201, 0x0015,
    0x0201, 0x0005, 0x0052, 0x0601, 0x0201, 0x0025, 0x0201, 0x0044, 0x0035, 0x0201, 0x0053,
    0x0201, 0x0045, 0x0201, 0x0054, 0x0055,
    # 9
    0x0801, 0x0401, 0x0201, 0x0000, 0x0010, 0x0201, 0x0001, 0x0011, 0x0a01, 0x0401, 0x0201,
    0x0020, 0x0021, 0x0201, 0x0012, 0x0201, 0x0002, 0x0022, 0x0c01, 0x0601, 0x0401, 0x0201,
    0x0030, 0x0003, 0x0031, 0x0201, 0x0013, 0x0201, 0x0032, 0x0023, 0x0c01, 0x0401, 0x0201,
    0x0041, 0x0014, 0x0401, 0x0201, 0x0040, 0x0033, 0x0201, 0x0042, 0x0024, 0x0a01, 0x0601,
    0x0401, 0x0201, 0x0004, 0x0050, 0x0043, 0x0201, 0x0034, 0x0051, 0x0801, 0x0401, 0x0201,
    0x0015, 0x0052, 0x0201, 0x0025, 0x0044, 0x0601, 0x0401, 0x0201, 0x0005, 0x0054, 0x0053,
    0x0201, 0x0035, 0x0201, 0x0045, 0x0055,
    # 10
    0x0201, 0x0000, 0x0401, 0x0201, 0x0010, 0x0001, 0x0a01, 0x0201, 0x0011, 0x0401, 0x0201,
    0x0020, 0x0002, 0x0201, 0x0021, 0x0012, 0x1c01, 0x0801, 0x0401, 0x0201, 0x0022, 0x0030,
    0x0201, 0x0031, 0x0013, 0x0801, 0x0401, 0x0201, 0x0003, 0x0032, 0x0201, 0x0023, 0x0040,
    0x0401, 0x0201, 0x0041, 0x0014, 0x0401, 0x0201, 0x0004, 0x0033, 0x0201, 0x0042, 0x0024,
    0x1c01, 0x0a01, 0x0601, 0x0401, 0x0201, 0x0050, 0x0005, 0x0060, 0x0201, 0x0061, 0x0016,
    0x0c01, 0x0601, 0x0401, 0x0201, 0x0043, 0x0034, 0x0051, 0x0201, 0x0015, 0x0201, 0x0052,
    0x0025, 0x0401, 0x0201, 0x0026, 0x0036, 0x0071, 0x1401, 0x0801, 0x0201, 0x0017, 0x0401,
    0x0201, 0x0044, 0x0053, 0x0006, 0x0601, 0x0401, 0x0201, 0x0035, 0x0045, 0x0062, 0x0201,
    0x0070, 0x0201, 0x0007, 0x0064, 0x0e01, 0x0401, 0x0201, 0x0072, 0x0027, 0x0601, 0x0201,
    0x0063, 0x0201, 0x0054, 0x0055, 0x0201, 0x0046, 0x0073, 0x0801, 0x0401, 0x0201, 0x0037,
    0x0065, 0x0201, 0x0056, 0x0074, 0x0601, 0x0201, 0x0047, 0x0201, 0x0066, 0x0075, 0x0401,
    0x0201, 0x0057, 0x0076, 0x0201, 0x0067, 0x0077,
    # 11
    0x0601, 0x0201, 0x0000, 0x0201, 0x0010, 0x0001, 0x0801, 0x0201, 0x0011, 0x0401, 0x0201,
    0x0020, 0x0002, 0x0012, 0x1801, 0x0801, 0x0201, 0x0021, 0x0201, 0x0022, 0x0201, 0x0030,
    0x0003, 0x0401, 0x0201, 0x0031, 0x0013, 0x0401, 0x0201, 0x0032, 0x0023, 0x0401, 0x0201,
    0x0040, 0x0004, 0x0201, 0x0041, 0x0014, 0x1e01, 0x1001, 0x0a01, 0x0401, 0x0201, 0x0042,
    0x0024, 0x0401, 0x0201, 0x0033, 0x0043, 0x0050, 0x0401, 0x0201, 0x0034, 0x0051, 0x0061,
    0x0601, 0x0201, 0x0016, 0x0201, 0x0006, 0x0026, 0x0201, 0x0062, 0x0201, 0x0015, 0x0201,
    0x0005, 0x0052, 0x1001, 0x0a01, 0x0601, 0x0401, 0x0201, 0x0025, 0x0044, 0x0060, 0x0201,
    0x0063, 0x0036, 0x0401, 0x0201, 0x0070, 0x0017, 0x0071, 0x1001, 0x0601, 0x0401, 0x0201,
    0x0007, 0x0064, 0x0072, 0x0201, 0x0027, 0x0401, 0x0201, 0x0053, 0x0035, 0x0201, 0x0054,
    0x0045, 0x0a01, 0x0401, 0x0201, 0x0046, 0x0073, 0x0201, 0x0037, 0x0201, 0x0065, 0x0056,
    0x0a01, 0x0601, 0x0401, 0x0201, 0x0055, 0x0057, 0x0074, 0x0201, 0x0047, 0x0066, 0x0401,
    0x0201, 0x0075, 0x0076, 0x0201, 0x0067, 0x0077,
    # 12
    0x0c01, 0x0401, 0x0201, 0x0010, 0x0001, 0x0201, 0x0011, 0x0201, 0x0000, 0x0201, 0x0020,
    0x0002, 0x1001, 0x0401, 0x0201, 0x0021, 0x0012, 0x0401, 0x0201, 0x0022, 0x0031, 0x0201,
    0x0013, 0x0201, 0x0030, 0x0201, 0x0003, 0x0040, 0x1a01, 0x0801, 0x0401, 0x0201, 0x0032,
    0x0023, 0x0201, 0x0041, 0x0033, 0x0a01, 0x0401, 0x0201, 0x0014, 0x0042, 0x0201, 0x0024,
    0x0201, 0x0004, 0x0050, 0x0401, 0x0201, 0x0043, 0x0034, 0x0201, 0x0051, 0x0015, 0x1c01,
    0x0e01, 0x0801, 0x0401, 0x0201, 0x0052, 0x0025, 0x0201, 0x0053, 0x0035, 0x0401, 0x0201,
    0x0060, 0x0016, 0x0061, 0x0401, 0x0201, 0x0062, 0x0026, 0x0601, 0x0401, 0x0201, 0x0005,
    0x0006, 0x0044, 0x0201, 0x0054, 0x0045, 0x1201, 0x0a01, 0x0401, 0x0201, 0x0063, 0x0036,
    0x0401, 0x0201, 0x0070, 0x0007, 0x0071, 0x0401, 0x0201, 0x0017, 0x0064, 0x0201, 0x0046,
    0x0072, 0x0a01, 0x0601, 0x0201, 0x0027, 0x0201, 0x0055, 0x0073, 0x0201, 0x0037, 0x0056,
    0x0801, 0x0401, 0x0201, 0x0065, 0x0074, 0x0201, 0x0047, 0x0066, 0x0401, 0x0201, 0x0075,
    0x0057, 0x0201, 0x0076, 0x0201, 0x0067, 0x0077,
    # 13
    0x0201, 0x0000, 0x0601, 0x0201, 0x0010, 0x0201, 0x0001, 0x0011, 0x1c01, 0x0801, 0x0401,
    0x0201, 0x0020, 0x0002, 0x0201, 0x0021, 0x0012, 0x0801, 0x0401, 0x0201, 0x0022, 0x0030,
    0x0201, 0x0003, 0x0031, 0x0601, 0x0201, 0x0013, 0x0201, 0x0032, 0x0023, 0x0401, 0x0201,
    0x0040, 0x0004, 0x0041, 0x4601, 0x1c01, 0x0e01, 0x0601, 0x0201, 0x0014, 0x0201, 0x0033,
    0x0042, 0x0401, 0x0201, 0x0024, 0x0050, 0x0201, 0x0043, 0x0034, 0x0401, 0x0201, 0x0051,
    0x0015, 0x0401, 0x0201, 0x0005, 0x0052, 0x0201, 0x0025, 0x0201, 0x0044, 0x0053, 0x0e01,
    0x0801, 0x0401, 0x0201, 0x0060, 0x0006, 0x0201, 0x0061, 0x0016, 0x0401, 0x0201, 0x0080,
    0x0008, 0x0081, 0x1001, 0x0801, 0x0401, 0x0201, 0x0035, 0x0062, 0x0201, 0x0026, 0x0054,
    0x0401, 0x0201, 0x0045, 0x0063, 0x0201, 0x0036, 0x0070, 0x0601, 0x0401, 0x0201, 0x0007,
    0x0055, 0x0071, 0x0201, 0x0017, 0x0201, 0x0027, 0x0037, 0x4801, 0x1801, 0x0c01, 0x0401,
    0x0201, 0x0018, 0x0082, 0x0201, 0x0028, 0x0401, 0x0201, 0x0064, 0x0046, 0x0072, 0x0801,
    0x0401, 0x0201, 0x0084, 0x0048, 0x0201, 0x0090, 0x0009, 0x0201, 0x0091, 0x0019, 0x1801,
    0x0e01, 0x0801, 0x0401, 0x0201, 0x0073, 0x0065, 0x0201, 0x0056, 0x0074, 0x0401, 0x0201,
    0x0047, 0x0066, 0x0083, 0x0601, 0x0201, 0x0038, 0x0201, 0x0075, 0x0057, 0x0201, 0x0092,
    0x0029, 0x0e01, 0x0801, 0x0401, 0x0201, 0x0067, 0x0085, 0x0201, 0x0058, 0x0039, 0x0201,
    0x0093, 0x0201, 0x0049, 0x0086, 0x0601, 0x0201, 0x00a0, 0x0201, 0x0068, 0x000a, 0x0201,
    0x00a1, 0x001a, 0x4401, 0x1801, 0x0c01, 0x0401, 0x0201, 0x00a2, 0x002a, 0x0401, 0x0201,
    0x0095, 0x0059, 0x0201, 0x00a3, 0x003a, 0x0801, 0x0401, 0x0201, 0x004a, 0x0096, 0x0201,
    0x00b0, 0x000b, 0x0201, 0x00b1, 0x001b, 0x1401, 0x0801, 0x0201, 0x00b2, 0x0401, 0x0201,
    0x0076, 0x0077, 0x0094, 0x0601, 0x0401, 0x0201, 0x0087, 0x0078, 0x00a4, 0x0401, 0x0201,
    0x0069, 0x00a5, 0x002b, 0x0c01, 0x0601, 0x0401, 0x0201, 0x005a, 0x0088, 0x00b3, 0x0201,
    0x003b, 0x0201, 0x0079, 0x00a6, 0x0601, 0x0401, 0x0201, 0x006a, 0x00b4, 0x00c0, 0x0401,
    0x0201, 0x000c, 0x0098, 0x00c1, 0x3c01, 0x1601, 0x0a01, 0x0601, 0x0201, 0x001c, 0x0201,
    0x0089, 0x00b5, 0x0201, 0x005b, 0x00c2, 0x0401, 0x0201, 0x002c, 0x003c, 0x0401, 0x0201,
    0x00b6, 0x006b, 0x0201, 0x00c4, 0x004c, 0x1001, 0x0801, 0x0401, 0x0201, 0x00a8, 0x008a,
    0x0201, 0x00d0, 0x000d, 0x0201, 0x00d1, 0x0201, 0x004b, 0x0201, 0x0097, 0x00a7, 0x0c01,
    0x0601, 0x0201, 0x00c3, 0x0201, 0x007a, 0x0099, 0x0401, 0x0201, 0x00c5, 0x005c, 0x00b7,
    0x0401, 0x0201, 0x001d, 0x00d2, 0x0201, 0x002d, 0x0201, 0x007b, 0x00d3, 0x3401, 0x1c01,
    0x0c01, 0x0401, 0x0201, 0x003d, 0x00c6, 0x0401, 0x0201, 0x006c, 0x00a9, 0x0201, 0x009a,
    0x00d4, 0x0801, 0x0401, 0x0201, 0x00b8, 0x008b, 0x0201, 0x004d, 0x00c7, 0x0401, 0x0201,
    0x007c, 0x00d5, 0x0201, 0x005d, 0x00e0, 0x0a01, 0x0401, 0x0201, 0x00e1, 0x001e, 0x0401,
    0x0201, 0x000e, 0x002e, 0x00e2, 0x0801, 0x0401, 0x0201, 0x00e3, 0x006d, 0x0201, 0x008c,
    0x00e4, 0x0401, 0x0201, 0x00e5, 0x00ba, 0x00f0, 0x2601, 0x1001, 0x0401, 0x0201, 0x00f1,
    0x001f, 0x0601, 0x0401, 0x0201, 0x00aa, 0x009b, 0x00b9, 0x0201, 0x003e, 0x0201, 0x00d6,
    0x00c8, 0x0c01, 0x0601, 0x0201, 0x004e, 0x0201, 0x00d7, 0x007d, 0x0201, 0x00ab, 0x0201,
    0x005e, 0x00c9, 0x0601, 0x0201, 0x000f, 0x0201, 0x009c, 0x006e, 0x0201, 0x00f2, 0x002f,
    0x2001, 0x1001, 0x0601, 0x0401, 0x0201, 0x00d8, 0x008d, 0x003f, 0x0601, 0x0201, 0x00f3,
    0x0201, 0x00e6, 0x00ca, 0x0201, 0x00f4, 0x004f, 0x0801, 0x0401, 0x0201, 0x00bb, 0x00ac,
    0x0201, 0x00e7, 0x00f5, 0x0401, 0x0201, 0x00d9, 0x009d, 0x0201, 0x005f, 0x00e8, 0x1e01,
    0x0c01, 0x0601, 0x0201, 0x006f, 0x0201, 0x00f6, 0x00cb, 0x0401, 0x0201, 0x00bc, 0x00ad,
    0x00da, 0x0801, 0x0201, 0x00f7, 0x0401, 0x0201, 0x007e, 0x007f, 0x008e, 0x0601, 0x0401,
    0x0201, 0x009e, 0x00ae, 0x00cc, 0x0201, 0x00f8, 0x008f, 0x1201, 0x0801, 0x0401, 0x0201,
    0x00db, 0x00bd, 0x0201, 0x00ea, 0x00f9, 0x0401, 0x0201, 0x009f, 0x00eb, 0x0201, 0x00be,
    0x0201, 0x00cd, 0x00fa, 0x0e01, 0x0401, 0x0201, 0x00dd, 0x00ec, 0x0601, 0x0401, 0x0201,
    0x00e9, 0x00af, 0x00dc, 0x0201, 0x00ce, 0x00fb, 0x0801, 0x0401, 0x0201, 0x00bf, 0x00de,
    0x0201, 0x00cf, 0x00ee, 0x0401, 0x0201, 0x00df, 0x00ef, 0x0201, 0x00ff, 0x0201, 0x00ed,
    0x0201, 0x00fd, 0x0201, 0x00fc, 0x00fe,
    # 15
    0x1001, 0x0601, 0x0201, 0x0000, 0x0201, 0x0010, 0x0001, 0x0201, 0x0011, 0x0401, 0x0201,
    0x0020, 0x0002, 0x0201, 0x0021, 0x0012, 0x3201, 0x1001, 0x0601, 0x0201, 0x0022, 0x0201,
    0x0030, 0x0031, 0x0601, 0x0201, 0x0013, 0x0201, 0x0003, 0x0040, 0x0201, 0x0032, 0x0023,
    0x0e01, 0x0601, 0x0401, 0x0201, 0x0004, 0x0014, 0x0041, 0x0401, 0x0201, 0x0033, 0x0042,
    0x0201, 0x0024, 0x0043, 0x0a01, 0x0601, 0x0201, 0x0034, 0x0201, 0x0050, 0x0005, 0x0201,
    0x0051, 0x0015, 0x0401, 0x0201, 0x0052, 0x0025, 0x0401, 0x0201, 0x0044, 0x0053, 0x0061,
    0x5a01, 0x2401, 0x1201, 0x0a01, 0x0601, 0x0201, 0x0035, 0x0201, 0x0060, 0x0006, 0x0201,
    0x0016, 0x0062, 0x0401, 0x0201, 0x0026, 0x0054, 0x0201, 0x0045, 0x0063, 0x0a01, 0x0601,
    0x0201, 0x0036, 0x0201, 0x0070, 0x0007, 0x0201, 0x0071, 0x0055, 0x0401, 0x0201, 0x0017,
    0x0064, 0x0201, 0x0072, 0x0027, 0x1801, 0x1001, 0x0801, 0x0401, 0x0201, 0x0046, 0x0073,
    0x0201, 0x0037, 0x0065, 0x0401, 0x0201, 0x0056, 0x0080, 0x0201, 0x0008, 0x0074, 0x0401,
    0x0201, 0x0081, 0x0018, 0x0201, 0x0082, 0x0028, 0x1001, 0x0801, 0x0401, 0x0201, 0x0047,
    0x0066, 0x0201, 0x0083, 0x0038, 0x0401, 0x0201, 0x0075, 0x0057, 0x0201, 0x0084, 0x0048,
    0x0601, 0x0401, 0x0201, 0x0090, 0x0019, 0x0091, 0x0401, 0x0201, 0x0092, 0x0076, 0x0201,
    0x0067, 0x0029, 0x5c01, 0x2401, 0x1201, 0x0a01, 0x0401, 0x0201, 0x0085, 0x0058, 0x0401,
    0x0201, 0x0009, 0x0077, 0x0093, 0x0401, 0x0201, 0x0039, 0x0094, 0x0201, 0x0049, 0x0086,
    0x0a01, 0x0601, 0x0201, 0x0068, 0x0201, 0x00a0, 0x000a, 0x0201, 0x00a1, 0x001a, 0x0401,
    0x0201, 0x00a2, 0x002a, 0x0201, 0x0095, 0x0059, 0x1a01, 0x0e01, 0x0601, 0x0201, 0x00a3,
    0x0201, 0x003a, 0x0087, 0x0401, 0x0201, 0x0078, 0x00a4, 0x0201, 0x004a, 0x0096, 0x0601,
    0x0401, 0x0201, 0x0069, 0x00b0, 0x00b1, 0x0401, 0x0201, 0x001b, 0x00a5, 0x00b2, 0x0e01,
    0x0801, 0x0401, 0x0201, 0x005a, 0x002b, 0x0201, 0x0088, 0x0097, 0x0201, 0x00b3, 0x0201,
    0x0079, 0x003b, 0x0801, 0x0401, 0x0201, 0x006a, 0x00b4, 0x0201, 0x004b, 0x00c1, 0x0401,
    0x0201, 0x0098, 0x0089, 0x0201, 0x001c, 0x00b5, 0x5001, 0x2201, 0x1001, 0x0601, 0x0401,
    0x0201, 0x005b, 0x002c, 0x00c2, 0x0601, 0x0401, 0x0201, 0x000b, 0x00c0, 0x00a6, 0x0201,
    0x00a7, 0x007a, 0x0a01, 0x0401, 0x0201, 0x00c3, 0x003c, 0x0401, 0x0201, 0x000c, 0x0099,
    0x00b6, 0x0401, 0x0201, 0x006b, 0x00c4, 0x0201, 0x004c, 0x00a8, 0x1401, 0x0a01, 0x0401,
    0x0201, 0x008a, 0x00c5, 0x0401, 0x0201, 0x00d0, 0x005c, 0x00d1, 0x0401, 0x0201, 0x00b7,
    0x007b, 0x0201, 0x001d, 0x0201, 0x000d, 0x002d, 0x0c01, 0x0401, 0x0201, 0x00d2, 0x00d3,
    0x0401, 0x0201, 0x003d, 0x00c6, 0x0201, 0x006c, 0x00a9, 0x0601, 0x0401, 0x0201, 0x009a,
    0x00b8, 0x00d4, 0x0401, 0x0201, 0x008b, 0x004d, 0x0201, 0x00c7, 0x007c, 0x4401, 0x2201,
    0x1201, 0x0a01, 0x0401, 0x0201, 0x00d5, 0x005d, 0x0401, 0x0201, 0x00e0, 0x000e, 0x00e1,
    0x0401, 0x0201, 0x001e, 0x00e2, 0x0201, 0x00aa, 0x002e, 0x0801, 0x0401, 0x0201, 0x00b9,
    0x009b, 0x0201, 0x00e3, 0x00d6, 0x0401, 0x0201, 0x006d, 0x003e, 0x0201, 0x00c8, 0x008c,
    0x1001, 0x0801, 0x0401, 0x0201, 0x00e4, 0x004e, 0x0201, 0x00d7, 0x007d, 0x0401, 0x0201,
    0x00e5, 0x00ba, 0x0201, 0x00ab, 0x005e, 0x0801, 0x0401, 0x0201, 0x00c9, 0x009c, 0x0201,
    0x00f1, 0x001f, 0x0601, 0x0401, 0x0201, 0x00f0, 0x006e, 0x00f2, 0x0201, 0x002f, 0x00e6,
    0x2601, 0x1201, 0x0801, 0x0401, 0x0201, 0x00d8, 0x00f3, 0x0201, 0x003f, 0x00f4, 0x0601,
    0x0201, 0x004f, 0x0201, 0x008d, 0x00d9, 0x0201, 0x00bb, 0x00ca, 0x0801, 0x0401, 0x0201,
    0x00ac, 0x00e7, 0x0201, 0x007e, 0x00f5, 0x0801, 0x0401, 0x0201, 0x009d, 0x005f, 0x0201,
    0x00e8, 0x008e, 0x0201, 0x00f6, 0x00cb, 0x2201, 0x1201, 0x0a01, 0x0601, 0x0401, 0x0201,
    0x000f, 0x00ae, 0x006f, 0x0201, 0x00bc, 0x00da, 0x0401, 0x0201, 0x00ad, 0x00f7, 0x0201,
    0x007f, 0x00e9, 0x0801, 0x0401, 0x0201, 0x009e, 0x00cc, 0x0201, 0x00f8, 0x008f, 0x0401,
    0x0201, 0x00db, 0x00bd, 0x0201, 0x00ea, 0x00f9, 0x1001, 0x0801, 0x0401, 0x0201, 0x009f,
    0x00dc, 0x0201, 0x00cd, 0x00eb, 0x0401, 0x0201, 0x00be, 0x00fa, 0x0201, 0x00af, 0x00dd,
    0x0e01, 0x0601, 0x0401, 0x0201, 0x00ec, 0x00ce, 0x00fb, 0x0401, 0x0201, 0x00bf, 0x00ed,
    0x0201, 0x00de, 0x00fc, 0x0601, 0x0401, 0x0201, 0x00cf, 0x00fd, 0x00ee, 0x0401, 0x0201,
    0x00df, 0x00fe, 0x0201, 0x00ef, 0x00ff,
    # 16
    0x0201, 0x0000, 0x0601, 0x0201, 0x0010, 0x0201, 0x0001, 0x0011, 0x2a01, 0x0801, 0x0401,
    0x0201, 0x0020, 0x0002, 0x0201, 0x0021, 0x0012, 0x0a01, 0x0601, 0x0201, 0x0022, 0x0201,
    0x0030, 0x0003, 0x0201, 0x0031, 0x0013, 0x0a01, 0x0401, 0x0201, 0x0032, 0x0023, 0x0401,
    0x0201, 0x0040, 0x0004, 0x0041, 0x0601, 0x0201, 0x0014, 0x0201, 0x0033, 0x0042, 0x0401,
    0x0201, 0x0024, 0x0050, 0x0201, 0x0043, 0x0034, 0x8a01, 0x2801, 0x1001, 0x0601, 0x0401,
    0x0201, 0x0005, 0x0015, 0x0051, 0x0401, 0x0201, 0x0052, 0x0025, 0x0401, 0x0201, 0x0044,
    0x0035, 0x0053, 0x0a01, 0x0601, 0x0401, 0x0201, 0x0060, 0x0006, 0x0061, 0x0201, 0x0016,
    0x0062, 0x0801, 0x0401, 0x0201, 0x0026, 0x0054, 0x0201, 0x0045, 0x0063, 0x0401, 0x0201,
    0x0036, 0x0070, 0x0071, 0x2801, 0x1201, 0x0801, 0x0201, 0x0017, 0x0201, 0x0007, 0x0201,
    0x0055, 0x0064, 0x0401, 0x0201, 0x0072, 0x0027, 0x0401, 0x0201, 0x0046, 0x0065, 0x0073,
    0x0a01, 0x0601, 0x0201, 0x0037, 0x0201, 0x0056, 0x0008, 0x0201, 0x0080, 0x0081, 0x0601,
    0x0201, 0x0018, 0x0201, 0x0074, 0x0047, 0x0201, 0x0082, 0x0201, 0x0028, 0x0066, 0x1801,
    0x0e01, 0x0801, 0x0401, 0x0201, 0x0083, 0x0038, 0x0201, 0x0075, 0x0084, 0x0401, 0x0201,
    0x0048, 0x0090, 0x0091, 0x0601, 0x0201, 0x0019, 0x0201, 0x0009, 0x0076, 0x0201, 0x0092,
    0x0029, 0x0e01, 0x0801, 0x0401, 0x0201, 0x0085, 0x0058, 0x0201, 0x0093, 0x0039, 0x0401,
    0x0201, 0x00a0, 0x000a, 0x001a, 0x0801, 0x0201, 0x00a2, 0x0201, 0x0067, 0x0201, 0x0057,
    0x0049, 0x0601, 0x0201, 0x0094, 0x0201, 0x0077, 0x0086, 0x0201, 0x00a1, 0x0201, 0x0068,
    0x0095, 0xdc01, 0x7e01, 0x3201, 0x1a01, 0x0c01, 0x0601, 0x0201, 0x002a, 0x0201, 0x0059,
    0x003a, 0x0201, 0x00a3, 0x0201, 0x0087, 0x0078, 0x0801, 0x0401, 0x0201, 0x00a4, 0x004a,
    0x0201, 0x0096, 0x0069, 0x0401, 0x0201, 0x00b0, 0x000b, 0x00b1, 0x0a01, 0x0401, 0x0201,
    0x001b, 0x00b2, 0x0201, 0x002b, 0x0201, 0x00a5, 0x005a, 0x0601, 0x0201, 0x00b3, 0x0201,
    0x00a6, 0x006a, 0x0401, 0x0201, 0x00b4, 0x004b, 0x0201, 0x000c, 0x00c1, 0x1e01, 0x0e01,
    0x0601, 0x0401, 0x0201, 0x00b5, 0x00c2, 0x002c, 0x0401, 0x0201, 0x00a7, 0x00c3, 0x0201,
    0x006b, 0x00c4, 0x0801, 0x0201, 0x001d, 0x0401, 0x0201, 0x0088, 0x0097, 0x003b, 0x0401,
    0x0201, 0x00d1, 0x00d2, 0x0201, 0x002d, 0x00d3, 0x1201, 0x0601, 0x0401, 0x0201, 0x001e,
    0x002e, 0x00e2, 0x0601, 0x0401, 0x0201, 0x0079, 0x0098, 0x00c0, 0x0201, 0x001c, 0x0201,
    0x0089, 0x005b, 0x0e01, 0x0601, 0x0201, 0x003c, 0x0201, 0x007a, 0x00b6, 0x0401, 0x0201,
    0x004c, 0x0099, 0x0201, 0x00a8, 0x008a, 0x0601, 0x0201, 0x000d, 0x0201, 0x00c5, 0x005c,
    0x0401, 0x0201, 0x003d, 0x00c6, 0x0201, 0x006c, 0x009a, 0x5801, 0x5601, 0x2401, 0x1001,
    0x0801, 0x0401, 0x0201, 0x008b, 0x004d, 0x0201, 0x00c7, 0x007c, 0x0401, 0x0201, 0x00d5,
    0x005d, 0x0201, 0x00e0, 0x000e, 0x0801, 0x0201, 0x00e3, 0x0401, 0x0201, 0x00d0, 0x00b7,
    0x007b, 0x0601, 0x0401, 0x0201, 0x00a9, 0x00b8, 0x00d4, 0x0201, 0x00e1, 0x0201, 0x00aa,
    0x00b9, 0x1801, 0x0a01, 0x0601, 0x0401, 0x0201, 0x009b, 0x00d6, 0x006d, 0x0201, 0x003e,
    0x00c8, 0x0601, 0x0401, 0x0201, 0x008c, 0x00e4, 0x004e, 0x0401, 0x0201, 0x00d7, 0x00e5,
    0x0201, 0x00ba, 0x00ab, 0x0c01, 0x0401, 0x0201, 0x009c, 0x00e6, 0x0401, 0x0201, 0x006e,
    0x00d8, 0x0201, 0x008d, 0x00bb, 0x0801, 0x0401, 0x0201, 0x00e7, 0x009d, 0x0201, 0x00e8,
    0x008e, 0x0401, 0x0201, 0x00cb, 0x00bc, 0x009e, 0x00f1, 0x0201, 0x001f, 0x0201, 0x000f,
    0x002f, 0x4201, 0x3801, 0x0201, 0x00f2, 0x3401, 0x3201, 0x1401, 0x0801, 0x0201, 0x00bd,
    0x0201, 0x005e, 0x0201, 0x007d, 0x00c9, 0x0601, 0x0201, 0x00ca, 0x0201, 0x00ac, 0x007e,
    0x0401, 0x0201, 0x00da, 0x00ad, 0x00cc, 0x0a01, 0x0601, 0x0201, 0x00ae, 0x0201, 0x00db,
    0x00dc, 0x0201, 0x00cd, 0x00be, 0x0601, 0x0401, 0x0201, 0x00eb, 0x00ed, 0x00ee, 0x0601,
    0x0401, 0x0201, 0x00d9, 0x00ea, 0x00e9, 0x0201, 0x00de, 0x0401, 0x0201, 0x00dd, 0x00ec,
    0x00ce, 0x003f, 0x00f0, 0x0401, 0x0201, 0x00f3, 0x00f4, 0x0201, 0x004f, 0x0201, 0x00f5,
    0x005f, 0x0a01, 0x0201, 0x00ff, 0x0401, 0x0201, 0x00f6, 0x006f, 0x0201, 0x00f7, 0x007f,
    0x0c01, 0x0601, 0x0201, 0x008f, 0x0201, 0x00f8, 0x00f9, 0x0401, 0x0201, 0x009f, 0x00fa,
    0x00af, 0x0801, 0x0401, 0x0201, 0x00fb, 0x00bf, 0x0201, 0x00fc, 0x00cf, 0x0401, 0x0201,
    0x00fd, 0x00df, 0x0201, 0x00fe, 0x00ef,
    # 24
    0x3c01, 0x0801, 0x0401, 0x0201, 0x0000, 0x0010, 0x0201, 0x0001, 0x0011, 0x0e01, 0x0601,
    0x0401, 0x0201, 0x0020, 0x0002, 0x0021, 0x0201, 0x0012, 0x0201, 0x0022, 0x0201, 0x0030,
    0x0003, 0x0e01, 0x0401, 0x0201, 0x0031, 0x0013, 0x0401, 0x0201, 0x0032, 0x0023, 0x0401,
    0x0201, 0x0040, 0x0004, 0x0041, 0x0801, 0x0401, 0x0201, 0x0014, 0x0033, 0x0201, 0x0042,
    0x0024, 0x0601, 0x0401, 0x0201, 0x0043, 0x0034, 0x0051, 0x0601, 0x0401, 0x0201, 0x0050,
    0x0005, 0x0015, 0x0201, 0x0052, 0x0025, 0xfa01, 0x6201, 0x2201, 0x1201, 0x0a01, 0x0401,
    0x0201, 0x0044, 0x0053, 0x0201, 0x0035, 0x0201, 0x0060, 0x0006, 0x0401, 0x0201, 0x0061,
    0x0016, 0x0201, 0x0062, 0x0026, 0x0801, 0x0401, 0x0201, 0x0054, 0x0045, 0x0201, 0x0063,
    0x0036, 0x0401, 0x0201, 0x0071, 0x0055, 0x0201, 0x0064, 0x0046, 0x2001, 0x0e01, 0x0601,
    0x0201, 0x0072, 0x0201, 0x0027, 0x0037, 0x0201, 0x0073, 0x0401, 0x0201, 0x0070, 0x0007,
    0x0017, 0x0a01, 0x0401, 0x0201, 0x0065, 0x0056, 0x0401, 0x0201, 0x0080, 0x0008, 0x0081,
    0x0401, 0x0201, 0x0074, 0x0047, 0x0201, 0x0018, 0x0082, 0x1001, 0x0801, 0x0401, 0x0201,
    0x0028, 0x0066, 0x0201, 0x0083, 0x0038, 0x0401, 0x0201, 0x0075, 0x0057, 0x0201, 0x0084,
    0x0048, 0x0801, 0x0401, 0x0201, 0x0091, 0x0019, 0x0201, 0x0092, 0x0076, 0x0401, 0x0201,
    0x0067, 0x0029, 0x0201, 0x0085, 0x0058, 0x5c01, 0x2201, 0x1001, 0x0801, 0x0401, 0x0201,
    0x0093, 0x0039, 0x0201, 0x0094, 0x0049, 0x0401, 0x0201, 0x0077, 0x0086, 0x0201, 0x0068,
    0x00a1, 0x0801, 0x0401, 0x0201, 0x00a2, 0x002a, 0x0201, 0x0095, 0x0059, 0x0401, 0x0201,
    0x00a3, 0x003a, 0x0201, 0x0087, 0x0201, 0x0078, 0x004a, 0x1601, 0x0c01, 0x0401, 0x0201,
    0x00a4, 0x0096, 0x0401, 0x0201, 0x0069, 0x00b1, 0x0201, 0x001b, 0x00a5, 0x0601, 0x0201,
    0x00b2, 0x0201, 0x005a, 0x002b, 0x0201, 0x0088, 0x00b3, 0x1001, 0x0a01, 0x0601, 0x0201,
    0x0090, 0x0201, 0x0009, 0x00a0, 0x0201, 0x0097, 0x0079, 0x0401, 0x0201, 0x00a6, 0x006a,
    0x00b4, 0x0c01, 0x0601, 0x0201, 0x001a, 0x0201, 0x000a, 0x00b0, 0x0201, 0x003b, 0x0201,
    0x000b, 0x00c0, 0x0401, 0x0201, 0x004b, 0x00c1, 0x0201, 0x0098, 0x0089, 0x4301, 0x2201,
    0x1001, 0x0801, 0x0401, 0x0201, 0x001c, 0x00b5, 0x0201, 0x005b, 0x00c2, 0x0401, 0x0201,
    0x002c, 0x00a7, 0x0201, 0x007a, 0x00c3, 0x0a01, 0x0601, 0x0201, 0x003c, 0x0201, 0x000c,
    0x00d0, 0x0201, 0x00b6, 0x006b, 0x0401, 0x0201, 0x00c4, 0x004c, 0x0201, 0x0099, 0x00a8,
    0x1001, 0x0801, 0x0401, 0x0201, 0x008a, 0x00c5, 0x0201, 0x005c, 0x00d1, 0x0401, 0x0201,
    0x00b7, 0x007b, 0x0201, 0x001d, 0x00d2, 0x0901, 0x0401, 0x0201, 0x002d, 0x00d3, 0x0201,
    0x003d, 0x00c6, 0x55fa, 0x0401, 0x0201, 0x006c, 0x00a9, 0x0201, 0x009a, 0x00d4, 0x2001,
    0x1001, 0x0801, 0x0401, 0x0201, 0x00b8, 0x008b, 0x0201, 0x004d, 0x00c7, 0x0401, 0x0201,
    0x007c, 0x00d5, 0x0201, 0x005d, 0x00e1, 0x0801, 0x0401, 0x0201, 0x001e, 0x00e2, 0x0201,
    0x00aa, 0x00b9, 0x0401, 0x0201, 0x009b, 0x00e3, 0x0201, 0x00d6, 0x006d, 0x1401, 0x0a01,
    0x0601, 0x0201, 0x003e, 0x0201, 0x002e, 0x004e, 0x0201, 0x00c8, 0x008c, 0x0401, 0x0201,
    0x00e4, 0x00d7, 0x0401, 0x0201, 0x007d, 0x00ab, 0x00e5, 0x0a01, 0x0401, 0x0201, 0x00ba,
    0x005e, 0x0201, 0x00c9, 0x0201, 0x009c, 0x006e, 0x0801, 0x0201, 0x00e6, 0x0201, 0x000d,
    0x0201, 0x00e0, 0x000e, 0x0401, 0x0201, 0x00d8, 0x008d, 0x0201, 0x00bb, 0x00ca, 0x4a01,
    0x0201, 0x00ff, 0x4001, 0x3a01, 0x2001, 0x1001, 0x0801, 0x0401, 0x0201, 0x00ac, 0x00e7,
    0x0201, 0x007e, 0x00d9, 0x0401, 0x0201, 0x009d, 0x00e8, 0x0201, 0x008e, 0x00cb, 0x0801,
    0x0401, 0x0201, 0x00bc, 0x00da, 0x0201, 0x00ad, 0x00e9, 0x0401, 0x0201, 0x009e, 0x00cc,
    0x0201, 0x00db, 0x00bd, 0x1001, 0x0801, 0x0401, 0x0201, 0x00ea, 0x00ae, 0x0201, 0x00dc,
    0x00cd, 0x0401, 0x0201, 0x00eb, 0x00be, 0x0201, 0x00dd, 0x00ec, 0x0801, 0x0401, 0x0201,
    0x00ce, 0x00ed, 0x0201, 0x00de, 0x00ee, 0x000f, 0x0401, 0x0201, 0x00f0, 0x001f, 0x00f1,
    0x0401, 0x0201, 0x00f2, 0x002f, 0x0201, 0x00f3, 0x003f, 0x1201, 0x0801, 0x0401, 0x0201,
    0x00f4, 0x004f, 0x0201, 0x00f5, 0x005f, 0x0401, 0x0201, 0x00f6, 0x006f, 0x0201, 0x00f7,
    0x0201, 0x007f, 0x008f, 0x0a01, 0x0401, 0x0201, 0x00f8, 0x00f9, 0x0401, 0x0201, 0x009f,
    0x00af, 0x00fa, 0x0801, 0x0401, 0x0201, 0x00fb, 0x00bf, 0x0201, 0x00fc, 0x00cf, 0x0401,
    0x0201, 0x00fd, 0x00df, 0x0201, 0x00fe, 0x00ef,
    # 32
    0x0201, 0x0000, 0x0801, 0x0401, 0x0201, 0x0008, 0x0004, 0x0201, 0x0001, 0x0002, 0x0801,
    0x0401, 0x0201, 0x000c, 0x000a, 0x0201, 0x0003, 0x0006, 0x0601, 0x0201, 0x0009, 0x0201,
    0x0005, 0x0007, 0x0401, 0x0201, 0x000e, 0x000d, 0x0201, 0x000f, 0x000b,
    # 33
    0x1001, 0x0801, 0x0401, 0x0201, 0x0000, 0x0001, 0x0201, 0x0002, 0x0003, 0x0401, 0x0201,
    0x0004, 0x0005, 0x0201, 0x0006, 0x0007, 0x0801, 0x0401, 0x0201, 0x0008, 0x0009, 0x0201,
    0x000a, 0x000b, 0x0401, 0x0201, 0x000c, 0x000d, 0x0201, 0x000e, 0x000f,
]

# HUFFMAN_TABLE_INFO contains a list of 3-tuples with format:
# huffman table, tree length, and linbits
HUFFMAN_TABLE_INFO = [
    (None, 0, 0),                    # Table  0
    (HUFFMAN_TABLE, 7, 0),           # Table  1
    (HUFFMAN_TABLE[7:24], 17, 0),      # Table  2
    (HUFFMAN_TABLE[24:41], 17, 0),     # Table  3
    (HUFFMAN_TABLE, 0, 0),           # Table  4
    (HUFFMAN_TABLE[41:72], 31, 0),     # Table  5
    (HUFFMAN_TABLE[72:103], 31, 0),     # Table  6
    (HUFFMAN_TABLE[103:174], 71, 0),    # Table  7
    (HUFFMAN_TABLE[174:245], 71, 0),    # Table  8
    (HUFFMAN_TABLE[245:316], 71, 0),    # Table  9
    (HUFFMAN_TABLE[316:443], 127, 0),   # Table 10
    (HUFFMAN_TABLE[443:570], 127, 0),   # Table 11
    (HUFFMAN_TABLE[570:697], 127, 0),   # Table 12
    (HUFFMAN_TABLE[697:1208], 511, 0),   # Table 13
    (HUFFMAN_TABLE, 0, 0),           # Table 14
    (HUFFMAN_TABLE[1208:1719], 511, 0),  # Table 15
    (HUFFMAN_TABLE[1719:2230], 511, 1),  # Table 16
    (HUFFMAN_TABLE[1719:2230], 511, 2),  # Table 17
    (HUFFMAN_TABLE[1719:2230], 511, 3),  # Table 18
    (HUFFMAN_TABLE[1719:2230], 511, 4),  # Table 19
    (HUFFMAN_TABLE[1719:2230], 511, 6),  # Table 20
    (HUFFMAN_TABLE[1719:2230], 511, 8),  # Table 21
    (HUFFMAN_TABLE[1719:2230], 511, 10), # Table 22
    (HUFFMAN_TABLE[1719:2230], 511, 13), # Table 23
    (HUFFMAN_TABLE[2230:2742], 512, 4),  # Table 24
    (HUFFMAN_TABLE[2230:2742], 512, 5),  # Table 25
    (HUFFMAN_TABLE[2230:2742], 512, 6),  # Table 26
    (HUFFMAN_TABLE[2230:2742], 512, 7),  # Table 27
    (HUFFMAN_TABLE[2230:2742], 512, 8),  # Table 28
    (HUFFMAN_TABLE[2230:2742], 512, 9),  # Table 29
    (HUFFMAN_TABLE[2230:2742], 512, 11), # Table 30
    (HUFFMAN_TABLE[2230:2742], 512, 13), # Table 31
    (HUFFMAN_TABLE[2742:2773], 31, 0),   # Table 32
    (HUFFMAN_TABLE[2773:], 31, 0),   # Table 33
]

def decode_big_values(bits: Bits, table_num: int) -> (int, int):
    """
    decode_big_values : decode the bytes in the big values regions
    """
    table, tree_length, linbits = HUFFMAN_TABLE_INFO[table_num]
    if tree_length == 0:
        return 0, 0
    x, y = traverse_table(table, bits)
    if linbits != 0 and x == 15:
        # I *think* we need to convert x back to binary, append more bits
        # and then convert binary back to decimal
        x = int(bin(x).split('b')[1] + bits.read(linbits), 2)
    if x != 0 and bits.read(1) == '1':
        x = -x
    if linbits != 0 and y == 15:
        y = int(bin(y).split('b')[1] + bits.read(linbits), 2)
    if y != 0 and bits.read(1) == '1':
        y = -y
    return x, y

def decode_quadruples(bits: Bits, table_num: int) -> (int, int, int, int):
    """
    decode_quadruples : decode the bytes in the big values regions
    """
    table, tree_length, linbits = HUFFMAN_TABLE_INFO[table_num]
    if tree_length == 0:
        return 0, 0
    x, y = traverse_table(table, bits)
    v = (y >> 3) & 1
    w = (y >> 2) & 1
    x = (y >> 1) & 1
    y = y & 1
    if v != 0 and bits.read(1) == '1':
        v = -v
    if w != 0 and bits.read(1) == '1':
        w = -w
    if x != 0 and bits.read(1) == '1':
        x = -x
    if y != 0 and bits.read(1) == '1':
        y = -y
    return v, w, x, y

def traverse_table(table, bits):
    """
    traverse_table : traverse the huffman table and get back your x and your y
    """
    point = 0
    for _ in range(0, 32):
        if (table[point] & 0xff00) == 0:
            x = int((table[point] >> 4) & 0xf)
            y = int(table[point] & 0xf)
            return x, y
        if bits.read(1) == '1':
            while table[point] >= 250:
                point += int(table[point] & 0xff)
            point += int(table[point] & 0xff)
        else:
            while (table[point] >> 8) >= 250:
                point += int(table[point]) >> 8
            point += int(table[point]) >> 8
    return 0, 0
