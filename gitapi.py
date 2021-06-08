# gitapi interaction script

import os
import argparse
import platform
import subprocess
import requests

class GitApi:
    def __init__(self, ops):
        if platform.system() == "Windows":
            self.git = '"C:\\Program Files\\Git\\bin\\git.exe"'
        else:
            self.git = "git"
        self.user = ops.username
        self.pat = ops.pat
        if ops.task == "clone" or ops.task == "pr" or ops.task == "pr_comment" or ops.task == "pr_merge":
            self.repo = ops.repo
            org = ops.org
            if ops.org == "":
                org = self.user
            self.org = org
        if ops.task == "clone":
            # might want more checking around this path, ensure folder/repo name etc
            path = ops.path
            if ops.path == "":
                path = self.repo
            self.path = path
        elif ops.task == "commit":
            if ops.files == "A":
                self.files = ["-A"]
            else:
                self.files = ops.files.split(",")
            self.message = ops.message
        elif ops.task == "pull":
            self.branch = ops.branch
        elif ops.task == "push":
            branch = ops.branch
            if branch == "":
                branch = subprocess.run(self.git+' rev-parse --abbrev-ref HEAD', shell=True, check=True, text=True, stdout=subprocess.PIPE).stdout.strip()
            self.branch = branch
        elif ops.task == "pr":
            self.title = ops.title
            self.body = ops.body
            self.merge_to = ops.merge_to
            self.merge_from = ops.merge_from
        elif ops.task == "pr_comment":
            self.comment = ops.comment
            self.pr_num = ops.pr_num
        elif ops.task == "pr_merge":
            self.title = ops.title
            self.message = ops.message
            self.method = ops.method
            self.pr_num = ops.pr_num
    
    def show(self, task):
        if task == "branches":
            subprocess.run(self.git+' branch --list', shell=True, check=True)
        elif task == "commits":
            subprocess.run(self.git+' log', shell=True, check=True)

    def clone(self):
        # not a very secure way of doing this
        subprocess.run(self.git+' clone https://'+self.user+':'+self.pat+'@github.com/'+self.org+'/'+self.repo+' '+self.path, shell=True, check=True)
        # remove access token from config file at least
        cwd = os.getcwd()
        os.chdir(self.path)
        print ("repo cloned to "+os.getcwd())
        print ("stripping personal access token out of repo config")
        subprocess.run(self.git+' remote set-url origin https://github.com/'+self.org+'/'+self.repo, shell=True, check=True)
        os.chdir(cwd)

    def commit(self):
        for file in self.files:
            if file == "-A":
                print("adding all files")
            else:
                print("adding file "+file)
            subprocess.run(self.git+' add '+file, shell=True, check=True)
        subprocess.run(self.git+' commit -m "'+self.message+'"', shell=True, check=True)

    def pull(self):
        remote = subprocess.run(self.git+' remote get-url origin', shell=True, check=True, text=True, stdout=subprocess.PIPE).stdout.strip()
        remote = remote.split("//")[1]
        subprocess.run(self.git+' pull https://'+self.user+':'+self.pat+'@'+remote+' '+self.branch, shell=True, check=True)

    def push(self):
        remote = subprocess.run(self.git+' remote get-url --push origin', shell=True, check=True, text=True, stdout=subprocess.PIPE).stdout.strip()
        remote = remote.split("//")[1]
        subprocess.run(self.git+' push https://'+self.user+':'+self.pat+'@'+remote+' '+self.branch, shell=True, check=True)

    def pr(self):
        headers = {'Accept': 'application/vnd.github.v3+json'}
        payload = {'title': self.title,'body': self.body,'head': self.merge_from,'base': self.merge_to}
        r = requests.post('https://api.github.com/repos/'+self.org+'/'+self.repo+'/pulls', auth=(self.user, self.pat), json=payload, headers=headers)
        if r.status_code != 201:
            print("Something went wrong! Check the status code for more info: "+str(r.status_code))
        else:
            print("Pull request created "+r.json()["url"])

    def pr_comment(self):
        headers = {'Accept': 'application/vnd.github.v3+json'}
        payload = {'body': self.comment}
        r = requests.post('https://api.github.com/repos/'+self.org+'/'+self.repo+'/issues/'+self.pr_num+'/comments', auth=(self.user, self.pat), json=payload, headers=headers)
        if r.status_code != 201:
            print("Something went wrong! Check the status code for more info: "+str(r.status_code))
        else:
            print("Comment created "+r.json()["url"])

    def pr_merge(self):
        # doesn't currently work, might require a SHA
        headers = {'Accept': 'application/vnd.github.v3+json'}
        payload = {'commit_title': self.title,'merge_method': self.method}
        if self.message != "":
            payload["commit_message"] = self.message
        r = requests.post('https://api.github.com/repos/'+self.org+'/'+self.repo+'/pulls/'+self.pr_num+'/merge', auth=(self.user, self.pat), json=payload, headers=headers)
        if r.status_code != 200:
            print("Something went wrong! Check the status code for more info: "+str(r.status_code))
        else:
            print("PR merged!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="user to auth with")
    parser.add_argument("pat", help="personal access token to auth with")
    sub = parser.add_subparsers(dest="task", help="selects which task to perform")
    # show parser
    show_parser = sub.add_parser("show")
    show_parser.add_argument("show_task", choices=["branches","commits"])
    # clone parser
    clone_parser = sub.add_parser("clone")
    clone_parser.add_argument("repo", help="git repo to clone")
    clone_parser.add_argument("--org", help="git org or user the repo belongs to, default is current user", dest="org", default="")
    clone_parser.add_argument("--path", help="location to clone to, defaults to current dir", dest="path", default="")
    # commit parser
    commit_parser = sub.add_parser("commit")
    commit_parser.add_argument("files", help="comma seperated list of files to commit (no spaces), passing A commits all")
    commit_parser.add_argument("message", help="commit message")
    # pull parser
    pull_parser = sub.add_parser("pull")
    pull_parser.add_argument("--branch", help="branch to pull from, default is to pull all", dest="branch", default="")
    # push parser
    push_parser = sub.add_parser("push")
    push_parser.add_argument("--branch", help="branch to push to, default is current branch", dest="branch", default="")
    # pr parser
    pr_parser = sub.add_parser("pr")
    pr_parser.add_argument("repo", help="git repo to create the pull request in")
    pr_parser.add_argument("--org", help="git org or user the repo belongs to, default is current user", dest="org", default="")
    pr_parser.add_argument("title", help="title of the pull request")
    pr_parser.add_argument("body", help="body of the pull request")
    pr_parser.add_argument("merge_to", help="branch that is getting merged into")
    pr_parser.add_argument("merge_from", help="branch that is getting pulled in")
    # pr comment parser
    prcom_parser = sub.add_parser("pr_comment")
    prcom_parser.add_argument("repo", help="git repo containing the pull request to comment on")
    prcom_parser.add_argument("--org", help="git org or user the repo belongs to, default is current user", dest="org", default="")
    prcom_parser.add_argument("comment", help="text of your comment")
    prcom_parser.add_argument("pr_num", help="pull request number")
    # pr merge parser
    prmerge_parser = sub.add_parser("pr_merge")
    prmerge_parser.add_argument("repo", help="git repo containing the pull request to comment on")
    prmerge_parser.add_argument("--org", help="git org or user the repo belongs to, default is current user", dest="org", default="")
    prmerge_parser.add_argument("--title", help="title of your merge commit, default is 'PR merge'", dest="title", default="PR merge")
    prmerge_parser.add_argument("--message", help="detailed message of your merge commit, default is blank", dest="message", default="")
    prmerge_parser.add_argument("--method", help="merge method to use, merge, squash, or rebase, default is merge", dest="method", choices=["merge","squash","rebase"], default="merge")
    prmerge_parser.add_argument("pr_num", help="pull request number")
    
    ops = parser.parse_args()
    gitapi = GitApi(ops)
    
    if ops.task == "show":
        gitapi.show(ops.show_task)
    elif ops.task == "clone":
        gitapi.clone()
    elif ops.task == "commit":
        gitapi.commit()
    elif ops.task == "pull":
        gitapi.pull()
    elif ops.task == "push":
        gitapi.push()
    elif ops.task == "pr":
        gitapi.pr()
    elif ops.task == "pr_comment":
        gitapi.pr_comment()
    elif ops.task == "pr_merge":
        gitapi.pr_merge()