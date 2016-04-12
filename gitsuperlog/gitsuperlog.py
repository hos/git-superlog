import sys
import os

import re
from datetime import datetime
from itertools import accumulate
import argparse
import logging
import helper

import git
from git.compat import (
    defenc,
    PY3
)

from git.util import (
    Actor,
    Iterable,
    Stats,
    finalize_process
)

EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
# logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument("repo_path", type=str,
                    help="Path to the repository")
parser.add_argument("-u", "--unwanted-extensions", type=str,
                    help="Extensions that will be excluded from counting")
parser.add_argument("-o", "--output", type=str,
                    help="CSV output")


def __main__():
    args = parser.parse_args()


    repo_path = args.repo_path
    repo = git.Repo(repo_path)

    if args.unwanted_extensions:
        unwantedExtensions = []
        for i in args.unwanted_extensions.split(","):
            i = i.strip()
            if not i[0] == ".":
                i = "." + i
            unwantedExtensions.append(i)
        print("Excluding extensions: %s"%(unwantedExtensions))
    else:
        unwantedExtensions = []
        # columns = None




    # the below gives us all commits
    # commits = repo.commit('master')
    commits = list(repo.iter_commits('master'))
    commits.reverse()

    # for i in dir(commits[0]):
    #     print(i)

    # trees = repo.tree().trees
    # print(len(trees))
    # for i in commits:
    #     print(i.tree.diff)

    timestamps = []
    summaries = []

    # take the first and last commit

    # a_commit = repo.commits()[0]
    # b_commit = repo.commits()[1]

    # now get the diff
    # repo.diff(a_commit,b_commit)

    totalChange = []

    diffArgs = dict(diff_filter="AMD",
                    find_renames=True,
                    ignore_space_change=True,
                    find_copies_harder=True,
                    ignore_all_space=True)

    # diffArgs = dict(patch_with_stat=True)


    def getStatsFromPatch(p):
        insertions = 0
        deletions = 0
        lines = p.split('\n')
        for i in lines[3:]:
            if len(i) == 0:
                continue
            if i[0] == "-":
                insertions += 1
            elif i[0] == "+":
                deletions += 1

        return insertions, deletions


    for i in commits:
        total = 0


        if not i.parents:
            diff = i.diff(EMPTY_TREE_SHA, create_patch=True, **diffArgs)
        else:
            diff = i.diff(i.parents[0], create_patch=True, **diffArgs)

        summaries.append(i.summary)
        timestamps.append(i.committed_date)


        dt = datetime.fromtimestamp(timestamps[-1])
        day = datetime.date(dt)
        dt_str = day.strftime("%a, %b %d %Y")

        logging.debug("\n\n\n>>> %s\n%s\n\n\n "%(dt_str,i.summary))


        # for diff_added in diff.iter_change_type('A'):
        # for k in diff.iter_change_type('M'):
        for k in diff:
            if k.renamed:
                logging.debug("RENAMED: %s  ->  %s"%(k.b_path, k.a_path))
                continue
            a_ext = os.path.splitext(k.a_path)[1]
            b_ext = os.path.splitext(k.b_path)[1]

            if (a_ext in unwantedExtensions) or (b_ext in unwantedExtensions):
                continue

            try:
                msg = k.diff.decode(defenc)
            except UnicodeDecodeError:
                continue

            # print("BEGIN"); print(msg); print("END")

            insertions,deletions = getStatsFromPatch(msg)

            netChange = insertions
            logging.debug("%s Insertions %s Deletions %s"%(k.b_path, insertions, deletions))
            total += abs(netChange)

            # lines = msg.split('\n')
            # if len(lines) >= 2:
            #     rangeInfo = lines[2]
            #     # print(rangeInfo)
            #     data = re.findall('@@ \-(\d+),(\d+) \+(\d+),(\d+) @@',rangeInfo)
            #     # print(data)
            #     # for l in lines[:2]:
            #         # print(l)
            #     # print(rangeInfo, data, )
            #     try:
            #         a = int(data[0][3])
            #         b = int(data[0][1])
            #         # netChange = a + b
            #         netChange = a
            #         print(k.b_path, a, b)
            #         total += abs(netChange)
            #         # print(netChange)
            #     except:
            #         pass

        logging.debug("Change : %d"%(total))

        totalChange.append(total)


    cumulative = list(accumulate(totalChange))

    for c,i,cum,s in zip(timestamps, totalChange, cumulative, summaries):
        # timestamp = c.committed_date

        dt = datetime.fromtimestamp(c)
        day = datetime.date(dt)
        dt_str = day.strftime("%a, %b %d %Y")
        print("%s | % 7d  | Cum: % 7d  --  %s"%(dt_str, i, cum, s))

    print("TOTAL CHANGE: %d"%(sum(totalChange)))


    if args.output:

        opath = args.output
        ofile = open(opath, "w")
        import csv

        owriter = csv.writer(ofile, delimiter=" ")
        outarray = helper.transpose([timestamps, totalChange, cumulative])

        owriter.writerows(outarray)

        ofile.close()

if __name__ == "__main__":
    __main__()
