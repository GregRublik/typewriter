import json
from config import types, standards, settings
import requests

class TypeWriterService:

    @staticmethod
    def generate_prompt(text_document):
        return f"""
        Определи тип и стандарт документа а также страну стандарта.
        Возможные типы:
        {json.dumps(types, ensure_ascii=False)}
        Возможные стандарты:
        {json.dumps(standards, ensure_ascii=False)}
        Документ:
        {text_document}
        Формат ответа:
        {{"name": "название типа", "value": "значение типа", "standard": "стандарт, например(EAEU)", "country": "alpha-2 код страны" }}
        Верни ТОЛЬКО валидный JSON без markdown и дополнительного текста.
        В ответе не должно быть символов (`,\n,\)
        Ответ:
        """

    def run(self, text_document):

        prompt = self.generate_prompt(text_document)

        # response = requests.post(
        #     f"http://{settings.llm.host}:{settings.llm.port}/completion",
        #     headers={"Content-Type": "application/json"},
        #     json={
        #         "prompt": prompt,
        #         "n_predict": 50
        #     }
        # )
        #
        # return response.json()
        if settings.llm.use_free:
            print("use free mode")

            response = requests.post(
                "http://localhost:20128/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {settings.llm.api_key}",
                },
                json={
                    "model": "ds-web/deepseek-v4-pro",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    "stream": False,
                },
            )

            # response.raise_for_status()
            print(response)

            result = response.json()
            # return response.text

        else:
            response = requests.post(
                'https://api.deepseek.com/chat/completions',
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {settings.llm.api_key}"
                },
                json={
                    "model": "deepseek-v4-flash",  # или "deepseek-v4-flash"[reference:3]
                    "messages": [
                        {"role": "user", "content": prompt}  # Промпт передается здесь
                    ],
                    # "max_tokens": 50  # Аналог n_predict[reference:4]
                }
            )
            result = response.json()
        return result

typewriter_service = TypeWriterService()
