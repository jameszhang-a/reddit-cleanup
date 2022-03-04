import praw
from prawcore import ResponseException, OAuthException
from PyInquirer import prompt, print_json, Separator, style_from_dict
from validator import NumberValidator


# for i, cid in enumerate(me):
#     cid = str(cid)
#     comment = reddit.comment(id=cid)

#     if (score := comment.score) < 1:
#         print(score, ":", comment.body)

# print(me)


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
    question = (
        {
            "type": "input",
            "name": "karma",
            "message": "Comments below how many upvotes would you like to delete",
            "validate": NumberValidator,
            "filter": lambda val: int(val),
        },
    )
    karma = prompt(question)
    return karma["karma"]


def main():
    # try:
    #     reddit = praw.Reddit("bot1")
    #     me = reddit.user.me().comments.new(limit=None)
    # except ResponseException:
    #     print("Your reddit app ID/secret is likely wrong")
    #     print("exiting...")
    #     return
    # except OAuthException:
    #     print("Your reddit username and password is likely wrong")
    #     print("exiting...")
    #     return

    # print(sum(1 for _ in me))
    # for i, cid in enumerate(me):
    #     cid = str(cid)
    #     comment = reddit.comment(id=cid)

    #     print()

    type = ask_type()
    if type == "General":
        print("general")
        karma = ask_karma()
        print(karma)
    elif type == "Subreddits":
        print("Sub")


if __name__ == "__main__":
    main()
