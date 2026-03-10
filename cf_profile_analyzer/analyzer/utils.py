import requests
import datetime
import random


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
    rating_history_labels = []
    
    for contest in contests:
        ratings.append(contest['newRating'])
        standings.append(contest['rank'])
        
        # Convert timestamp to readable date string for the chart
        if 'ratingUpdateTimeSeconds' in contest:
            timestamp = contest['ratingUpdateTimeSeconds']
            dt_object = datetime.datetime.fromtimestamp(timestamp)
            date_str = dt_object.strftime("%b %Y") # e.g., "Jan 2023"
            rating_history_labels.append(date_str)
        else:
            rating_history_labels.append("")

    data = {'ratings': ratings, 'rating_history_labels': rating_history_labels}
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
        
        # New tracking variables for abandoned problems
        solved_problem_ids = set() # Track IDs of problems solved
        attempted_problem_tags = {} # problem_id -> list of tags
        
        solved_problems = set()
        problem_ratings = {}
        
        # Radar Chart Core Categories
        core_categories = ['math', 'greedy', 'dp', 'data structures', 'graphs', 'strings']
        radar_data_dict = {cat: 0 for cat in core_categories}

        for submission in submissions:
            prob_id = f"{submission['problem'].get('contestId', '')}_{submission['problem'].get('name', '')}"
            if 'tags' in submission['problem']:
                attempted_problem_tags[prob_id] = submission['problem']['tags']
                
            if submission['verdict'] == 'OK':
                solved_problem_ids.add(prob_id)
                successfulSubmission += 1
                tags = submission['problem'].get('tags', [])
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
                    
                # Track difficulty distribution for unique solved problems
                if prob_id not in solved_problems:
                    solved_problems.add(prob_id)
                    rating = submission['problem'].get('rating')
                    if rating:
                        if rating in problem_ratings:
                            problem_ratings[rating] += 1
                        else:
                            problem_ratings[rating] = 1
                            
                    # Track Radar chart core categories
                    for tag in tags:
                        if tag in core_categories:
                            radar_data_dict[tag] += 1
            else:
                failedSubmission += 1
                index = submission['problem']['index']
                if index in failedProblemIndex:
                    failedProblemIndex[index] += 1
                else:
                    failedProblemIndex[index] = 1
                    
        # Calculate abandoned problems by tag
        abandoned_tags_counts = {}
        for prob_id, tags in attempted_problem_tags.items():
            if prob_id not in solved_problem_ids:
                # This problem was attempted but never OK'd
                for tag in tags:
                    if tag in abandoned_tags_counts:
                        abandoned_tags_counts[tag] += 1
                    else:
                        abandoned_tags_counts[tag] = 1
        
        # Sort and get top 10 abandoned tags
        sorted_abandoned = sorted(abandoned_tags_counts.items(), key=lambda item: item[1], reverse=True)[:10]
        abandoned_labels = [item[0] for item in sorted_abandoned]
        abandoned_data = [item[1] for item in sorted_abandoned]

        topTags = get_top_five(favProgTag)
        topSuccessIndex = get_top_five(successProblemIndex)
        topFailedIndex = get_top_five(failedProblemIndex)

        if len(submissions)>0:
            successRatio = round((successfulSubmission/len(submissions))*100,2)
            failedRatio = round((failedSubmission / len(submissions)) * 100,2)
        else:
            successRatio = "--"
            failedRatio = "--"
            
        # Parse rating distribution data
        rating_labels = sorted(problem_ratings.keys())
        rating_data = [problem_ratings[r] for r in rating_labels]
        
        # Parse radar data
        radar_labels = [cat.title() for cat in core_categories]
        radar_data = [radar_data_dict[cat] for cat in core_categories]
        
        data = {'totalSub': len(submissions), 'successSub': successfulSubmission, 'failedSub': failedSubmission,
                'topTags': topTags, 'topSuccessIndex': topSuccessIndex, 'topFailedIndex': topFailedIndex,
                'successRatio': successRatio, 'failedRatio': failedRatio,
                'rating_labels': rating_labels, 'rating_data': rating_data,
                'abandoned_labels': abandoned_labels, 'abandoned_data': abandoned_data,
                'radar_labels': radar_labels, 'radar_data': radar_data,
                'solved_problem_ids': list(solved_problem_ids)}
    except KeyError:
        pass

    return data


def get_recommendations(user_rating, abandoned_labels, solved_problem_ids):
    # Set target rating
    if not isinstance(user_rating, int) or user_rating < 800:
        target_rating = 800
    else:
        # Suggest problems slightly harder than their current rating (round down to nearest 100, then add 100)
        target_rating = (user_rating // 100) * 100 + 100

    link = "https://codeforces.com/api/problemset.problems"
    
    try:
        response = requests.get(link).json()
        if response['status'] != 'OK':
            return []
            
        all_problems = response['result']['problems']
        recommended = []
        
        # Consider top 3 abandoned tags for recommendations
        target_tags = set(abandoned_labels[:3]) if abandoned_labels else set()
        
        for p in all_problems:
            prob_id = f"{p.get('contestId', '')}_{p.get('name', '')}"
            
            # Skip if already solved
            if prob_id in solved_problem_ids:
                continue
                
            p_rating = p.get('rating')
            # Check rating constraints: between target_rating and target_rating + 200
            if p_rating and target_rating <= p_rating <= target_rating + 200:
                p_tags = set(p.get('tags', []))
                
                # Check tag constraints (must have at least one weak tag, or if no weak tags exist, just recommend based on rating)
                if not target_tags or p_tags.intersection(target_tags):
                    p['link'] = f"https://codeforces.com/problemset/problem/{p.get('contestId', '')}/{p.get('index', '')}"
                    recommended.append(p)
                    
        # Randomly select up to 5 problems
        if len(recommended) > 5:
            return random.sample(recommended, 5)
        return recommended

    except Exception:
        return []
