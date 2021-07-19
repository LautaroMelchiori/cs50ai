import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    def calculate(person):
        """
        Calculate the chance a person has the amount of genes required, and has the trait (or doesnt have it)
        Depending on which set (given as parameters to the joint_probability function) are they included in

        This function works for people from whose parents we dont have information about
        """
        prob = 0

        # set the chance someone has a particular amount of mutated genes
        if person['name'] in one_gene:
            prob += PROBS["gene"][1]
            genes = 1
        elif person['name'] in two_genes:
            prob += PROBS["gene"][2]
            genes = 2
        else:
            prob += PROBS["gene"][0]
            genes = 0

        # calculate the chance they have the particular amount of genes and present (or not) the trait
        if person['name'] in have_trait:
            prob *= PROBS["trait"][genes][True]
        else:
            prob *= PROBS["trait"][genes][False]

        return prob

    def calculate_gene_passing(person):
        """
        Calculates the chance person passes a mutated gene to their child
        """
        # if parent has one good gene and one mutated, the chance they pass mutated one to child is 0.5
        # times the chance it doesn't mutate (1 - the chance it does mutate)
        if person['name'] in one_gene:
            prob = 0.5 * (1 - PROBS["mutation"])
        # if parent has two mutated genes, they'll pass a mutated gene to child, so the probability child gets
        # mutated gene is 1 times the chance it doesn't mutate
        elif person['name'] in two_genes:
            prob = 1 * (1 - PROBS["mutation"])
        # if parent doesn't have mutated genes, the only chance it passes one to child is if a good gene mutates
        else:
            prob = PROBS["mutation"]

        return prob

    def calculate_conditional(person):
        """
        Calculate the chance a person has the amount of genes required, and has the trait (or doesnt have it)
        Depending on which set (given as parameters to the joint_probability function) are they included in

        This function works for people from whose parents we have information about
        """
        father = people[person['father']]
        mother = people[person['mother']]

        chance_mother_passes = calculate_gene_passing(mother)
        chance_father_passes = calculate_gene_passing(father)

        prob = 0

        if person['name'] in one_gene:
            # probability is composed by adding two possible casses for the child having one mutated gene:
            # mather passes, father doesnt
            # father passes, mother doesnt
            prob = chance_mother_passes * (1 - chance_father_passes) + \
                chance_father_passes * (1 - chance_mother_passes)

            genes = 1
        elif person['name'] in two_genes:
            prob = chance_father_passes * chance_mother_passes
            genes = 2
        else:
            prob = (1 - chance_mother_passes) * (1 - chance_father_passes)
            genes = 0

        if person['name'] in have_trait:
            prob *= PROBS["trait"][genes][True]
        else:
            prob *= PROBS["trait"][genes][False]

        return prob

    # we calculate the joint probability of the events described in the parameters by
    # multiplying the individual chances of each of them happening
    total_prob = 1
    for person in people:
        current_person = people[person]
        # check if we have info about person's parents or not
        if current_person['father'] is None:
            total_prob *= calculate(current_person)
        else:
            total_prob *= calculate_conditional(current_person)

    return total_prob


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in one_gene:
        probabilities[person]["gene"][1] += p

    for person in two_genes:
        probabilities[person]["gene"][2] += p

    for person in have_trait:
        probabilities[person]["trait"][True] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
