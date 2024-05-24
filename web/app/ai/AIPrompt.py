import random

from app.ai.AIQuestion import AIQuestion
from app.ai.AIQuestionAnswer import AIQuestionAnswer


class AIPrompt:
    _const = "Siber güvenlik eğitimi vereceğim. Bana dilinde labı hazırlar mısın lütfen"

    def __init__(
        self,
        aiQuestion: AIQuestion = None,
        vulnerability: str | None = None,
        language: str | None = None,
    ) -> None:
        self.messages = []
        self._selected = {"language": None, "vulnerability": None}
        self.vulnerability = self._validate_vulnerability(vulnerability)
        self.language = self._validate_language(language)
        self.aiQuestion = aiQuestion
        self._options = {
            "languages": ["PHP", "Java", "Python", "Ruby", "Node Js", "C++"],
            "vulnerabilities": [
                "sql injection",
                "xss",
                "idor",
                "deserialization",
                "rce",
                "prototype pollution",
            ],
        }

    def _validate_vulnerability(self, vulnerability: str):
        if vulnerability is None and vulnerability in self._options["vulnerabilities"]:
            raise ValueError("QuestionNumber must be a positive integer")

        self._selected["vulnerability"] = vulnerability

        return vulnerability

    def _validate_language(self, language: str):
        if language is None and language in self._options["languages"]:
            raise ValueError("QuestionNumber must be a positive integer")

        self._selected["language"] = language

        return language

    def _validate_option(self, option_type, value):
        if value.lower() not in self._options[option_type]:
            raise ValueError(
                f"Lütfen şu değerlerden birini girin: {', '.join(self._options[option_type])}"
            )

    def set_option(self, option_type, value):
        self._validate_option(option_type, value)
        self._selected[option_type] = value.lower()

    def list_options(self, option_type):
        return self._options[option_type]

    def choose_random_option(self, option_type):
        self._selected[option_type] = random.choice(self._options[option_type])

    def clear_selected_option(self, option_type):
        self._selected[option_type] = None

    def ai_prompt_format(self):
        if all(self._selected.values()):
            chunks = self._const.split(".")[0].strip()
            self.messages = [
                {
                    "role": "system",
                    "content": "Sen bir siber güvenlik asistanısın",
                },
                {
                    "role": "user",
                    "content": f"{chunks} {self._selected['language']} dilinde {self._selected['vulnerability']} labı hazırlar mısın lütfen. Lab kod örneği olacak ! Düzgün bir biçimde labı ver syntaxı doğru olsun ! Labı yazarken Lab: diye başla !",
                },
                {
                    "role": "user",
                    "content": self.aiQuestion.generate_question_string(),
                },
                {
                    "role": "user",
                    "content": AIQuestionAnswer.generate_answer_string(),
                },
            ]

            return self.get_message

    @property
    def get_message(self):
        return self.messages
