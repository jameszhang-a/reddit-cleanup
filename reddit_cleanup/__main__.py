import praw
from prawcore import ResponseException, OAuthException
from PyInquirer import prompt, print_json, Separator, style_from_dict
from validator import NumberValidator
from datetime import datetime


def ask_type():
    main_prompt = {
        "type": "list",
        "name": "cleanup-type",
        "message": "Do you want to clean up in general or for specific subreddits?",
        "choices": ["General", "Subreddits"],
    }

    answer = prompt(main_prompt)
    if answer:
        return answer["cleanup-type"]
    else:
        return


def ask_karma():
    question = {
        "type": "input",
        "name": "karma",
        "message": "Comments below how many upvotes would you like to delete",
        "validate": NumberValidator,
        "filter": lambda val: int(val),
    }

    karma = prompt(question)
    return karma["karma"]


def ask_delete():
    q = [
        {
            "type": "list",
            "name": "mode",
            "message": "Do you want to preview any comments or nuke it all?",
            "choices": ["Preview", "NUKE"],
        },
        {
            "type": "input",
            "name": "display_limit",
            "message": "How many would you like to preview? (limit: 1000)",
            "validate": NumberValidator,
            "filter": lambda val: int(val),
            "when": lambda answers: answers["mode"] == "Preview",
        },
    ]

    answers = prompt(q)
    return answers


def fcomment(comment):
    upvotes, body, time, sub = (
        comment.score,
        comment.body,
        datetime.fromtimestamp(comment.created_utc),
        comment.subreddit,
    )

    return f"upvotes: {upvotes} \t created: {time} \t subreddit: {sub}\n{body}\n"


def select_delete(choices):
    q = {
        "type": "checkbox",
        "qmark": "😃",
        "message": "select comments",
        "name": "comments",
        "choices": choices,
    }

    answers = prompt(q)
    print(answers)


def main():
    try:
        reddit = praw.Reddit("bot1")
        me = reddit.user.me().comments.new(limit=3)
    except ResponseException:
        print("Your reddit app ID/secret is likely wrong")
        print("exiting...")
        return
    except OAuthException:
        print("Your reddit username and password is likely wrong")
        print("exiting...")
        return

    # print(sum(1 for _ in me))

    # whether all of reddit or for specific subs
    type = ask_type()
    if type == "General":
        threshold = ask_karma()
        delete_mode = ask_delete()
        print(delete_mode)

        mode = delete_mode["mode"]

        if mode == "NUKE":
            for i, cid in enumerate(me):
                cid = str(cid)
                comment = reddit.comment(id=cid)

                if (comment.score) < threshold:
                    print(fcomment(comment))
                    # comment.delete()

        elif mode == "Preview":
            n = delete_mode["display_limit"]
            choices = []
            for i, cid in enumerate(me):
                if i < n:
                    cid = str(cid)
                    comment = reddit.comment(id=cid)

                    if (comment.score) < threshold:
                        choices.append({"name": fcomment(comment), "value": comment})

            select_delete(choices)

    elif type == "Subreddits":
        print("Sub")


if __name__ == "__main__":
    main()

"""
Flow:
ask general or specific

general:
    ask nuke or show comments
    
    nuke:
        nuke
        
    show:
        show how many
"""
