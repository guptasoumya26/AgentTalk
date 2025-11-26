import os
from pathlib import Path
from jproperties import Properties
from dotenv import load_dotenv

class ConfigLoader:
    def __init__(self):
        self.config = {}
        self._load_config()

    def _load_config(self):
        base_path = Path(__file__).parent.parent

        env_path = base_path / '.env'
        if env_path.exists():
            load_dotenv(env_path)
            self.config = {
                'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
                'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
                'GROQ_API_KEY': os.getenv('GROQ_API_KEY'),
                'OPENAI_MODEL': os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
                'GOOGLE_MODEL': os.getenv('GOOGLE_MODEL', 'gemini-pro'),
                'GROQ_MODEL': os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile'),
            }
        else:
            props_path = base_path / 'config.properties'
            if props_path.exists():
                props = Properties()
                with open(props_path, 'rb') as f:
                    props.load(f)

                self.config = {
                    'OPENAI_API_KEY': props.get('OPENAI_API_KEY').data if props.get('OPENAI_API_KEY') else None,
                    'GOOGLE_API_KEY': props.get('GOOGLE_API_KEY').data if props.get('GOOGLE_API_KEY') else None,
                    'GROQ_API_KEY': props.get('GROQ_API_KEY').data if props.get('GROQ_API_KEY') else None,
                    'OPENAI_MODEL': props.get('OPENAI_MODEL').data if props.get('OPENAI_MODEL') else 'gpt-3.5-turbo',
                    'GOOGLE_MODEL': props.get('GOOGLE_MODEL').data if props.get('GOOGLE_MODEL') else 'gemini-pro',
                    'GROQ_MODEL': props.get('GROQ_MODEL').data if props.get('GROQ_MODEL') else 'llama-3.3-70b-versatile',
                }

    def get(self, key):
        value = self.config.get(key)
        if value and value.startswith('your_') and value.endswith('_here'):
            return None
        return value

    def is_configured(self):
        return any([
            self.get('OPENAI_API_KEY'),
            self.get('GOOGLE_API_KEY'),
            self.get('GROQ_API_KEY')
        ])
