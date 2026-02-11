import qrcode
import os
import uuid
from app.core.config import DATA_DIR
from app.core.security import security_manager

class QRHandler:
    def __init__(self):
        self.qr_dir = os.path.join(DATA_DIR, "qr_codes")
        if not os.path.exists(self.qr_dir):
            os.makedirs(self.qr_dir)

    def generate_qr(self, text: str, secure: bool = False) -> str:
        """
        Generate a QR code image and return the absolute path.
        If secure is True, the text is encrypted before generation.
        """
        if not text:
            return ""

        content = text
        prefix = "qr_"
        if secure:
            content = security_manager.encrypt(text)
            prefix = "secure_qr_"

        # Create unique filename
        filename = f"{prefix}{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(self.qr_dir, filename)

        # Generate QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(content)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filepath)

        return filepath

    def cleanup_old_qrs(self):
        """Optionally cleanup old QR files to save space."""
        # Implementation for later if needed
        pass

qr_handler = QRHandler()
