import re

class AIResponseParser:
    @staticmethod
    async def parse_completion_choices(completion):
        parsed_data = []

        for choice in completion.choices:
            content = choice.message.content
            print("DEBUG: Full Content: ", content)  # Debugging line

            # Split content by "Lab:", "Soru:", and "Cevap:"
            parts = re.split(r'(Lab:|Soru:|Cevap:)', content)

            lab_content = None
            question_content = None
            answer_content = None

            for i in range(1, len(parts), 2):
                if parts[i] == "Lab:":
                    lab_content = parts[i + 1].strip()
                    parsed_data.append({"lab": lab_content})
                elif parts[i] == "Soru:":
                    question_content = parts[i + 1].strip()
                    if parsed_data:
                        parsed_data[-1]["question"] = question_content
                    else:
                        parsed_data.append({"question": question_content})
                elif parts[i] == "Cevap:":
                    answer_content = parts[i + 1].strip()
                    if parsed_data:
                        parsed_data[-1]["answer"] = answer_content
                    else:
                        parsed_data.append({"answer": answer_content})


        return parsed_data