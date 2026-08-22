from .media import Sticker
import subprocess

class Utils:
    @staticmethod
    async def webm_to_gif(m_bytes):
        result = subprocess.run(
        [
            "ffmpeg",
            "-i", "pipe:0",
            "-vf", "fps=15,scale=512:-1:flags=lanczos",
            "-f", "gif",
            "pipe:1"
        ],
        input=m_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True
    )

        return result.stdout