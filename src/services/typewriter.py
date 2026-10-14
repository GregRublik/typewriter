import json
import time

from config import types, standards, settings
import requests

MAX_ATTEMPTS = 3  # первая попытка + 2 повтора
RETRY_DELAY = 3  # секунды, дальше удваивается: 3, 6
REQUEST_TIMEOUT = (10, 120)  # (подключение, чтение) — без таймаута запрос может висеть бесконечно
RETRYABLE_STATUS = {408, 429, 500, 502, 503, 504}  # временные ошибки, имеет смысл повторить


class TypeWriterError(Exception):
    """LLM не ответила или вернула ошибку. retryable=False — повторять бессмысленно."""

    def __init__(self, message, retryable=True):
        super().__init__(message)
        self.retryable = retryable


def error_reason(response):
    """Короткое описание ошибки из тела ответа роутера/провайдера."""
    try:
        body = response.json()
    except ValueError:
        body = None

    message = None
    if isinstance(body, dict):
        error = body.get("error")
        if isinstance(error, dict):
            message = error.get("message")
        elif error:
            message = str(error)

    if not message:
        message = (response.text or "").strip()[:200] or "пустой ответ"

    return f"HTTP {response.status_code}: {message[:300]}"


class TypeWriterService:

    @staticmethod
    def generate_prompt(text_document):
        return f"""
        Твоя задача Просмотреть документ и вернуть по нему json.
        Определи Тип, Стандарт документа, Страну стандарта и Торговое наименование.
        Возможные типы:
        {json.dumps(types, ensure_ascii=False)}
        Возможные стандарты:
        {json.dumps(standards, ensure_ascii=False)}
        Торговое наименование - Это полное название продукта для которого выписывается Документ
        Документ:
        {text_document}
        Формат ответа:
        {{"name": "название типа", "value": "значение типа", "standard": "стандарт, например(EAEU)", "country": "alpha-2 код страны", "trade_name": "Торговое наименование продукта" }}
        Верни ТОЛЬКО валидный JSON без markdown и дополнительного текста.
        В ответе не должно быть символов (```json ```, `, \n,\)
        Ответ:
        """

    @staticmethod
    def _request(url, headers, payload):
        """Один запрос к LLM. Возвращает тело ответа как dict или бросает TypeWriterError."""
        response = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
        print(response)

        if response.status_code in RETRYABLE_STATUS:
            raise TypeWriterError(error_reason(response))

        if response.status_code >= 400:
            # 4xx кроме 408/429 — ошибка в запросе или ключе, повтор не поможет
            raise TypeWriterError(error_reason(response), retryable=False)

        result = response.json()  # ValueError, если тело не json — тоже повод повторить

        if "choices" not in result:
            raise TypeWriterError(error_reason(response))

        return result

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

            url = "http://localhost:20128/v1/chat/completions"
            payload = {
                "model": "ds/deepseek-v4-flash",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "stream": False,
            }
        else:
            url = "https://api.deepseek.com/chat/completions"
            payload = {
                "model": "deepseek-v4-flash",  # или "deepseek-v4-flash"[reference:3]
                "messages": [
                    {"role": "user", "content": prompt}  # Промпт передается здесь
                ],
                # "max_tokens": 50  # Аналог n_predict[reference:4]
            }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.llm.api_key}",
        }

        last_error = None

        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                return self._request(url, headers, payload)
            except TypeWriterError as e:
                if not e.retryable:
                    raise
                last_error = e
            except (requests.RequestException, ValueError) as e:
                last_error = e

            if attempt == MAX_ATTEMPTS:
                break

            delay = RETRY_DELAY * 2 ** (attempt - 1)
            print(f"Попытка {attempt}/{MAX_ATTEMPTS} не удалась ({last_error}). Повтор через {delay} с")
            time.sleep(delay)

        raise TypeWriterError(
            f"Сервис распознавания недоступен после {MAX_ATTEMPTS} попыток. "
            f"Последняя ошибка: {last_error}"
        ) from last_error


typewriter_service = TypeWriterService()
