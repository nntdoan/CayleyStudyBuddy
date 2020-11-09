from os.path import exists, join, basename, splitext
from stackapi import StackAPI
from lxml import html, etree
import subprocess as sp
import requests
import json
import time
import glob
import os


# Some math-related tags that are Cayley does not need to know
_notinclude = ["math-software", "book-recommendation", "mathematica", "matlab", "soft-question", "recreational-mathematics", "networkx", "python", "recreational-mathematics", "online-resources"]



def fetch_stack_posts(_siteToQuery='math', _tags="graph-theory", _nottags=_notinclude, _sort='votes', _accepted=True, log=False):
    ''' Currently do not support multiple tags and nottags.
    '''
    # fetch the data
    SITE = StackAPI(_siteToQuery, max_pages=200)
    queries = SITE.fetch('search/advanced', order='desc', min=1, sort=_sort, tagged=_tags, nottagged=_nottags[-1], accepted=_accepted)
    questions = queries['items']
    if log:
        print("Original fetch: %d items."%len(questions))
    # clean the data
    _nottags.pop() #query the items without the last tags already
    questions = clean(questions, nottagged=_nottags) 
    if log:
        print("After clean: %d items."%len(questions))
    # remove old data of the site if exist
    site_files = glob.glob(f"./data/*_{_tags}.json")
    if len(site_files)!=0:
        for f in site_files:
            os.remove(f)
    # store the data
    filename = time.strftime("%Y%m%d_%H%M%S") + "_" + _tags + ".json"
    pathtofile = os.path.join("./data", filename)
    with open(pathtofile, 'w') as file:
        json.dump(questions, file)
    if log:
        print(f"Data saved at {os.path.abspath(pathtofile)}")

    return



def clean(data, _to_keep=["tags", "accepted_answer_id", "score", "question_id", "link", "title"], nottagged=[]):
    ''' Remove unnessessary data such as details of the person who posted the questionss, etc.
    '''
    # Need a more efficient ways to do this
    to_remove_keys = [k for k in data[0].keys() if k not in _to_keep]
    cleaned_data = []
    nottagged = set(nottagged)
    for item in data:
        if bool(nottagged.intersection(set(item["tags"]))): continue
        else:
            for k in to_remove_keys:
                item.pop(k, None)
            cleaned_data.append(item)
    return cleaned_data



def parse_a_post(url,accepted_answer_id=None):
    ''' Parse the data for extract the content of the post (question) and answer for Cayley to use.
    Return the details of the question and the accepted answer.
    '''
    if not accepted_answer_id:
        raise Exception('Must provide accepted answer ID! Cayley only accepts legit answers')
    else:
        page = requests.get(url) 
        tree = etree.HTML(page.content)
        post = tree.xpath('string(//*[@id="question"]/div[2]/div[2]/div[1])')
        answer = tree.xpath(f'string(//*[@id="answer-{accepted_answer_id}"]/div/div[2]/div[1])')
    return post, answer 


def render_tex(to_render, path_to_png='tex/temp.png'):
    '''Shell commands to render Latex math display. 
    :param to_render: string
    :return None
    '''
    # create the tex file with the tex in Latex in it
    with open('tex/preamble.tex') as f:
        buffer = f.read()
    buffer+= "\n"+to_render+"\n \end{document}"
    with open('tex/temp.tex', 'w') as f:
        f.write(buffer)
    try:
        # convert the file to pdf     
        p = sp.run('xelatex tex/temp.tex -output-directory="./tex"', shell=True, check=True)
        # convert the file to png
        p = sp.run(f'pdftoppm -png tex/temp.pdf > {path_to_png}', shell=True, check=True)
    except Exception as e:
        print(e)
    return 


if __name__ == "__main__":
    # uncomment to query the questions
    fetch_stack_posts(log=True)
