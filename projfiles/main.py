import sqlite3

connection = sqlite3.connect("song_library.db")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS songids (
        id INTEGER PRIMARY KEY,
        spotify_trackinfo TEXT UNIQUE,
        yt_id TEXT
    )
""")

connection.commit()

# use this code to delete a song from the database
# cursor.execute("DELETE FROM songids WHERE spotify_trackinfo = ?", ("Regina Song - high school boy",))
# connection.commit()

def song_exists(cursor, tInfo):
    cursor.execute(
        "SELECT 1 FROM songids WHERE spotify_trackinfo = ? LIMIT 1",
        (tInfo,)
    )
    return cursor.fetchone() is not None

def add_entry(cursor, tInfo, ytid):
    cursor.execute(
        "INSERT INTO songids (spotify_trackinfo, yt_id) VALUES (?, ?)",
        (tInfo, ytid)
    )
    connection.commit()
    return

def get_ytid(cursor, tInfo):
    cursor.execute(
        "SELECT yt_id FROM songids WHERE spotify_trackinfo = ?",
        (tInfo,)
    )
    result = cursor.fetchone()
    if result is None:
        return None
    return result[0]

print("Welcome to Spotify to YouTube Converter")
print("loading...")

from spotify import Spotify

spotify = Spotify()

spotify.login()

playlists = spotify.get_playlists()

playlist_name = ""
item_num = 1
for playlist in playlists["items"]:
    print(str(item_num), "-", playlist["name"])
    item_num += 1

all_set = False
pl_num = ""
selected_playlist = []
while all_set != True:
    print("Type in the number of the playlist you want to convert: ")
    pl_num = input()
    while int(pl_num) < 1 or int(pl_num) > len(playlists["items"]):
        print("Error: Please enter a valid number")
        print("Type in the number of the playlist you want to convert: ")
        pl_num = input()
    pl_idx = int(pl_num) - 1
    selected_playlist = playlists["items"][pl_idx]
    print("Are you sure you want to convert", selected_playlist["name"], "? (y/n)")
    confirmation = input()
    if confirmation == "y":
        all_set = True



plst_obj = spotify.access_playlist(selected_playlist)
playlist_name = selected_playlist["name"]
# for debugging
# print("track list:")
tracklist = plst_obj["items"]
tracksinfo = []
track_info = ""
for item in tracklist:
    track = item["item"]
    # for debugging
    # print(track["artists"][0]["name"] + " - " + track["name"])
    track_info = str(track["artists"][0]["name"] + " - " + track["name"])
    tracksinfo.append(track_info)

from youtube import YouTube

youtube = YouTube()

youtube.login()



myplaylists = youtube.get_playlists()
def find_existing():
    for playlist in myplaylists:
        if playlist["snippet"]["title"] == playlist_name and playlist["contentDetails"]["itemCount"] > 0:
            remaining_tracks = find_starting_point(playlist, tracksinfo)
            # for debugging
            # print("found existing match! " + playlist["id"])
            print("found existing playlist! " + playlist["id"])
            return playlist["id"], remaining_tracks
    yt_playlist = youtube.make_playlist(playlist_name)
    plst_id = yt_playlist["id"]
    # print("youtube playlist id: " + plst_id)
    return plst_id, tracksinfo

def find_starting_point(plst, tracksinfo):
    offset = plst["contentDetails"]["itemCount"]
    print("we'll be starting at song #" + str(offset+1) + "/" + str(len(tracksinfo)))
    return tracksinfo[offset:]


playlist_id, tracksinfo = find_existing()


     
for song in tracksinfo:
    video_id = ""
    if song_exists(cursor, song):
        video_id = get_ytid(cursor, song)
    else:
        video_id = youtube.search_video(song)
        add_entry(cursor, song, video_id)

    # For debugging:
    print("Attempting to convert song: ", song)
    # print("Video ID:", repr(video_id))
    # print("Playlist ID:", repr(playlist_id))

    if video_id is None:
        print("No video found, skipping")
        continue

    youtube.add_video(playlist_id, video_id)
    print("Conversion successful!")
    print("------------------------------")

print("Playlist Conversion is Complete!")

connection.close()