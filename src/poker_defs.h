#pragma once

enum {
    PO_HIGH_CARD = 0,
    PO_PAIR = 1,
    PO_TWO_PAIRS = 2,
    PO_THREE_OFAK = 3,
    PO_STRAIGHT = 4,
    PO_FLUSH = 5,
    PO_FULL_HOUSE = 6,
    PO_FOUR_OFAK = 7,
    PO_STRAIGHT_FLUSH = 8
};

constexpr int HandMulti = 13 * 13 * 13 * 13 * 13;
