from email.policy import default
import praw
from prawcore import ResponseException, OAuthException
from PyInquirer import prompt, Separator
from validator import NumberValidator, MinimumChoice
from datetime import datetime

LIMIT = 500


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
        "message": "Comments below how many upvotes would you like to delete: ",
        "validate": NumberValidator,
        "filter": lambda val: int(val),
    }

    karma = prompt(question)
    return karma["karma"]


def ask_delete(total_comments):
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
            "message": f"How many would you like to preview? (limit: {total_comments})",
            "validate": NumberValidator,
            "filter": lambda val: int(val),
            "when": lambda answers: answers["mode"] == "Preview"
            and total_comments < 1000,
        },
        {
            "type": "input",
            "name": "display_limit",
            "message": "How many would you like to preview? (limit: 1000)",
            "validate": NumberValidator,
            "filter": lambda val: int(val),
            "when": lambda answers: answers["mode"] == "Preview"
            and total_comments >= 1000,
        },
    ]

    answers = prompt(q)
    return answers


def cbody(comment):
    return f"{comment.body}\n"


def cinfo(comment):
    upvotes, time, sub = (
        comment.score,
        datetime.fromtimestamp(comment.created_utc),
        comment.subreddit,
    )

    return f"upvotes: {upvotes}    created: {time}    subreddit: {sub}"


def delete_comments(comments):
    n = len(comments)

    q = {
        "type": "confirm",
        "name": "delete",
        "message": f"{n} comments found, delete?",
        "default": False,
    }
    delete = prompt(q)["delete"]

    if delete:
        for comment in comments:
            comment.delete()


def select_delete(choices):
    q = {
        "type": "checkbox",
        "qmark": "😃",
        "message": "select comments",
        "name": "comments",
        "choices": choices,
        "validate": MinimumChoice,
    }

    return prompt(q)["comments"]


def rerun():
    q = {
        "type": "confirm",
        "name": "restart",
        "message": "There are no comments that match. Restart?",
    }
    return prompt(q)["restart"]


def main():
    while True:
        try:
            reddit = praw.Reddit("bot1")
            me = reddit.user.me().comments.new(limit=LIMIT)
            total_comments = sum(1 for _ in reddit.user.me().comments.new(limit=LIMIT))
        except ResponseException:
            print("Your reddit app ID/secret is likely wrong")
            print("exiting...")
            return
        except OAuthException:
            print("Your reddit username and password is likely wrong")
            print("exiting...")
            return

        # whether all of reddit or for specific subs
        type = ask_type()
        if type == "General":
            threshold = ask_karma()
            delete_mode = ask_delete(total_comments)

            if delete_mode["mode"] == "NUKE":
                comments_to_delete = []
                for cid in me:
                    # Finds the reddit comment object associated with comments you posted
                    comment = reddit.comment(id=str(cid))

                    # only comments below a certain up vote threshold is selected
                    if (comment.score) < threshold:
                        comments_to_delete.append(comment)

                delete_comments(comments_to_delete)
                break

            elif delete_mode["mode"] == "Preview":
                n = delete_mode["display_limit"]
                choices = []
                for cid in me:
                    # Only searches through the selected limit
                    if len(choices) / 2 < n:
                        # Finds the reddit comment object associated with comments you posted
                        comment = reddit.comment(id=str(cid))

                        # only comments below a certain up vote threshold is selected
                        if (comment.score) < threshold:
                            choices.append(Separator(cinfo(comment)))
                            choices.append({"name": cbody(comment), "value": comment})

                # if no comments match the query, restart script or exit
                if len(choices) < 1:
                    if rerun():
                        continue
                    else:
                        break

                comments_to_delete = select_delete(choices)
                delete_comments(comments_to_delete)
                break

        elif type == "Subreddits":
            print("Sub")


if __name__ == "__main__":
    main()
