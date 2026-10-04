import os

class Settings:
    @property
    def narada_llm_provider(self) -> str:
        return os.getenv("NARADA_LLM_PROVIDER", "ollama")
        
    @property
    def sarvam_api_key(self) -> str:
        return os.getenv("SARVAM_API_KEY", "")
        
    @property
    def sarvam_model(self) -> str:
        return os.getenv("SARVAM_MODEL", "sarvam-105b")
        
    @property
    def ollama_base_url(self) -> str:
        return os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
        
    @property
    def ollama_model(self) -> str:
        return os.getenv("OLLAMA_MODEL", "llama2")

settings = Settings()
