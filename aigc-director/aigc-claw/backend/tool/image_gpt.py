import os
import time
import uuid
import base64
import httpx
from openai import OpenAI
try:
    from tool.image_processor import ImageProcessor
except ImportError:
    from image_processor import ImageProcessor


class ImageGPT:
    """
    OpenAI 图片生成客户端
    支持模型：
        - sora_image → Images API
        - gpt-image-2 → Responses API
    """
    def __init__(self,
                 api_key: str = None,
                 base_url: str = None,
                 local_proxy: str = None,
                 timeout: float = 300.0):
        """
        OpenAI 图片生成客户端
        :param api_key: API Key
        :param base_url: 自定义 Base URL（如果传入，则不使用本地代理）
        :param timeout: 超时时间
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.timeout = timeout
        
        kwargs = {"api_key": self.api_key, "timeout": self.timeout}
        
        self.base_url = base_url
        if not self.base_url and local_proxy:
            kwargs["http_client"] = httpx.Client(
                proxy=local_proxy,
                timeout=self.timeout,
            )
        if self.base_url:
            kwargs["base_url"] = self.base_url
            
        self.client = OpenAI(**kwargs)
        self.max_attempts = 10
        self.image_processor = ImageProcessor()

    def generate_image(self, prompt, size="1024x1024", quality="high", model="gpt-image-2",
                       save_dir=None, image_urls=None):
        """Generate a single image, download it, and return the local file path.

        Args:
            prompt: 图片描述提示词
            size: 图片尺寸
            quality: 图片质量
            model: 模型名称 (sora_image / gpt-image-2)
            save_dir: 保存目录（不传则返回 URL 或 base64）
            image_urls: 参考图片 URL 列表（仅 gpt-image-2 支持）
        """

        attempts = 0
        last_error = None
        while attempts < self.max_attempts:
            try:
                response = self.client.images.generate(
                    model=model,
                    prompt=prompt,
                    size=size,
                    quality=quality,
                    n=1,
                )
                if response and response.data and response.data[0].url:
                    url = response.data[0].url
                    if save_dir:
                        os.makedirs(save_dir, exist_ok=True)
                        file_name = f"sora_{int(time.time())}_{uuid.uuid4().hex[:6]}.png"
                        file_path = os.path.join(save_dir, file_name)
                        if self.image_processor.download_image(url, file_path):
                            return file_path
                        else:
                            print(f"Failed to save image from {url}")
                    else:
                        return url
            except Exception as e:
                last_error = e
                msg = str(e)
                # Other errors: wait before retry
                print(f"Image generation error: {e}. Retrying in 10 seconds.")
                time.sleep(10)
                break  # Break inner loop to retry all models
            attempts += 1
        raise Exception(f"Max attempts reached, failed to generate image. Last error: {last_error}")

    def generate_images(self, prompt, count=4, size="1024x1024", quality="standard", model=None):
        """Generate multiple image URLs by calling Images API 'count' times."""
        urls = []
        for _ in range(count):
            url = self.generate_image(prompt=prompt, size=size, quality=quality, model=model)
            urls.append(url)
        return urls


if __name__ == "__main__":
    import sys
    import tempfile
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import Config

    print("=== GPT 图片生成可用性测试 ===")
    api_key = Config.OPENAI_API_KEY
    base_url = Config.OPENAI_BASE_URL
    
    MODELS = ["gpt-image-2.0"]
    img_prompt = "A cute orange cat lying on a sunny windowsill, watercolor style"
    img_path = ""

    if not api_key:
        print("✗ OPENAI_API_KEY 未设置，跳过")
        sys.exit(1)

    print(f"  API Key: {api_key[:6]}***")
    print(f"  Base URL: {base_url}")

    client = ImageGPT(api_key=api_key, base_url=Config.OPENAI_BASE_URL, local_proxy=Config.LOCAL_PROXY)
    for model in MODELS:
        print(f"\nTesting model: {model}")
        print(f"Prompt: {img_prompt}")
        print(f"Image path: {img_path}")
        client.max_attempts = 1
        t0 = time.time()
        save_dir = "result/image/test_avail"
        os.makedirs(save_dir, exist_ok=True)
        try:
            path = client.generate_image(prompt=img_prompt, size="1024x1024",
                                                model=model, save_dir=save_dir)
            elapsed = time.time() - t0
            print(f"✓ 生成成功 ({elapsed:.1f}s): {path}")
        except Exception as e:
            elapsed = time.time() - t0
            print(f"✗ 失败 ({elapsed:.1f}s): {e}")
