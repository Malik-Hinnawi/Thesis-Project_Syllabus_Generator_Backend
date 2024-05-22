from googleapiclient.discovery import build
from isodate import parse_duration
import time
from decouple import config


class YoutubeHelper:

    def __init__(self, api):
        self.api = api

    @staticmethod
    def search_youtube_videos(api_key, query, max_results=5):
        youtube = build('youtube', 'v3', developerKey=api_key)

        # Call the search.list method to retrieve results matching the specified query term.
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=max_results
        ).execute()

        videos = []

        # Add each result to the list
        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                videos.append({
                    'title': search_result['snippet']['title'],
                    'video_id': search_result['id']['videoId'],
                    'url': f"https://www.youtube.com/watch?v={search_result['id']['videoId']}"
                })

        return videos

    @staticmethod
    def get_video_duration(api_key, video_id):
        youtube = build('youtube', 'v3', developerKey=api_key)

        # Call the videos.list method to retrieve information about the specified video.
        videos_response = youtube.videos().list(
            part='contentDetails',
            id=video_id
        ).execute()

        # Extract duration from the response
        duration = videos_response['items'][0]['contentDetails']['duration']

        return duration

    def get_most_popular_videos(self, api_key, query):
        videos = self.search_youtube_videos(api_key, query)

        if not videos:
            return None

        for video in videos:
            duration = parse_duration(self.get_video_duration(api_key, video['video_id']))
            if duration.total_seconds() > 300:  # 20 minutes in seconds
                return video

        return None

    def youtube_videos(self, query):
        output = None
        most_popular_video = self.get_most_popular_videos(self.api, query)
        if most_popular_video:
            output = [most_popular_video['title'], most_popular_video['url']]
        time.sleep(5)

        return output


yh = YoutubeHelper(config('API_KEY'))
