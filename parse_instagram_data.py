import os
import zipfile
import re
from bs4 import BeautifulSoup
import webbrowser

def find_instagram_zip(directory="."):
    """
    Find the Instagram zip file in the specified directory.
    The zip file name should match 'instagram-hookedonoxy-YYYY-MM-DD-randomChars.zip'
    """
    pattern = re.compile(r'instagram-hookedonoxy-\d{4}-\d{2}-\d{2}-[a-zA-Z0-9]+\.zip')
    for file in os.listdir(directory):
        if pattern.fullmatch(file):
            return os.path.join(directory, file)
    return None

def extract_and_analyze_followers(zip_path):
    """
    Extract the zip file and analyze the follower/following data.
    """
    # Extract the zip file
    extract_dir = "instagram_data_extracted"
    os.makedirs(extract_dir, exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    except zipfile.BadZipFile:
        print("Error: The file is not a valid zip file or is corrupted.")
        return
    
    # Paths to the HTML files
    base_path = os.path.join(extract_dir, "connections", "followers_and_following")
    following_path = os.path.join(base_path, "following.html")
    followers_path = os.path.join(base_path, "followers_1.html")
    
    # Check if files exist
    if not os.path.exists(following_path):
        print(f"Error: File not found - {following_path}")
        print("Please check if the Instagram data export format has changed.")
        return
    if not os.path.exists(followers_path):
        print(f"Error: File not found - {followers_path}")
        print("Please check if the Instagram data export format has changed.")
        return
    
    # Open the files in browser
    print(f"\nOpening following data: {following_path}")
    webbrowser.open(following_path)
    
    print(f"Opening followers data: {followers_path}")
    webbrowser.open(followers_path)
    
    # Parse the HTML files
    print("\nParsing data...")
    following_data = parse_html_file(following_path)
    followers_data = parse_html_file(followers_path)
    
    # Compare followers vs following
    compare_followers(followers_data, following_data)

def parse_html_file(file_path):
    """
    Parse the Instagram HTML file and extract clean usernames.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                soup = BeautifulSoup(file, 'html.parser')
        except Exception as e:
            print(f"Failed to read file: {e}")
            return []

    users = []
    
    # Find all user entries
    for user_div in soup.find_all('div', class_='_a6-p'):
        # Find the username link (most reliable)
        user_link = user_div.find('a', href=lambda x: x and '/www.instagram.com/' in x)
        if user_link:
            username = user_link.text.strip()
            if username:
                users.append(username)
                continue
        
        # If no link found, parse the text carefully
        full_text = user_div.get_text('\n', strip=True)
        if full_text:
            # Split by newlines and take the first non-empty line
            lines = [line.strip() for line in full_text.split('\n') if line.strip()]
            if lines:
                username = lines[0]
                # Remove any trailing numbers/dates that might have been merged
                username = username.split(' ')[0]
                users.append(username)
    
    return users

def compare_followers(followers, following):
    """
    Compare followers and following lists to find differences.
    """
    if not followers or not following:
        print("Error: Could not extract follower data from the HTML files.")
        print("Instagram may have changed their data export format.")
        return
    
    followers_set = set(followers)
    following_set = set(following)
    
    # People you follow who don't follow you back
    not_following_back = following_set - followers_set
    
    # People who follow you but you don't follow back
    you_dont_follow = followers_set - following_set
    
    print("\nAnalysis Results:")
    print(f"Total Followers: {len(followers)}")
    print(f"Total Following: {len(following)}")
    print(f"People who don't follow you back: {len(not_following_back)}")
    print(f"People you don't follow back: {len(you_dont_follow)}")
    
    # Save results to a file
    with open("follower_analysis.txt", "w", encoding='utf-8') as f:
        f.write("People who don't follow you back:\n")
        f.write("\n".join(sorted(not_following_back)))
        f.write("\n\nPeople you don't follow back:\n")
        f.write("\n".join(sorted(you_dont_follow)))
    
    print("\nDetailed analysis saved to 'follower_analysis.txt'")

def main():
    print("Instagram Follower Analyzer")
    print("Looking for Instagram data zip file...")
    
    # Check both current directory and Downloads folder
    search_dirs = [".", os.path.expanduser("~/Downloads")]
    
    for directory in search_dirs:
        zip_file = find_instagram_zip(directory)
        if zip_file:
            print(f"Found zip file: {zip_file}")
            extract_and_analyze_followers(zip_file)
            return
    
    print("\nError: Could not find Instagram data zip file.")
    print("Please make sure the file name matches:")
    print("'instagram-hookedonoxy-YYYY-MM-DD-randomChars.zip'")
    print("and is in either:")
    print(f"- Current directory: {os.getcwd()}")
    print(f"- Downloads folder: {os.path.expanduser('~/Downloads')}")
    print("\nYou can also drag and drop the zip file onto this script to analyze it.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # If file is dragged onto the script
        zip_path = sys.argv[1]
        if os.path.isfile(zip_path) and zip_path.endswith('.zip'):
            extract_and_analyze_followers(zip_path)
        else:
            print(f"Error: {zip_path} is not a valid zip file")
    else:
        main()