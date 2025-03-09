import praw
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

# ---------------------------------------
# Step 1: Configure Reddit Bot Credentials
# ---------------------------------------
reddit = praw.Reddit(
    client_id='nLGUf0IYWSuluP3dg9DCMQ',       # New client_id
    client_secret='ewMEBh5hkBTrpOUpSKBx1E4xO-yBQ',  # New client_secret
    user_agent='GooglyGuru by /u/ApprehensiveDonut636',  # New user_agent
    username='GooglyGuru',                # New bot's username
    password='deleteaccount@123'          # New bot's password
)

# ---------------------------------------
# Step 2: Connect to Google Sheets (Optional)
# ---------------------------------------
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

# Use a raw string for the JSON credentials path
creds = ServiceAccountCredentials.from_json_keyfile_name(r"D:\Bot\rare-drummer-453211-v0-3ef559bf14c4.json", scope)
client = gspread.authorize(creds)

# Open your Google Sheet and specific worksheet where predictions are stored
sheet = client.open("IPL_2025_Prediction_League").worksheet("Prediction_Data")

# ---------------------------------------
# Step 3: Define the Megathread URL & Regex
# ---------------------------------------
MEGATHREAD_URL = "https://www.reddit.com/r/YourSubreddit/comments/xxxxx/your_megathread_title/"
prediction_pattern = re.compile(r"match\s*(\d+)\s*:\s*([A-Za-z]+)", re.IGNORECASE)

# ---------------------------------------
# (Optional) Match Lineups Dictionary
# ---------------------------------------
# Update this dictionary with the actual teams playing in each match.
match_lineups = {
    "1": ["Royal Challengers Bengaluru", "Rajasthan Royals"],
    "2": ["Mumbai Indians", "Lucknow Super Giants"],
    # Add additional matches as needed
}

# ---------------------------------------
# Step 4: Utility Functions
# ---------------------------------------
def normalize_username(username: str) -> str:
    """Convert a Reddit username to lowercase for consistency."""
    return username.strip().lower()

def already_processed(comment_id: str) -> bool:
    """Check if this comment's ID is already in the sheet to avoid duplication."""
    try:
        sheet.find(comment_id)
        return True
    except gspread.exceptions.CellNotFound:
        return False

def process_comment(comment):
    """
    Processes a Reddit comment:
    - Checks if it matches the prediction format.
    - Avoids duplicates.
    - Validates the predicted team (if match lineup data is available).
    - Logs the prediction in Google Sheets.
    - Replies with a confirmation (or error message).
    """
    if already_processed(comment.id):
        print(f"Already processed comment {comment.id}")
        return

    text = comment.body.strip()
    match_obj = prediction_pattern.search(text)
    
    if match_obj:
        match_id = match_obj.group(1)
        predicted_team = match_obj.group(2).upper()
        user = normalize_username(comment.author.name)
        timestamp = comment.created_utc

        # Validate team if lineup data exists for this match
        if match_id in match_lineups:
            if predicted_team not in match_lineups[match_id]:
                reply_text = (f"Your prediction '{predicted_team}' is not valid for Match {match_id}.\n\n"
                              f"Teams playing are: {', '.join(match_lineups[match_id])}. "
                              "Please update your prediction.")
                comment.reply(reply_text)
                print(f"Invalid team: {predicted_team} not in match {match_id} lineup")
                return
        else:
            print(f"No lineup data for match {match_id}. Proceeding without team check.")

        # Prepare row for Google Sheets; store comment ID to avoid duplicates
        row = [match_id, user, predicted_team, timestamp, time.ctime(timestamp), comment.id]
        sheet.append_row(row)
        
        confirmation_message = f"Your prediction for Match {match_id} ({predicted_team}) has been recorded!"
        comment.reply(confirmation_message)
        
        print(f"Recorded prediction: {user} predicted Match {match_id}: {predicted_team}")
    else:
        print("No valid prediction in comment:", text[:30])

# ---------------------------------------
# Step 5: Main Bot Function
# ---------------------------------------
def run_bot():
    """Loads the megathread, processes all comments, and logs predictions."""
    submission = reddit.submission(url=MEGATHREAD_URL)
    submission.comments.replace_more(limit=0)
    
    print("Processing comments from the megathread...")
    for comment in submission.comments.list():
        process_comment(comment)

# ---------------------------------------
# Step 6: Execute the Script
# ---------------------------------------
if __name__ == "__main__":
    run_bot()
