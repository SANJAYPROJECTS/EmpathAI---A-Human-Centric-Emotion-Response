from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips


def adjust_video_length(video_clip, audio_clip):
    # Calculate the duration of the audio clip
    audio_duration = audio_clip.duration
    
    # Trim or pad the video clip to match the duration of the audio clip
    video_duration = video_clip.duration
    if video_duration < audio_duration:
        # Pad the video clip with black frames to match the audio duration
        padded_video_clip = video_clip.set_duration(audio_duration)
    elif video_duration > audio_duration:
        # Trim the video clip to match the audio duration
        trimmed_video_clip = video_clip.subclip(0, audio_duration)
        return trimmed_video_clip
    else:
        return video_clip

def combine_video_and_audio(video_path, audio_path, output_path):
    # Load the video clip
    video_clip = VideoFileClip(video_path)
    
    # Load the audio clip
    audio_clip = AudioFileClip(audio_path)
    
    # Adjust the video length to match the audio length
    adjusted_video_clip = adjust_video_length(video_clip, audio_clip)
    
    # Set the audio of the adjusted video clip to the provided audio
    video_with_audio_clip = adjusted_video_clip.set_audio(audio_clip)
    
    # Write the combined video with audio to the output file
    video_with_audio_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')


