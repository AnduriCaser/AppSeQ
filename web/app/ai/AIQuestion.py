from app.ai.AIPromptValidation import AIPromptValidation


class AIQuestion(AIPromptValidation):
    DIFFICULTIES = ["kolay", "orta", "zor"]

    def __init__(
        self, difficulty: str | None = None, question_number: str | None = None
    ) -> None:
        self.difficulty = self._validate_difficulty(difficulty)
        self.question_number = self._validate_question_number(question_number)

    def _validate_difficulty(self, difficulty):
        if difficulty not in AIQuestion.DIFFICULTIES:
            raise ValueError("Invalid difficulty level")

        return difficulty

    def _validate_question_number(self, question_number):
        if not isinstance(question_number, int) or question_number <= 0:
            raise ValueError("QuestionNumber must be a positive integer")

        return question_number

    @classmethod
    def validate_values(cls, **kwargs):
        super().validate_values(**kwargs)


    @classmethod
    def sanitize_values(cls, **kwargs):
        super().sanitize_values(**kwargs)

    def generate_question_string(self) -> str:
        return f"Bana bu oluşturduğun lab ile alakalı {self.question_number} tane {self.difficulty} soru oluşturur musun? Soru çok çok kısa olsun 2 kelime falan Soruyu yazarken Soru: diye başla !"
