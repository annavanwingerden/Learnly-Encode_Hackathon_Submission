from portia.errors import ToolHardError
from pydantic import BaseModel, Field
from portia.tool import Tool, ToolRunContext
import subprocess
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import os

class FindVideoToolSchema(BaseModel):
    """Schema defining the inputs for the FindVideoTool"""
    topic: str = Field(...,
                          description = "Chosen topic for Youtube video transcript to find")
    
class FindVideoTool(Tool[str]):
    """Returns the transcript and url for a video about the chosen topic"""
    
    id: str = "find_video_tool"
    name: str = "Find video tool"
    description: str = "Finds a youtube video that matches the topic and returns the transcript and the url"
    args_schema: type[BaseModel] = FindVideoToolSchema
    output_schema: tuple[str, str] = ("str", "The video transcript of the youtube video, with the url at the front")

    def run(self, _: ToolRunContext, topic: str) -> str:
        """Run the NotionPageAddTool"""
        
        load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.local'))

        GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
        
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': topic,
            'type': 'video',
            'key': GOOGLE_API_KEY
        }
        
        # Make the request to the YouTube API
        response = requests.get(url, params=params)
        data = response.json()
        
        # Check if we got results
        if 'items' in data and len(data['items']) > 0:
            # Return the video ID of the first result
            id = data['items'][0]['id']['videoId']
        else:
            return None
        
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.list(video_id=id).find_transcript(['en']).fetch(preserve_formatting=False)
        transcript_entries = fetched_transcript.to_raw_data()  
        transcript_text = ' '.join([entry['text'] for entry in transcript_entries]) 
        return 'https://www.youtube.com/watch?v='+id + " : " +transcript_text