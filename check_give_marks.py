#!/usr/bin/env python3
import subprocess as sp
import os, time, sys, json, re

courses = []
if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <course_id [course_id [course_id ...]]>", file=sys.stderr)
    exit(1)
for i in range(1, len(sys.argv)):
    courses.append(sys.argv[i])
try:
    del os.environ['DISPLAY']
except:
    pass

text_to_notify: str = ""

def do_notify(title, text):
    print(F"notifying...\n{title}\n{text}")
    # implement your notification procedure here
    
    # wechat_notify and email_notify will not be available unless you implement them
    # res = sp.run(["wechat_notify", title, text])
    # print(res)
    # res = sp.run(["email_notify", title, text])
    # print(res)

def notify(title: str):
    global text_to_notify
    do_notify(title, text_to_notify)
    text_to_notify = ""

def add_notify(text: str):
    global text_to_notify
    text_to_notify += f"{text}  \n"

def save_to_file(course_id: str, assign: str, content: str):
    name = f'{course_id}_{assign}.txt'
    if os.access(name, os.F_OK):
        last_update = get_last_update(course_id, assign)
        os.rename(name, f'{course_id}_{assign}_{last_update}.txt')
    f = open(name, 'w')
    f.write(content)
    f.close()

def get_assigns(course_id: str) -> list:
    res = sp.run([course_id, 'classrun', '-assign'], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    assigns = res.stdout.decode('utf-8')
    assigns = assigns.strip()
    assigns = assigns.split('\n')
    assigns = [a for a in assigns if a != ""]
    if "sturec" in assigns:
        raise ValueError(f'"sturec" is in assignment list?? {assigns}')
    assigns.append("sturec")
    return assigns

def check_assign(course_id: str, assign: str) -> None:
    if assign == "sturec":
        res = sp.run([course_id, 'classrun', '-sturec'], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    else:
        res = sp.run([course_id, 'classrun', '-check', assign], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    curr = res.stdout
    curr = curr.decode('utf-8')
    filename = f'{course_id}_{assign}.txt'
    if os.access(filename, os.F_OK):
        f = open(filename, 'r')
        prev = f.read()
        f.close()
        if sanitize_check_result(curr) != sanitize_check_result(prev):
            save_to_file(course_id, assign, curr)
            record_last_update(course_id, assign)
            add_notify(f"Your marks for {course_id} {assign} has changed!!")
    else:
        save_to_file(course_id, assign, curr)
        record_last_update(course_id, assign)

def get_last_update(course_id: str, assign: str) -> int:
    f = open(f'{course_id}_last_update.json', 'r')
    last_update = json.load(f)
    last_update = int(last_update[assign])
    return last_update

def record_last_update(course_id: str, assign: str) -> None:
    try:
        f = open(f'{course_id}_last_update.json', 'r')
        last_update = json.load(f)
        f.close()
    except FileNotFoundError:
        last_update = {}
    last_update[assign] = int(time.time())
    f = open(f'{course_id}_last_update.json', 'w')
    json.dump(last_update, f)
    f.close()

def sanitize_check_result(content: str) -> str:
    #_orig = content
    content = re.sub(r'^Current day and time:.+$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^Assignment deadline:.+$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^A submission now would be.+$', '', content, flags=re.MULTILINE)
    #print(f"\n========orig=========\n{_orig}=========new=========\n{content}")
    return content


if __name__ == '__main__':
    for c in courses:
        assigns = get_assigns(c)
        time.sleep(1)
        for ass in assigns:
            check_assign(c, ass)
            time.sleep(5)
    if text_to_notify != "":
        notify("Your marks has changed")
