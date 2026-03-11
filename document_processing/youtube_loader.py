import re
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url):

    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)

    if match:
        return match.group(1)

    return None


def load_youtube_video(url):

    video_id = extract_video_id(url)

    if not video_id:
        print("\nInvalid YouTube link. Please try again with a valid link or press enter to skip.\n")
        return []

    try:

        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id)

    except Exception as e:

        print("\nCould not retrieve transcript for this video.")
        print("Reason:", e)
        print("Try another link or press enter to skip.\n")

        return []

    chunks = []

    current_text = ""
    start_time = transcript[0].start

    window = 30  # seconds

    for segment in transcript:

        if segment.start - start_time < window:

            current_text += segment.text + " "

        else:

            chunks.append({
                "doc_id": f"youtube:{video_id}",
                "text": f"[{start_time:.1f}s] {current_text.strip()}"
            })

            start_time = segment.start
            current_text = segment.text + " "

    if current_text:
        chunks.append({
            "doc_id": f"youtube:{video_id}",
            "text": f"[{start_time:.1f}s] {current_text.strip()}"
        })

    return chunks