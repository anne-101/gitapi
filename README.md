gitapi - a python script for interacting with git

This script uses a mixture of local git and the git REST api.

List of Commands

show

this takes one parameter, and it must be either branches or commits, branches will list all branches, commits will show the recent set of commits

EX: gitapi.py anne $token show branches


clone

this cmd has 1 required param and 2 optional ones.  You must pass the repo, you also have the option of passing the git user/organization that owns the repo, if this is not set the script assumes the user is the owner. You may also pass the desired path location for the repo to clone to. NOTE, if using --path this is RELATIVE to your current dir and you must be sure the final folder you specify is empty.

EX: gitapi.py anne $token clone test-repo --org ProbablyMonsters --path ../test-repo


commit

this cmd has 2 required params. You must pass a comma seperated list of files to be commited (passing just A commits all files) and you must pass a commit message.

EX: gitapi.py anne $token commit README.md,gitapi.py "commiting my list of files"


pull

this cmd has 1 optional param. You may provide a branch specifier if you want to pull in that branch instead of your current branch.

EX: gitapi.py anne $token pull --branch test


push

this cmd has 1 optional param. You may provide a branch specifier if you want to push to that branch instead of your current branch.

EX: gitapi.py anne $token push --branch test


pr

this cmd has 5 required params and 1 optional param. You must pass the repo, you also have the option of passing the git user/organization that owns the repo, if this is not set the script assumes the user is the owner. You must pass the title of your PR, the body of your PR, the branch getting merged into, and the branch getting pulled in.

EX: gitapi.py anne $token pr test-repo --org ProbablyMonsters "Code PR" "This is my code PR" main test


pr_comment

this cmd has 3 required params and 1 optional param. You must pass the repo, you also have the option of passing the git user/organization that owns the repo, if this is not set the script assumes the user is the owner. You must pass the comment to be made and you must pass the number of the PR being commented on.

EX: gitapi.py anne $token pr test-repo --org ProbablyMonsters "I am commenting now" 4


pr_merge

this cmd has 2 required params and 4 optional params. You must pass the repo, you also have the option of passing the git user/organization that owns the repo, if this is not set the script assumes the user is the owner. You must pass the number of the PR that is being merged. You also may set the PR merge title, default is "PR merge", you may also set the detailed message for the merge commit, the default is left blank, and finally you may set the merge method to be used, merge, squash, or rebase.

EX: gitapi.py anne $token pr test-repo --org ProbablyMonsters --title "Merging this PR" --message "merging it so good" --method squash 4

NOTE: currently p4_merge is non functional, it may require a git SHA as well
