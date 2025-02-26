import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


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
    a link at random chosen from all pages in the corpus.
    """
    distribution = dict()
    # check if the page has any links, if none then return a uniform distribution
    if len(corpus[page]) == 0:
        for page_name in corpus.keys():
            distribution[page_name] = 1/len(corpus)

    # if the page has links do the calculations
    else:
        for page_name in corpus.keys(): 
            distribution[page_name] = (1-damping_factor)/len(corpus)  # for random visit
        for page_name in corpus[page]:
            distribution[page_name] += damping_factor/len(corpus[page])  # for links from page

    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    sample_list = [random.choice(list(corpus.keys()))]  # start with a random page

    #create n-1 new samples
    for i in range(n-1):
        current_page = sample_list[-1]
        distribution = transition_model(corpus, current_page, damping_factor)
        keys = list(distribution.keys())
        probabilities = list(distribution.values())
        random_page = random.choices(keys, weights=probabilities, k=1)[0]
        sample_list.append(random_page)
    
    # find probability distribution from sample_list
    rank_distribution = dict()
    for page_name in corpus.keys():
        rank_distribution[page_name] = sample_list.count(page_name)/n

    return rank_distribution


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    # start by assigning 1/N to each page
    rank_distribution = {page_name: 1/N for page_name in corpus.keys()}
    no_link_pages = [page_name for page_name in corpus.keys() if len(corpus[page_name])==0]
    while True:
        is_all_done = True
        # recalculate pagerank for each page once
        for page_name in corpus.keys():
            old_rank = rank_distribution[page_name]
            
            # find the pages that have link to this page, include no_link_pages too
            page_links = [page_name2 for page_name2 in corpus.keys() if page_name in corpus[page_name2]]+no_link_pages
            
            # calculate the new rank
            new_rank = (1-damping_factor)/N
            for page_name3 in page_links:
                if len(corpus[page_name3]) == 0:
                    new_rank += damping_factor*rank_distribution[page_name3]/N
                else:
                    new_rank += damping_factor*rank_distribution[page_name3]/len(corpus[page_name3])
            rank_distribution[page_name] = new_rank

            # check if old and new ranks are closer than 0.001
            if abs(old_rank-new_rank) > 0.001:
                is_all_done = False
        
        if is_all_done:
            break
    return rank_distribution


if __name__ == "__main__":
    main()
