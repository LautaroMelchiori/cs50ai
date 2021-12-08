from os import curdir
import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP
S -> NP VP NP VP
S -> NP VP Conj VP
S -> NP VP NP NP
NP -> N | Det N | Det N P N | P Det Adj N | P Det Adj N Conj N  | Det Adj N | P N | P Det N P Det N
NP -> N Adv | Det N Conj N | P Det N | NP Adv | Det Adj N P N | N P Det Adj N | Det Adj Adj Adj N | P Det Adj Adj N
VP -> V | V NP | V Adv | V NP V
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    def validate_word(word):
        """
        Receives a word, validates that it contains
        at least 1 alphabetic character, turns it to
        lowercase and returns it
        """
        for letter in word:
            if letter.isalpha():
                return word.lower()
        return False

    return [validate_word(word) for word in nltk.word_tokenize(sentence) if validate_word(word)]


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    chunks = []
    # traverse subtrees of sentence
    for t in tree.subtrees():
        # once we find an np subtree, we check if it has others NPs as subtrees
        if t.label() == 'NP':
            np_flag = True
            for subt in t.subtrees():
                # subtrees method gives us the tree itself as a subtree, so we skip in that case
                if subt == t:
                    continue

                # check if any subtree is an np
                if subt.label() == 'NP':
                    np_flag = False

            # if no subtree is np, we append the NP-chunk
            if np_flag:
                chunks.append(t)

    return chunks


if __name__ == "__main__":
    main()
