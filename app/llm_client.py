import subprocess

class LLMClient:
    def __init__(self, provider="ollama", model="mistral"):
        self.provider = provider
        self.model = model

    def generate(self, prompt: str) -> str:
        if self.provider == "ollama":
            try:
                result = subprocess.run(
                    ["ollama", "run", self.model, prompt],
                    capture_output=True, text=True, encoding="utf-8", check=True
                )
                return result.stdout.strip()
            except subprocess.CalledProcessError as e:
                return f"Error running model: {e.stderr.strip()}"
            except Exception as e:
                return f"Unexpected error: {str(e)}"
        else:
            raise ValueError("Unsupported provider in this build")