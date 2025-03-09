import praw
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

# ---------------------------------------
# Step 1: Configure Reddit Bot Credentials
# ---------------------------------------
reddit = praw.Reddit(
    client_id='nLGUf0IYWSuluP3dg9DCMQ',       # Your bot's client_id
    client_secret='ewMEBh5hkBTrpOUpSKBx1E4xO-yBQ',  # Your bot's client_secret
    user_agent='GooglyGuru by /u/ApprehensiveDonut636',  # A descriptive user agent
    username='GooglyGuru',                # Your bot's Reddit username
    password='deleteaccount@123'          # Your bot's Reddit password
)

# ---------------------------------------
# Step 2: Connect to Google Sheets (Optional)
# ---------------------------------------
scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

# Use a raw string for the path to your JSON credentials file
creds = ServiceAccountCredentials.from_json_keyfile_name(r"D:\Bot\rare-drummer-453211-v0-3ef559bf14c4.json", scope)
client = gspread.authorize(creds)

# Open your Google Sheet and the specific worksheet where you'll store predictions
sheet = client.open("IPL_2025_Prediction_League").worksheet("Prediction_Data")

# ---------------------------------------
# Step 3: Define the Megathread URL, Regex, and Match Lineups
# ---------------------------------------
MEGATHREAD_URL = "https://www.reddit.com/r/YourSubreddit/comments/xxxxx/your_megathread_title/"
prediction_pattern = re.compile(r"match\s*(\d+)\s*:\s*([A-Za-z]+)", re.IGNORECASE)

# Updated match lineups dictionary (70 matches)
match_lineups = {
  "1": ["Kolkata Knight Riders", "Royal Challengers Bengaluru"],
  "2": ["Sunrisers Hyderabad", "Rajasthan Royals"],
  "3": ["Chennai Super Kings", "Mumbai Indians"],
  "4": ["Delhi Capitals", "Lucknow Super Giants"],
  "5": ["Gujarat Titans", "Punjab Kings"],
  "6": ["Rajasthan Royals", "Kolkata Knight Riders"],
  "7": ["Sunrisers Hyderabad", "Lucknow Super Giants"],
  "8": ["Chennai Super Kings", "Royal Challengers Bengaluru"],
  "9": ["Gujarat Titans", "Mumbai Indians"],
  "10": ["Delhi Capitals", "Sunrisers Hyderabad"],
  "11": ["Rajasthan Royals", "Chennai Super Kings"],
  "12": ["Mumbai Indians", "Kolkata Knight Riders"],
  "13": ["Lucknow Super Giants", "Punjab Kings"],
  "14": ["Royal Challengers Bengaluru", "Gujarat Titans"],
  "15": ["Kolkata Knight Riders", "Sunrisers Hyderabad"],
  "16": ["Lucknow Super Giants", "Mumbai Indians"],
  "17": ["Chennai Super Kings", "Delhi Capitals"],
  "18": ["Punjab Kings", "Rajasthan Royals"],
  "19": ["Kolkata Knight Riders", "Lucknow Super Giants"],
  "20": ["Sunrisers Hyderabad", "Gujarat Titans"],
  "21": ["Mumbai Indians", "Royal Challengers Bengaluru"],
  "22": ["Punjab Kings", "Chennai Super Kings"],
  "23": ["Gujarat Titans", "Rajasthan Royals"],
  "24": ["Royal Challengers Bengaluru", "Delhi Capitals"],
  "25": ["Chennai Super Kings", "Kolkata Knight Riders"],
  "26": ["Lucknow Super Giants", "Gujarat Titans"],
  "27": ["Sunrisers Hyderabad", "Punjab Kings"],
  "28": ["Rajasthan Royals", "Royal Challengers Bengaluru"],
  "29": ["Delhi Capitals", "Mumbai Indians"],
  "30": ["Lucknow Super Giants", "Chennai Super Kings"],
  "31": ["Punjab Kings", "Kolkata Knight Riders"],
  "32": ["Delhi Capitals", "Rajasthan Royals"],
  "33": ["Mumbai Indians", "Sunrisers Hyderabad"],
  "34": ["Royal Challengers Bengaluru", "Punjab Kings"],
  "35": ["Gujarat Titans", "Delhi Capitals"],
  "36": ["Rajasthan Royals", "Lucknow Super Giants"],
  "37": ["Punjab Kings", "Royal Challengers Bengaluru"],
  "38": ["Mumbai Indians", "Chennai Super Kings"],
  "39": ["Kolkata Knight Riders", "Gujarat Titans"],
  "40": ["Lucknow Super Giants", "Delhi Capitals"],
  "41": ["Sunrisers Hyderabad", "Mumbai Indians"],
  "42": ["Royal Challengers Bengaluru", "Rajasthan Royals"],
  "43": ["Chennai Super Kings", "Sunrisers Hyderabad"],
  "44": ["Kolkata Knight Riders", "Punjab Kings"],
  "45": ["Mumbai Indians", "Lucknow Super Giants"],
  "46": ["Delhi Capitals", "Royal Challengers Bengaluru"],
  "47": ["Rajasthan Royals", "Gujarat Titans"],
  "48": ["Delhi Capitals", "Kolkata Knight Riders"],
  "49": ["Chennai Super Kings", "Punjab Kings"],
  "50": ["Rajasthan Royals", "Mumbai Indians"],
  "51": ["Gujarat Titans", "Sunrisers Hyderabad"],
  "52": ["Royal Challengers Bengaluru", "Chennai Super Kings"],
  "53": ["Kolkata Knight Riders", "Rajasthan Royals"],
  "54": ["Punjab Kings", "Lucknow Super Giants"],
  "55": ["Sunrisers Hyderabad", "Delhi Capitals"],
  "56": ["Mumbai Indians", "Gujarat Titans"],
  "57": ["Kolkata Knight Riders", "Chennai Super Kings"],
  "58": ["Punjab Kings", "Delhi Capitals"],
  "59": ["Lucknow Super Giants", "Royal Challengers Bengaluru"],
  "60": ["Sunrisers Hyderabad", "Kolkata Knight Riders"],
  "61": ["Punjab Kings", "Mumbai Indians"],
  "62": ["Delhi Capitals", "Gujarat Titans"],
  "63": ["Chennai Super Kings", "Rajasthan Royals"],
  "64": ["Royal Challengers Bengaluru", "Sunrisers Hyderabad"],
  "65": ["Gujarat Titans", "Lucknow Super Giants"],
  "66": ["Mumbai Indians", "Delhi Capitals"],
  "67": ["Rajasthan Royals", "Punjab Kings"],
  "68": ["Royal Challengers Bengaluru", "Kolkata Knight Riders"],
  "69": ["Gujarat Titans", "Chennai Super Kings"],
  "70": ["Lucknow Super Giants", "Sunrisers Hyderabad"]
}

# ---------------------------------------
# Step 4: Utility Functions
# ---------------------------------------
def normalize_username(username: str) -> str:
    """Convert a Reddit username to lowercase for consistency."""
    return username.strip().lower()

def already_processed(comment_id: str) -> bool:
    """Check if this comment's ID is already in the sheet to avoid duplicates."""
    try:
        sheet.find(comment_id)
        return True
    except gspread.exceptions.CellNotFound:
        return False

# Mapping abbreviations to full team names (all in uppercase for consistency)
team_abbreviations = {
    "MI": "MUMBAI INDIANS",
    "RCB": "ROYAL CHALLENGERS BENGALURU",
    "CSK": "CHENNAI SUPER KINGS",
    "KKR": "KOLKATA KNIGHT RIDERS",
    "SRH": "SUNRISERS HYDERABAD",
    "RR": "RAJASTHAN ROYALS",
    "LSG": "LUCKNOW SUPER GIANTS",
    "PK": "PUNJAB KINGS",
    "GT": "GUJARAT TITANS",
    "DC": "DELHI CAPITALS"
}

def process_comment(comment):
    """
    Processes a Reddit comment:
    - Checks if it matches the prediction format.
    - Avoids duplicates.
    - Replaces abbreviations with full team names.
    - Validates the predicted team against the match lineup.
    - Logs the prediction to Google Sheets.
    - Replies with a confirmation message including the full team name.
    """
    if already_processed(comment.id):
        print(f"Already processed comment {comment.id}")
        return

    text = comment.body.strip()
    match_obj = prediction_pattern.search(text)
    
    if match_obj:
        match_id = match_obj.group(1)
        predicted_team = match_obj.group(2).upper()  # e.g., "MI"

        # Replace abbreviation with full team name if available
        if predicted_team in team_abbreviations:
            full_team_name = team_abbreviations[predicted_team]
        else:
            full_team_name = predicted_team

        user = normalize_username(comment.author.name)
        timestamp = comment.created_utc

        # Validate predicted team against match_lineups if available
        if match_id in match_lineups:
            if full_team_name not in [team.upper() for team in match_lineups[match_id]]:
                reply_text = (f"Your prediction '{full_team_name}' is not valid for Match {match_id}.\n\n"
                              f"Teams playing are: {', '.join(match_lineups[match_id])}. Please update your prediction.")
                comment.reply(reply_text)
                print(f"Invalid team: {full_team_name} not in match {match_id} lineup")
                return
        else:
            print(f"No lineup data for match {match_id}. Proceeding without team validation.")

        # Prepare the row for Google Sheets, including the comment ID to avoid duplicates
        row = [match_id, user, full_team_name, timestamp, time.ctime(timestamp), comment.id]
        sheet.append_row(row)
        
        confirmation_message = f"Your prediction for Match {match_id} ({full_team_name}) has been recorded!"
        comment.reply(confirmation_message)
        
        print(f"Recorded prediction: {user} predicted Match {match_id}: {full_team_name}")
    else:
        print("No valid prediction in comment:", text[:30])

# ---------------------------------------
# Step 5: Main Bot Function
# ---------------------------------------
def run_bot():
    """
    Loads the megathread by URL, processes all comments, and logs predictions.
    """
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
