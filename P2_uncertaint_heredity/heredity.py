import csv
import itertools
import sys

debug = True


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


'''
Each punnet square indicates probability distribution thatoffspring has n genes 
given any permutation of parent gene counts

                                        Parent A
            
        Broken Gene Count     |   0 |     1 |     2 |
                              |  aa |    Aa |    AA |
        ---------------------------------------------
                        0 bb  |   P |     P |     P |  
        Parent B        1 Bb  |   P |     P |     P | 
                        2 BB  |   P |     P |     P | 
                        
Example:    Without considering mutations, parents with genes Aa and Bb have equal prob of 
            producing child with AB, Ab, aB, ab. However, mutation means each gene has a
            0.01 chance of mutating, so even a child given AB genes could have them mutate into ab.
            
            First weight the probability for each genotype without considering mutations.
            Then determine what combination of mutations and unmutations would result in desired gene count.
            Then calculate the probabilities
            
'''
mut = PROBS['mutation']
unmut = 1 - mut

two_gene_punnett = [[0, 1, 2], 
                    [3, 4, 5], 
                    [6, 7, 8]]
# 1.0 chance of ab requiring (a mut and b mut)
two_gene_punnett[0][0] = mut * mut  
# .5 chance of Ab requiring (A unmut and b mut) and .5 chance of ab requiring (a mut and b mut)
two_gene_punnett[0][1] = .5*(unmut * mut) + .5* (mut * mut)
# 1.0 chance of Ab requiring (A unmut and b mut)
two_gene_punnett[0][2] = unmut * mut 
# Matrix is symmetric      
two_gene_punnett[1][0] = two_gene_punnett[0][1]
# .25 chance AB requring (A unmut and B unmut) and .25 chance ab requiring (a mut and b mut) and .25 chance of Ab requiring (A unmut and b mut) * 2 because aB is symmetrical
two_gene_punnett[1][1] = .25*(unmut * unmut) + .25*(mut * mut) + 2*.5*(unmut * mut) 
# .5 chance Ab requiring (A unmut and b mut) and .5 chance AB requiring (A unmut and B unmut)
two_gene_punnett[1][2] = .5*(unmut * mut) + .5*(unmut * unmut)
# Matrix is symmetric 
two_gene_punnett[2][0] = two_gene_punnett[0][2]
# Matrix is symmetric 
two_gene_punnett[2][1] = two_gene_punnett[1][2]
# 1.0 chance of AB requiring (A unmut and B unmut)
two_gene_punnett[2][2] = unmut * unmut 



# This punnett is more complicated. New notation: let A be unbroken gene for parentA and b be broken gene for parentB
one_gene_punnett = [[0, 1, 2], 
                    [3, 4, 5], 
                    [6, 7, 8]]
# 1.0 chance ab requiring (a mut and b unmut OR a unmut and b mut)
one_gene_punnett[0][0] = mut*unmut + unmut*mut   
# .5 chance of ab requiring (a mut and b unmut OR a unmut and b mut) OR .5 chance of Ab requiring (A unmut and b unmut OR A mut and b mut)
one_gene_punnett[0][1] = .5*(mut*unmut + unmut*mut) + .5*(unmut*unmut + mut*mut)   
# 1.0 chance of Ab, requiring (A unmut and b unmut OR A mut and b mut)          
one_gene_punnett[0][2] = unmut*unmut + mut*mut
# Matrix is symmetric 
one_gene_punnett[1][0] = one_gene_punnett[0][1]
#.25 chance of AB requiring (A mut and B unmut OR A unmut and B mut) * 2 for ab; .25 chance of Ab requiring (A unmut and b unmut OR A mut and b mut ) * 2 for aB
one_gene_punnett[1][1] =  .5*(mut*unmut + unmut*mut) + .5*(unmut*unmut + mut*mut) 
# .5 chance of AB requring (A mut and B unmut OR A unmut B mut) OR .5 chance of Ab requiring (A unmut and b unmut OR A mut and b mut)
one_gene_punnett[1][2] = .5*(mut*unmut + unmut*mut) + .5*(unmut*unmut + mut*mut)
# Matrix is symmetric 
one_gene_punnett[2][0] = one_gene_punnett[0][2]
# Matrix is symmetric 
one_gene_punnett[2][1] = one_gene_punnett[1][2]
# 1.0 chance of AB requiring (A mut and B unmut OR A unmut and B mut)
one_gene_punnett[2][2] = mut*unmut + unmut*mut 

# zero and two punnetts are just 180 degree rotated
zero_gene_punnett = [[0, 1, 2], 
                    [3, 4, 5], 
                    [6, 7, 8]]
for i in range(3):
    for j in range(3):
        zero_gene_punnett[3-1-i][3-1-j] = two_gene_punnett[i][j]

PUNNETT = [zero_gene_punnett, one_gene_punnett, two_gene_punnett]

def main():

    # Check for proper usage
    '''
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    
    people = load_data(sys.argv[1])
    '''
    people = load_data("C:/Users/Kanoa/Projects/CS50/P2 Uncertainty/heredity/data/family0.csv")
    

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
                #print(one_gene)
                
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
                
        
                
    '''
    Do quick and dirty testing here
    '''
    #joint_probability(people, {"Harry"}, {"James"}, {"James"})            
                
   
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
    arr_probabilities = []  #Store all the probabilities enumerated above
    for person in people:
        arr_probabilities.extend(gene_and_trait_probability(people, person, one_gene, two_genes, have_trait))
     
    prob_product = 1
    for prob in arr_probabilities:
        prob_product = prob_product * prob
        
    if(debug):
        print(f"IN THE POSSIBLE WORLD\none_gene={one_gene}, \ntwo_genes={two_genes}, \nhave_trait={have_trait}\njoint_prob = {prob_product}")
    return prob_product
    


def gene_and_trait_probability(people, person, one_gene, two_genes, have_trait):
    '''
    Use Punnett square LUTs to determine probability that the person in people
    will have a certain number of broken genes based on parents' gene count.
    A person without listed parents uses prob. dist. for general population.
    
    Returns the list [gene_prob, trait_prob].
    gene_prob is the probabilty person has the indicated gene count based on parents gene count.
    trait_prob is the probability person has/doesn't have hearing impairment based on their indicated gene count
    
    Note: no entry in my test data has one known and on unknown parent, so this 
    case is not handled here but could easily be implemented. 
    '''

    if person in (two_genes):
        gene_count = 2
    elif person in (one_gene):
        gene_count = 1
    else:
        gene_count = 0
        
    gene_prob = None
    trait_prob = PROBS['trait'][gene_count][bool(person in have_trait)]
    mother_gene = None
    father_gene = None

    # If person has no listed parent, represent parent gene count using general population statistics in PROBS['gene'] 
    if(people[person]['mother'] == None or people[person]['father'] == None):   #No one in data sets has one known and unknown parent
        gene_prob = PROBS['gene'][gene_count]

    else:
        # Determine how many broken genes the mother has in this possible world
        if people[person]['mother'] in (two_genes):
            mother_gene = 2
        elif people[person]['mother'] in (one_gene):
            mother_gene = 1
        else:
            mother_gene = 0

        # Determine how many broken genes the father has in this possible world
        if people[person]['father'] in (two_genes):
            father_gene = 2
        elif people[person]['father'] in (one_gene):
            father_gene = 1
        else:
            father_gene = 0
            
        # Use the punnett LUTs to determine probability person will have desired gene count based on parents' gene count
        gene_prob = PUNNETT[gene_count][father_gene][mother_gene]
 
    if(debug): 
        print(f"{person} has gene_prob = {gene_prob} and trait_prob = {trait_prob} when gene_count = {gene_count}, mother_gene = {mother_gene}, father_gene = {father_gene}")
        #print(f"{person} has gene_prob = {gene_prob} and trait_prob = {trait_prob} in possible world when gene_count = {gene_count}, mother_gene = {mother_gene}, father_gene = {father_gene}") 
    return [gene_prob, trait_prob]



def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    # For each person, check what trait and gene count they have in this possible world,
    # then update the corresponding entries in probabilities with p
    for person in probabilities:
        # Should probabilities update True or False key of prob['person']['trait']
        bool_trait = bool(person in have_trait)
        
        # Should probabilities update 2, 1, or 0 key of prob['person']['gene'] 
        if person in (two_genes):
            gene_count = 2
        elif person in (one_gene):
            gene_count = 1
        else:
            gene_count = 0
            
        # Update correct entry of probabilities by adding a new joint possibilty
        probabilities[person]['trait'][bool_trait] += p
        probabilities[person]['gene'][gene_count] += p
        
        
def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    
    To normalize, take sum of all probabilties then divide each probability by the sum
    """
    for person in probabilities: 
        # Get the sum of all probabilities in each prob. distribution
        sum_prob = [0, 0]   # [sum of gene probabilities, sum of trait probabilities]
        sum_prob[0] = sum(probabilities[person]['gene'].values())
        sum_prob[1] = sum(probabilities[person]['trait'].values())
            
        # Divide each value in prob. dist. by its respective sum to noramlize it
        if(sum_prob[0] != 0 and sum_prob[1] != 0):
            for gene in probabilities[person]['gene']:
                probabilities[person]['gene'][gene] = probabilities[person]['gene'][gene] / sum_prob[0]
            for trait in probabilities[person]['trait']:
                probabilities[person]['trait'][trait] = probabilities[person]['trait'][trait] / sum_prob[1]
       
    
    


if __name__ == "__main__":
    main()




