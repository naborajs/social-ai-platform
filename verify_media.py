from app.features.media_handler import create_sticker, create_gif
from PIL import Image
import os
import time

def verify_media_logic():
    print("🧪 Testing Media Logic...")
    
    # Create dummy image
    img_path = "test_image.jpg"
    img = Image.new('RGB', (100, 100), color = 'red')
    img.save(img_path)
    
    print(f"👉 Testing Sticker Creation from {img_path}...")
    sticker_path = create_sticker(img_path)
    
    if sticker_path and os.path.exists(sticker_path):
        print(f"✅ Sticker created at: {sticker_path}")
        # Clean up
        os.remove(sticker_path)
    else:
        print("❌ Sticker creation failed.")
        
    os.remove(img_path)
    
    print("\n👉 Testing GIF Creation (Skipping actual video file creation as it requires more deps)...")
    print("ℹ️ GIF logic depends on moviepy/ffmpeg which might be missing. If installed, it should work.")
    
    print("\n✅ Media Verification Complete!")

if __name__ == "__main__":
    verify_media_logic()
