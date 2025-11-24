import requests
import json

class LLMClient:
    def __init__(self, provider="ollama", model="minimax-m2:cloud"):
        self.provider = provider
        self.model = model

        # Define persona-specific generation settings
        self.persona_settings = {
            "efficient": {"temperature": 0.3, "top_p": 0.8, "num_predict": 150},
            "empathetic": {"temperature": 0.7, "top_p": 0.95, "num_predict": 200},
            "direct": {"temperature": 0.2, "top_p": 0.7, "num_predict": 120},
            "chatty": {"temperature": 0.9, "top_p": 1.0, "num_predict": 220},
            "general": {"temperature": 0.7, "top_p": 0.9, "num_predict": 150}  # fallback/default
        }

    def generate(self, prompt: str, persona: str = "general") -> str:
        if self.provider == "ollama":
            try:
                # Use persona-specific settings or fallback to general
                options = self.persona_settings.get(persona.lower(), self.persona_settings["general"])

                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "options": options,
                        "stream": False
                    }
                )
                response.raise_for_status()
                return response.json().get("response", "").strip()
            except requests.exceptions.RequestException as e:
                return f"Error calling Ollama API: {str(e)}"
        else:
            raise ValueError("Unsupported provider in this build")