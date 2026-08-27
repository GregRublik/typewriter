from pydantic_settings import BaseSettings, SettingsConfigDict

class LLMSettings(BaseSettings):
    host: str
    port: int

    model_config = SettingsConfigDict(env_file=".env", env_prefix="LLM_", extra="ignore")


class Settings(BaseSettings):
    host: str
    port: int
    ocr_engine: str = "tesseract"  # "tesseract" (лёгкий) или "paddle" (тяжёлый, качественнее)

    llm: LLMSettings

    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_", extra="ignore")

settings = Settings(
    llm=LLMSettings(),
)

types = {
    "result": [
        {
            "name": "Сертификат соответствия",
            "value": "certificate_of_conformity"
        },
        {
            "name": "Декларация о соответствии",
            "value": "declaration"
        },
        {
            "name": "Свидетельство о регистрации",
            "value": "certificate_of_registration"
        },
        {
            "name": "Регистрационное удостоверение",
            "value": "registration_certificate"
        },
        {
            "name": "Отказное письмо",
            "value": "refused_letter"
        },
        {
            "name": "Ветеринарное свидетельство",
            "value": "veterinary_cover_document"
        },
        {
            "name": "Паспорт безопасности",
            "value": "safety_data_sheet"
        }
    ]
}