#pragma once

namespace Flop {

// Descriptors for the flop stage

typedef struct {
    int handCount; // 0 - not present, 1 - one own card, 2 - two own cards
    int outs; // 0 (full), 1, or 2
} StraightDesc;

typedef enum {
    KindNone = 0,
    KindPair = 1,
    Kind2Pairs = 2,
    KindThree = 3,
    KindFullHouse = 4,
    KindFour = 5
} KindType;

typedef struct {
    KindType type;
    int handCount; // 0, 1, or 2
    bool bothKinds; // if KindType is 2 or 4, and handCount = true, then bothKinds=true means presence
                    // of hand cards in both kinds
} KindDesc;

typedef struct {
    int count; // 0 - not present, otherwise >= 3
    bool handCount; // false - 1, true - 2
} FlashDesc;

} // Flop namespace
