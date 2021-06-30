from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# general base for any puzzle
# each character can be a knight or a knave, but not both
general_base = And(
    Or(AKnight, AKnave), Not(And(AKnight, AKnave)),
    Or(BKnight, BKnave), Not(And(BKnight, BKnave)),
    Or(CKnight, CKnave), Not(And(CKnight, CKnave)),
)

# Puzzle 0
# A says "I am both a knight and a knave."
A0_sentence = And(AKnight, AKnave)

knowledge0 = And(
    general_base,
    Implication(AKnight, A0_sentence),
    Implication(AKnave, Not(A0_sentence))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
A1_sentence = And(AKnave, BKnave)

knowledge1 = And(
    general_base,
    Implication(AKnight, A1_sentence),
    Implication(AKnave, Not(A1_sentence))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
A2_sentence = Or(Biconditional(AKnight, BKnight),
                 Biconditional(AKnave, BKnave))

B2_sentence = Not(A2_sentence)

knowledge2 = And(
    general_base,
    Implication(AKnight, A2_sentence),
    Implication(AKnave, Not(A2_sentence)),
    Implication(BKnight, B2_sentence),
    Implication(BKnave, Not(B2_sentence))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
A_said_knight = Symbol("A said 'I am a knight'")

A3_sentence = And(Implication(A_said_knight, AKnight),
                  Implication(Not(A_said_knight), AKnave))

# Negating that A said "I am a knight" is equivalent to saying A said "I am a Knave"
B3_first_sentence = Not(A_said_knight)
B3_second_sentence = CKnave

C3_sentence = AKnight

knowledge3 = And(
    general_base,
    Implication(AKnight, A3_sentence),
    Implication(AKnave, Not(A3_sentence)),
    Implication(BKnight, And(B3_first_sentence, B3_second_sentence)),
    Implication(BKnave, And(Not(B3_first_sentence), Not(B3_second_sentence))),
    Implication(CKnight, C3_sentence),
    Implication(CKnave, Not(C3_sentence))
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
