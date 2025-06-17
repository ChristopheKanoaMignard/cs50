import os
import random
import re
import sys

debug = False
corpus_dirs = ['corpus0', 'corpus1', 'corpus2']

DAMPING = 0.85
SAMPLES = 10000


def main():
    if not debug:   # Allows running from command line else from IDE
        if len(sys.argv) != 2:
            sys.exit("Usage: python pagerank.py corpus")
        corpus = crawl(sys.argv[1])
    else:
        # Make a dictionary where keys are html file names and values are html file names linked to by the key file
        corpus = crawl(corpus_dirs[0])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
     
    ''' 
    Quick and dirty tests here
    '''
    if debug:
        test_corpus =  {'1': {'2'}, 
                        '2': {'3', '1'}, 
                        '3': {'2', '4', '5'}, 
                        '4': {'2', '1'}, 
                        '5': set()}
        print(transition_model(test_corpus, '1', DAMPING))
        print(sample_pagerank(test_corpus, DAMPING, 1000))
        print(iterate_pagerank(test_corpus, DAMPING))


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages

def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus. If no pages
    are linked, give equal probability to all pages. 
    """
    prob_dist = dict()                  # Dictionary containing probability distributions for each page in network
    all_pages = list(corpus.keys())     # List of all page names in network
    num_pages = len(all_pages)          # Number of pages in network
    linked_pages = list(corpus[page])   # List of pages linked to by page
    num_links = len(linked_pages)       # Number of pages linked to by page
    
    if num_links == 0:
        # If current page doesn't link to any other pages, equal prob of trans to any page
        prob_dist = {key: (1/num_pages) for key in corpus} 
      
    else:   
        # Else, each page has a (1-damping_factor) / num_pages probability...
        prob_dist = {key: ((1-damping_factor)/num_pages) for key in corpus} 
        
        # ...and linked pages have an additional probability of damping_factor / num_links    
        for p in all_pages:
            if p in linked_pages:
                prob_dist[p] += damping_factor / num_links
    
    return prob_dist      

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """   
    all_pages = list(corpus.keys())             # List of all page names in network
    prob_dist = dict()                          # Probability distribution for the current page to reach other pages
    page_hits = {key: 0 for key in corpus}      # Number of times a page has been visited while sampling
    page_rank = {key: 0 for key in corpus}      # Return variable
    page = str(random.choice(all_pages))        # Randomly choose a starting page
    
    for sample in range(n):
        # Generate a probability distribution based on random surfer following links on current page or teleporting
        prob_dist = transition_model(corpus, page, damping_factor)
        # Choose a new page at random weighted by probability distribution
        page = str(random.choices(list(prob_dist.keys()), 
                                  weights=list(prob_dist.values())))[2:-2]
        # Increment the number of times the new page has been visited
        page_hits[page] += 1
        
    # Set page rank equal to number of times a site was visited / number of sites visited
    for p in all_pages:
        page_rank[p] = page_hits[p] / n
        
    return page_rank
        
def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    all_pages = list(corpus.keys())                     # List of all page names in network
    num_pages = len(all_pages)
    page_rank = {key: (1/num_pages) for key in corpus}  # Return variable
    page_rank_change = 0                                # Difference between current and old page rank value for current page
    change_tolerance = 0.001
    
    # Check that every page has at least one link. If no links, treat it as linking to every page
    for p in all_pages:
        if len(corpus[p]) == 0:
            corpus[p] = all_pages
    
    # Loop until difference between current page rank and previous iteration's is <change_tolerance for all pages
    keep_looping = True
    while(keep_looping):
        old_page_rank = page_rank.copy()    # Make a copy of the previous iteration's page rank
        keep_looping = False                # Reset bool to leave loop unless any page's PageRank changes too much 
        
        if debug:
            print("New loop")
        
        for p in all_pages:
            # Implement PageRank iteration formula
            
            # First term is probability of a surfer on another page jumping to p from any page
            page_rank[p] = (1 - damping_factor) / num_pages
            
            # Loop over all pages, and if a page links to current page, p, calculate its effect on p's PageRank
            for linker in all_pages:
                if p in corpus[linker]:
                    page_rank[p] += damping_factor * page_rank[linker] / len(corpus[linker])
                # if linker has no links, treat it as linking to every page
                elif len(corpus[linker]) == 0:
                    page_rank[p] += damping_factor * page_rank[linker] / num_pages
                    
            # If any p's PageRank changes too much during this iteration of while, keep looping
            page_rank_change = abs(page_rank[p] - old_page_rank[p])
            if debug:
                print(f"{p}'s rank changed by {page_rank_change}")
            if (page_rank_change > change_tolerance):
                keep_looping = True
            
    return page_rank
    


if __name__ == "__main__":
    main()
    

