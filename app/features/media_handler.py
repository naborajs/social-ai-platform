from PIL import Image
import os
import time

try:
    from moviepy.editor import VideoFileClip
except ImportError:
    print("Warning: moviepy not installed or audio dependencies missing. Video to GIF disabled.")
    VideoFileClip = None

OUTPUT_DIR = "media_output"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def create_sticker(image_path: str) -> str:
    """Convert an image to a WebP sticker (512x512)."""
    try:
        img = Image.open(image_path)
        img.thumbnail((512, 512))
        
        # Create a new transparent image
        sticker = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        
        # Center the image
        offset_x = (512 - img.width) // 2
        offset_y = (512 - img.height) // 2
        sticker.paste(img, (offset_x, offset_y))
        
        output_filename = f"sticker_{int(time.time())}.webp"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        sticker.save(output_path, "WEBP")
        return output_path
    except Exception as e:
        print(f"❌ Error creating sticker: {e}")
        return None

def create_gif(video_path: str) -> str:
    """Convert a video to a GIF."""
    if not VideoFileClip:
        return None
        
    try:
        clip = VideoFileClip(video_path)
        
        # Resize if too large (max width 320 for performance/size)
        if clip.w > 320:
             clip = clip.resize(width=320)
             
        # Limit duration to 5 seconds
        if clip.duration > 5:
            clip = clip.subclip(0, 5)
            
        output_filename = f"gif_{int(time.time())}.gif"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        clip.write_gif(output_path, fps=10, program='ffmpeg') # Requires ffmpeg, moviepy usually downloads it
        return output_path
    except Exception as e:
        print(f"❌ Error creating GIF: {e}")
        return None
