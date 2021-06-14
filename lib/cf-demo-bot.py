import fileinput
import os
import sys
import subprocess
import time
from github import Github


def run_command(full_command):
    proc = subprocess.Popen(full_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = proc.communicate()
    print(output)
    if proc.returncode != 0:
        sys.exit(1)
    return b''.join(output).strip().decode()  # only save stdout into output, ignore stderr

def replace_line(file_name, line_num, text):
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()


def main():

    choice_a = os.getenv('CHOICE_A')
    choice_b = os.getenv('CHOICE_B')
    jira_issue_id = os.getenv('JIRA_ISSUE_ID')
    target_branch = os.getenv('TARGET_BRANCH')
    github_token = os.getenv('GITHUB_TOKEN')
    revision = os.getenv('REVISION')
    repo_name = os.getenv('REPO_NAME')
    repo_owner = os.getenv('REPO_OWNER')

    # Configure git

    output = run_command('git config --global user.email "salesdemocf@gmail.com"')
    print(output)

    output = run_command('git config --global user.name "Freshbot"')
    print(output)

    code_friendly_place = choice_a.replace(' ', '-').lower()

    code_friendly_resort = choice_b.replace(' ', '-').lower()

    # Clean directory

    output = run_command('rm -rf /codefresh/volume/{}'.format(repo_name))
    print(output)

    # Clone repository

    output = run_command('git clone https://{}:{}@github.com/{}/{}.git /codefresh/volume/{}'.format(repo_owner, github_token, repo_owner, repo_name, repo_name))
    print(output)

    # Change working directory

    os.chdir('/codefresh/volume/{}'.format(repo_name))

    # Clean remote branches

    try:
        output = run_command('git branch -r | grep origin/ | grep -v \'main$\' | grep -v HEAD| cut -d/ -f2 | while read line; do git push origin :$line; done;')
        print(output)
    except:
        pass

    try:
        output = run_command('git branch | grep -v "main" | xargs git branch -D')
        print(output)
    except:
        pass

    # Create branch

    feature_branch = '{}-{}-or-{}'.format(jira_issue_id, code_friendly_place, code_friendly_resort)
   
    output = run_command('git checkout -b {}'.format(feature_branch))
    print(output)

    # Replace lines

    replace_line('tests/selenium/test_app.py', 34, '    option_a = "{}"\n'.format(choice_a))
    replace_line('tests/selenium/test_app.py', 35, '    option_b = "{}"\n'.format(choice_b))

    replace_line('vote/app.py', 7, 'option_a = os.getenv(\'OPTION_A\', "{}")\n'.format(choice_a))
    replace_line('vote/app.py', 8, 'option_b = os.getenv(\'OPTION_B\', "{}")\n'.format(choice_b))

    replace_line('result/views/index.html', 22, '            <div class="label">{}</div>\n'.format(choice_a))
    replace_line('result/views/index.html', 27, '            <div class="label">{}</div>\n'.format(choice_b))

    # Create commit
    output = run_command('git commit -am "update for {}"'.format(feature_branch))
    print(output)

    # Push commit

    output = run_command('git push --set-upstream origin {}'.format(feature_branch))
    print(output)

    # Sleep

    time.sleep(30)

    # PyGitHub Auth

    g = Github(github_token)

    # Set repo

    repo = g.get_repo('{}/{}'.format(repo_owner, repo_name))

    # Create pull request

    create_pull_request = repo.create_pull(title='Pull Request from Freshbot', head=feature_branch, base=target_branch, body='Automated Pull Request', maintainer_can_modify=True)

    # get_pull_request_build_id

    pull_request = repo.get_pull(create_pull_request.number)

    merge_pull_request = None
    while merge_pull_request is None:
        try:
            print('Waiting 600 seconds for Pull Request builds')
            time.sleep(600)
            merge_pull_request = pull_request.merge(commit_title='Freshbot Demo Automation', commit_message='Committed by Codefresh Freshbot', merge_method='merge')
        except:
            pass

    # create_release

    time.sleep(5)

    branch_data = g.get_repo('{}/{}'.format(repo_owner, repo_name)).get_branch(target_branch)

    repo.create_git_tag_and_release(tag='4.0.{}'.format(revision), tag_message='Freshbot Demo Automation', object=branch_data.commit.sha, type='sha', release_name='{} vs. {}'.format(choice_a, choice_b), release_message='Freshbot Demo Automation', prerelease=False)

if __name__ == "__main__":
    main()
