# Heredity
An excercise in using a Bayesian network to determine the probability--based on information about their parent--that a child has 0, 1, or 2 copies of a damaged gene that causes hearing loss, and the probability that child will have hearing loss as a result. 

Gene testing can be expensive, so while it is easy to determine if a child has hearing loss, it is more difficult to determine how many copies of the damaged gene they have. At the most information-starved level, we can use parents' hearing loss to predict the probability distribution of a child's damaged gene count and the probability they will experience hearing loss as a result.

Three data sets are also included. Note that in all sets, every person has either two known or two unknown parents, and we are only dealing with two generations of a family.

## Bayesian Network

The number of damaged genes (gene count) is a hidden state that can be observed via a person possessing the trait hearing loss or not. Each person can have 0, 1, or 2 damaged genes and always recieves one gene from each parent. However, there is a small probability that a gene passed down by a parent will mutate (damaged to undamged or vice-versa). We have established data on the probability distributions in the general population of having 0, 1, or 2 damaged genes and the probability of experiencing hearing loss dependent on the person's gene count.

We can model all of these relationships by forming a Bayesian Network of all the relevant variables, as in the one below, which considers a family of two parents and a single child.

![gene_bayesian_network](https://github.com/user-attachments/assets/e7744571-2143-4389-90a0-74fd43bac6af)

The goal this project is to use this model to make inferences about a population. Given information about people, who their parents are, and whether they have a particular observable trait (e.g. hearing loss) caused by a given gene, the AI will infer the probability distribution for each person’s genes, as well as the probability distribution for whether any person will exhibit the trait in question.

# Functions
Below are a description of the functions I created, largely copied from the assignment description with some editorializing. 

## joint_probablity
The function returns the joint probability of all events taking place as described by the inputs. For readability, it calls gene_and_trait_probability which returns a pair of probabilities for gene-count and for trait-possession based on a global look up table I created called PUNNETT and PROBS. This pair of probabilities is then extended onto arr_probabilities iteratively until all probabilities have been determined for all people. Finally, all elements in arr_probabilities are producted to determine the joint probability for the possible world described by the inputs. 

* The function accepts four values as input: people, one_gene, two_genes, and have_trait.
  - people is a dictionary of people as described in the “Understanding” section. The keys represent names, and the values are dictionaries that contain mother and father keys. You may assume that either mother and father are both blank (no parental information in the data set), or mother and father will both refer to other people in the people dictionary.
  - one_gene is a set of all people for whom we want to compute the probability that they have one copy of the gene.
  - two_genes is a set of all people for whom we want to compute the probability that they have two copies of the gene.
  - have_trait is a set of all people for whom we want to compute the probability that they have the trait.
  - For any person not in one_gene or two_genes, we would like to calculate the probability that they have no copies of the gene; and for anyone not in have_trait, we would like to calculate the probability that they do not have the trait.
* For example, if the family consists of Harry, James, and Lily, then calling this function where one_gene = {"Harry"}, two_genes = {"James"}, and trait = {"Harry", "James"} should calculate the probability that Lily has zero copies of the gene, Harry has one copy of the gene, James has two copies of the gene, Harry exhibits the trait, James exhibits the trait, and Lily does not exhibit the trait.  
* For anyone with no parents listed in the data set, use the probability distribution PROBS["gene"] to determine the probability that they have a particular number of the gene.
* For anyone with parents in the data set, each parent will pass one of their two genes on to their child randomly, and there is a PROBS["mutation"] chance that it mutates (goes from being the gene to not being the gene, or vice versa).
* Uses the probability distribution PROBS["trait"] to compute the probability that a person does or does not have a particular trait; and uses PUNNETT[n] to compute the probability that a person has n copies of a broken gene.
* 
## update
The update function adds a new joint distribution probability to the existing probability distributions in probabilities.

* The function accepts five values as input: probabilities, one_gene, two_genes, have_trait, and p.
  - probabilities is a dictionary of people as described in the “Understanding” section. Each person is mapped to a "gene" distribution and a "trait" distribution.
  - one_gene is a set of people with one copy of the gene in the current joint distribution.
  - two_genes is a set of people with two copies of the gene in the current joint distribution.
  - have_trait is a set of people with the trait in the current joint distribution.
  - p is the probability of the joint distribution.

* For each person person in probabilities, the function updates the probabilities[person]["gene"] distribution and probabilities[person]["trait"] distribution by adding p to the appropriate value in each distribution.

* For example, if "Harry" were in both two_genes and in have_trait, then p would be added to probabilities["Harry"]["gene"][2] and to probabilities["Harry"]["trait"][True].

 ## normalize 
 The normalize function updates a dictionary of probabilities such that each probability distribution is normalized (i.e., sums to 1, with relative proportions the same).

* The function accepts a single value: probabilities.
- probabilities is a dictionary of people. Each person is mapped to a "gene" distribution and a "trait" distribution.
