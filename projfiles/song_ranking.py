import math
def find_best_match(vids, viewcounts, artist_name, song_name):
    artist_name = artist_name.lower()
    song_name = song_name.lower()
    scores = []
    counter = 0
    relevance = 0.5
    for vid in vids:
        currScore = 27
        title = vid["snippet"]["title"]
        title = title.lower()
        currScore += math.log10(viewcounts[counter] + 1) * 4
        if "mv" in title or "music video" in title or "m/v" in title:
            currScore += 15
        if (
            "feat. " in title
            or "ft. " in title
            or "feat " in title
            or "with " in title
        ) and not (
            "feat. " in song_name
            or "ft. " in song_name
            or "feat " in song_name
            or "with " in song_name
        ):
            currScore -= 3
        if artist_name in title and song_name in title:
            currScore += 4
        elif song_name in title:
            currScore += 25
        elif artist_name in title and not song_name in title:
            currScore -= 4
        if (
            "feat. " + artist_name in title
            or "ft. " + artist_name in title
            or "feat " + artist_name in title
            or "with " + artist_name in title
        ):
            currScore -= 40
        if "lyric video" in title:
            currScore += 4
        elif "lyric" in title:
            currScore += 1
        if "unofficial" in title:
            currScore -= 10
        elif "official audio" in title:
            currScore += 1
        elif "official video" in title:
            currScore += 4
        elif "official" in title:
            currScore += 2
        if "slowed + reverb" in title:
            currScore -= 10
        elif "slowed" in title and not "slowed" in song_name:
            currScore -= 7
        if "(sped" in title or "sped." in title or "sped " in title:
            currScore -= 7
        if "nightcore" in title:
            currScore -= 5
        if "remix" in title and not "remix" in song_name:
            currScore -= 3
        if "acoustic" in title and not "acoustic" in song_name:
            currScore -= 10
        if "live version" in title:
            currScore -= 10
        if "karaoke" in title and not "karaoke" in song_name:
            currScore -= 10
        if "(live" in title or "[live" in title:
            currScore -= 15
        elif " live" in title and not " live" in song_name:
            currScore -= 15
        elif "live" in title and not "live" in song_name:
            currScore -= 15
        if ("version" in title or "ver." in title) and not ("version" in song_name or "ver." in song_name):
            currScore -= 7
        if " by " in title:
            currScore -= 5
        if "demo" in title and not "demo" in song_name:
            currScore -= 5
        if "instrumental" in title and not "instrumental" in song_name:
            currScore -= 10
        if "#short" in title:
            currScore -= 20
        elif "#" in title:
            currScore -= 9
        currScore += relevance
        # print("song #" + str(counter+1) + " (" + title + ")" + ", final score: " + str(currScore))
        scores.append(currScore)
        relevance -= 0.1
        counter += 1
    highest_index = scores.index(max(scores))
    # for debugging:
    # print("Winner: " + vids[highest_index]["snippet"]["title"])
    # print("----------------------------")
    return vids[highest_index]["id"]["videoId"]