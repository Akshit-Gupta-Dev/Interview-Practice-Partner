import subprocess

class LLMClient:
    def __init__(self, provider="ollama", model="mistral"):
        self.provider = provider
        self.model = model

    def generate(self, prompt: str) -> str:
        if self.provider == "ollama":
            result = subprocess.run(
                ["ollama", "run", self.model, prompt],
                capture_output=True, text=True
            )
            return result.stdout.strip()
        else:
            raise ValueError("Unsupported provider in this build")