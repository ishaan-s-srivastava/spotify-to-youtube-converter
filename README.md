Author: Ishaan Srivastava

Spotify -> YouTube Playlist Converter
=====================================

I built this application because I personally needed it. I listen to a lot 
of music and wanted a straightforward way to move my Spotify playlists over 
to YouTube without having to manually search for hundreds of songs one by one.

What started out as a simple script quickly grew into a project I had a lot 
of fun refining. As I kept using it on my own playlists, I ran into real 
roadblocks, like YouTube's strict daily API search limits, messy search 
results, and lost connections mid-transfer. I kept building out features 
to solve those exact problems, turning it into a pretty reliable tool.


WHAT IT DOES
------------
- Takes a Spotify playlist and builds an equivalent playlist on YouTube.
- Uses a custom scoring system to pick the right YouTube video for each track.
- Saves song matches in a local SQLite database to avoid repeating searches.
- Resume-friendly: if a transfer gets cut off, it picks up right where it left off.
- Handles transfers between different Spotify and YouTube accounts without hassle.


THE CHALLENGE: PICKING THE RIGHT TRACK
---------------------------------------
When you search for a song on YouTube, the top result isn't always the actual 
song. It's often a fan-made lyric video, a live recording, a cover, or a sped-up 
edit. 

To make sure the converter grabs the actual official track, I built a scoring 
system that looks at candidate search results and ranks them:
- It rewards exact artist/title matches, official audio/video labels
- It factors in view counts logarithmically, giving a boost to popular uploads 
  without letting random high-view videos override an exact title match.
- It penalizes keywords like "live", "remix", "cover", "acoustic", "karaoke", 
  "slowed", "sped up", "nightcore", or "shorts".

Tuning this algorithm was one of the most interesting parts of the project, 
as I kept tweaking the weights whenever I found an edge-case track it missed.

Note: I have intentionally left commented out print statements in song_ranking.py
which are very useful for debugging and seeing why the algorithm chose each
candidate.


SAVING API QUOTA (SQL CACHING)
------------------------------
YouTube limits free developer accounts to a pretty tight daily search quota. 
Searching for every single track on every run exhausted that limit instantly.

To fix this, I added a local SQLite database to store Spotify track -> YouTube ID 
mappings:
- Once a track is matched, it's saved locally.
- Future conversions (or other playlists with the same track) read straight 
  from the database instead of making a new YouTube search request.
- This cut down API calls dramatically and made subsequent runs super fast.


FAULT TOLERANCE & RESUMING CONVERSIONS
--------------------------------------
Large playlists take time, and nothing is more frustrating than having a script 
crash 90% of the way through and having to start over from track 1.

I designed the script to add songs to the YouTube playlist incrementally as it 
processes them. If the program stops due to a dropped connection or rate limit, 
you can just run it again. It detects the existing playlist, sees what's already 
there, and resumes from where it left off without creating duplicates or wasting quota.


REQUIREMENTS
------------
- Python 3.8+
- Spotify API Credentials (Client ID & Client Secret)
- Google / YouTube Data API v3 Credentials
- SQLite3


SETUP & RUNNING
---------------
1. Clone the repository:
   git clone https://github.com/your-username/spotify-youtube-converter.git
   cd spotify-youtube-converter

2. Set up a virtual environment:
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install requirements:
   pip install -r requirements.txt

4. Add your API credentials to a .env file (see .env.example).

5. Run the script:
   python main.py


YOUTUBE API ACCESS NOTE
-----------------------
Since this is my personal developer project, the YouTube OAuth app is currently 
in Google's testing mode. Only approved test accounts can log in directly. If you 
want to run this yourself, you'll just need to create your own client_secret.json 
in the Google Cloud Console.


THINGS TO IMPROVE / FUTURE IDEAS
--------------------------------
This project grew organically out of my own use, so there are still a few things 
I'd love to add over time:
- Build a lightweight Web UI (maybe with Flask or FastAPI) instead of running terminal commands.
- Add bi-directional syncing so I can go YouTube -> Spotify as well.
- Better handling if an existing YouTube playlist gets manually renamed.