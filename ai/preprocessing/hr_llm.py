# hr_assistant.py
from langchain_ollama import ChatOllama


class HRAssistant:
    def __init__(self, model_name="qwen2.5:1.5b"):
        self.llm = ChatOllama(
            model=model_name,
            temperature=0.3,
            base_url="http://localhost:11434"
        )
        print(f" Модель {model_name} готова к работе!")

    def analyze_resume(self, resume_text):
        """Анализ одного резюме"""
        prompt = f"""
        Ты HR-специалист. Проанализируй резюме кандидата.

        Резюме:
        {resume_text}

        Ответь на вопросы:
        1. Имя кандидата
        2. Сколько лет опыта
        3. Ключевые навыки (через запятую)
        4. Уровень (Junior/Middle/Senior)
        5. Рекомендация (Подходит/Не подходит/Возможно)
        """

        response = self.llm.invoke(prompt)
        return response.content

    def compare_resumes(self, resumes_list, requirements):
        """Сравнение нескольких резюме"""
        text = "\n---\n".join([f"Резюме {i + 1}:\n{r}" for i, r in enumerate(resumes_list)])

        prompt = f"""
        Требования к вакансии:
        {requirements}

        {text}

        Отсортируй кандидатов от лучшего к худшему.
        Для каждого укажи:
        - Номер резюме
        - Сильные стороны
        - Слабые стороны
        - Оценка соответствия (0-100%)
        """

        response = self.llm.invoke(prompt)
        return response.content


def main():
    # Создаем ассистента
    assistant = HRAssistant()

    print("\n" + "=" * 50)
    print("HR Ассистент на базе Qwen 2.5 1.5B")
    print("=" * 50)

    while True:
        print("\nВыберите действие:")
        print("1. Анализ одного резюме")
        print("2. Сравнение нескольких резюме")
        print("3. Выход")

        choice = input("Ваш выбор (1-3): ")

        if choice == "1":
            print("\nВведите текст резюме (для окончания ввода нажмите Enter дважды):")
            lines = []
            while True:
                line = input()
                if line:
                    lines.append(line)
                else:
                    break
            resume = "\n".join(lines)

            if resume:
                print("\n Анализирую...")
                result = assistant.analyze_resume(resume)
                print("\n Результат анализа:")
                print(result)

        elif choice == "2":
            resumes = []
            print("\nВведите количество резюме для сравнения:")
            n = int(input("Количество: "))

            for i in range(n):
                print(f"\n--- Резюме {i + 1} ---")
                print("Введите текст (Enter дважды для окончания):")
                lines = []
                while True:
                    line = input()
                    if line:
                        lines.append(line)
                    else:
                        break
                resumes.append("\n".join(lines))

            print("\nВведите требования к вакансии:")
            req_lines = []
            while True:
                line = input()
                if line:
                    req_lines.append(line)
                else:
                    break
            requirements = "\n".join(req_lines)

            if resumes and requirements:
                print("\n Сравниваю...")
                result = assistant.compare_resumes(resumes, requirements)
                print("\n Результат сравнения:")
                print(result)

        elif choice == "3":
            print("До свидания!")
            break

        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()