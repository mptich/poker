#include <pybind11/pybind11.h>
#include <pybind11/stl.h>  // Enables automatic STL conversions (vector, pair, etc.)
#include <vector>
#include <map>
#include <string>

#include "poker_defs.h"


namespace py = pybind11;

typedef std::pair<int, bool> Card;
typedef std::map<int,std::vector<int>> KindCount;

static bool CheckForStraight(const std::vector<Card> &v, int *pStraightRank) {

    int straightRank = 0;
    int prev = -1;
    int straightCount;
    for (const Card &c : v) {
        if (c.first !=  (prev-1)) {
            if (c.first != prev) {
                straightRank = c.first;
                straightCount = 1;
            }
        } else {
            straightCount += 1;
        }

        if (straightCount == 5) break;
    }

    // Check the reverse Ace case
    if ((straightCount == 4) && (v.back().first == 0) && (v[0].first == 12))
        straightCount = 5;

    if (straightCount == 5) {
        *pStraightRank = straightRank;
        return true;
    }

    return false;
}

static bool CheckForFullHouse(const std::vector<Card> &v, const KindCount &kindCounts, int *pFfullHouseRank) {
    if (kindCounts.at(3).size() == 0) return false;
    if (kindCounts.at(3).size() + kindCounts.at(2).size() < 2) return false;

    std::vector<int> threeVector = kindCounts.at(3);

    std::sort(threeVector.begin(), threeVector.end(), [](int a, int b) {
        return a > b; // comparison for descending order
    });

    int threeRank = threeVector[0];

    int twoRank = -1;
    if (threeVector.size() == 2) {
        twoRank = *threeVector.end();
    }

    for (int k : kindCounts.at(2)) {
        if (k > twoRank) twoRank = k;
    }

    *pFfullHouseRank = threeRank * 13 + twoRank;
    return true;
}


// Returns absolute imaximum rank of 7 cards
// Integer is card value, boolean is true if the suite is significant (that could potentially create flush)
// and false if it is not significant
int Process7Cards(const std::vector<Card>& input) {
    // Non cosntant vector
    std::vector<Card> v = input;

    // Sort it in acsending order of values
    std::sort(v.begin(), v.end(), [](const Card &a, const Card &b) {
        return a.first > b.first; // comparison for descending order
    });
    // Add dummy value
    v.emplace_back(Card(1000, false));

    KindCount kindCounts = {{2,{}}, {3,{}}, {4,{}}};

    int flushCount = 0;
    int kindCount = 0;
    int flushRank = 0;
    int prev = -1;
    for (const Card &c: v) {
        if (c.first == prev) kindCount += 1;
        else {
            if (kindCount) {
                kindCounts[kindCount+1].emplace_back(prev);
                kindCount = 0;
            }
            prev = c.first;
        }

        if (c.second) {
            flushRank = flushRank * 13 + c.first; 
            flushCount += 1;
        }
    }

    bool flush = (flushCount >= 5);

    // Remove the dummy element
    v.pop_back();

    // Check for straight and straight flush
    int straightRank;

    // First for straightflush
    if (flush) {
        std::vector<Card> signifV;
        for (const Card &c : v) {
            if (c.second) signifV.emplace_back(c);
        }
        if (CheckForStraight(signifV, &straightRank))
            return PO_STRAIGHT_FLUSH * HandMulti + straightRank;
    }

    auto fourVector = kindCounts[4];
    if (!fourVector.empty()) {
        // It can have only 1 element
        int fourRank = fourVector[0];
        for (const Card &c : v) {
            if (c.first != fourRank) {
                fourRank = fourRank * 13 + c.first;
                return PO_FOUR_OFAK * HandMulti + fourRank;
            }
        }
    }

    int fullHouseRank;
    if (CheckForFullHouse(v, kindCounts, &fullHouseRank))
        return PO_FULL_HOUSE * HandMulti + fullHouseRank;

    if (flush)
        return PO_FLUSH * HandMulti + flushRank;

    if (CheckForStraight(v, &straightRank))
        return PO_STRAIGHT * HandMulti + straightRank;

    auto threeVector = kindCounts[3];
    if (!threeVector.empty()) {
        // There can be only 1 member, otherwise it would have been a full house earlier
        int threeRank = threeVector[0];
        int nonThreeCount = 0;
        int r = 0;
        for (const Card &c : v) {
            if (c.first != threeRank) {
                r = r *13 + c.first;
                nonThreeCount++;
                if (nonThreeCount == 2) break;
            }
        }
        threeRank = threeRank * 13 * 13 + r; 
        return PO_THREE_OFAK * HandMulti + threeRank;
    }

    // check for 2 or 1 pairs
    int absRank = CheckForPairs(v, kindCounts.at(2));
    if (absRank) return absRank;

    // High card
    int highCardCount = 0;
    int highCardRank = 0;
    for (const Card &c : v) {
        highCardRank = highCardRank * 13 + c.first;
        highCardCount++;
        if (highCardCount == 5) return highCardRank;
    }

    // Should not be here
    return 0
}


PYBIND11_MODULE(PokerFastutils, m) {
    m.doc() = "C++ module example with pair and vector handling";
    m.def("Process7Cards", &Process7Cards, "Process a list of (int, bool) pairs and return a string summary plus filtered list");
}
