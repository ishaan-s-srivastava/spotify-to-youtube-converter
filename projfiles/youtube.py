import time
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import song_ranking


class YouTube:

    def __init__(self):
        self.youtube = None

    def login(self):
        scopes = [
            "https://www.googleapis.com/auth/youtube"
        ]

        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json",
            scopes
        )

        credentials = flow.run_local_server(port=0)

        self.youtube = build(
            "youtube",
            "v3",
            credentials=credentials
        )

        print("YouTube authorization successful!")
        
    def search_video(self, query):
        request = self.youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=4
        )

        response = request.execute()
        # for debugging
        # print("search initiated")
        vid_found = False
        vid_candidates = []
        viewcounts = []
        artist_name,song_name = query.split(" - ")
        for item in response["items"]:
            # print("SEARCH RESULT:", item["id"])
            if item["id"]["kind"] == "youtube#video" and not any(
                word in item["snippet"]["title"].lower() for word in ("cover", "performance")
            ):
                vid_candidates.append(item)
                currViews = self.youtube.videos().list(
                    part="statistics",
                    id=item["id"]["videoId"]
                ).execute()
                view_count = int(currViews["items"][0]["statistics"]["viewCount"])
                viewcounts.append(view_count)
                vid_found = True
        
        if vid_found:
            return song_ranking.find_best_match(vid_candidates, viewcounts, artist_name, song_name)
        return None

    def get_playlists(self):
        request = self.youtube.playlists().list(
        part="snippet,contentDetails",
        mine="true",
        maxResults="50"
        )
        response = request.execute()
        return response["items"]


    def make_playlist(self, plst_name):
        request = self.youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": plst_name,
                "description": ""
            },
            "status": {
                "privacyStatus": "private"
            }
        } 
        )
        response = request.execute()
        return response

    def add_video(self, playlist_id, video_id):
        request = self.youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        )
        for attempt in range(5):
            try:
                response = request.execute()
                return response

            except HttpError as e:
                print(f"YouTube error (attempt {attempt + 1}/5): {e}")

                if e.resp.status == 409:
                    wait_time = 2 ** attempt
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise

        raise Exception("Failed to add video after 5 attempts")