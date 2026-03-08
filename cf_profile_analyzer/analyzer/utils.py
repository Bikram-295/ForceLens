import requests


def choose_color(rating):
    if rating < 1200:
        color = "#808080"
    elif 1200 <= rating <= 1400:
        color = "#008000"
    elif 1400 <= rating <= 1600:
        color = "#03a89e"
    elif 1600 <= rating <= 1900:
        color = "#0000ff"
    elif 1900 <= rating <= 2100:
        color = "#aa00aa"
    elif 2100 <= rating <= 2300:
        color = "#ff8c00"
    elif 2300 <= rating <= 2400:
        color = "#ff8c00"
    elif 2400 <= rating <= 2600:
        color = "#ff0000"
    elif 2600 <= rating <= 3000:
        color = "#ff0000"
    else:
        color = "#ff0000"

    return color


def get_user_info(handle):
    link = f"https://codeforces.com/api/user.info?handles={handle}"

    try:
        user_info = requests.get(link).json()['result'][0]
    except KeyError:
        data = {"message": f"{handle} does not exist."}
        return data

    data = {}
    fields = ['rating', 'rank', 'maxRating', 'friendOfCount', 'titlePhoto', 'handle']
    for field in fields:
        if field in user_info:
            data[field] = user_info[field]
        else:
            data[field] = "--"

    if isinstance(data['rating'], int):
        data['curColor'] = choose_color(data['rating'])
    else:
        data['curColor'] = "#808080"

    if isinstance(data['maxRating'], int):
        data['maxColor'] = choose_color(data['maxRating'])
    else:
        data['maxColor'] = "#808080"

    return data


def get_contest_info(handle):
    link = f"https://codeforces.com/api/user.rating?handle={handle}"

    contests = requests.get(link).json()['result']

    ratings = []
    standings = []
    for contest in contests:
        ratings.append(contest['newRating'])
        standings.append(contest['rank'])

    data = {'ratings': ratings}
    if len(ratings)>0:
        data['minRating'] = min(ratings)
    else:
        data['minRating'] = "--"

    if len(standings)>0:
        data['minStanding'] = max(standings)
        data['maxStanding'] = min(standings)
    else:
        data['minStanding'] = "--"
        data['maxStanding'] = "--"

    if isinstance(data['minRating'], int):
        data['minColor'] = choose_color(data['minRating'])
    else:
        data['minColor'] = "#808080"

    return data


def get_top_five(dictionary):
    tags = []
    for key, value in dictionary.items():
        tags.append((value, key))

    tags.sort(reverse=True)
    tags = tags[:5]
    top_five = {}
    for key, value in tags:
        top_five[value] = key

    return top_five


def get_submission_info(handle):
    link = f"https://codeforces.com/api/user.status?handle={handle}"

    data = ""
    try:
        submissions = requests.get(link).json()['result']

        successfulSubmission = 0
        failedSubmission = 0
        favProgTag = {}
        successProblemIndex = {}
        failedProblemIndex = {}

        for submission in submissions:
            if submission['verdict'] == 'OK':
                successfulSubmission += 1
                tags = submission['problem']['tags']
                for tag in tags:
                    if tag not in favProgTag:
                        favProgTag[tag] = 1
                    else:
                        favProgTag[tag] += 1

                index = submission['problem']['index']
                if index in successProblemIndex:
                    successProblemIndex[index] += 1
                else:
                    successProblemIndex[index] = 1
            else:
                failedSubmission += 1
                index = submission['problem']['index']
                if index in failedProblemIndex:
                    failedProblemIndex[index] += 1
                else:
                    failedProblemIndex[index] = 1

        topTags = get_top_five(favProgTag)
        topSuccessIndex = get_top_five(successProblemIndex)
        topFailedIndex = get_top_five(failedProblemIndex)

        if len(submissions)>0:
            successRatio = round((successfulSubmission/len(submissions))*100,2)
            failedRatio = round((failedSubmission / len(submissions)) * 100,2)
        else:
            successRatio = "--"
            failedRatio = "--"
        data = {'totalSub': len(submissions), 'successSub': successfulSubmission, 'failedSub': failedSubmission,
                'topTags': topTags, 'topSuccessIndex': topSuccessIndex, 'topFailedIndex': topFailedIndex,
                'successRatio': successRatio, 'failedRatio': failedRatio}
    except KeyError:
        pass

    return data
