def load_questions_from_txt(file_path):
    questions = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    question = {}
    options = {}
    for line in lines:
        line = line.strip()
        if line.startswith('Pergunta:'):
            if question:
                question["options"] = options
                questions.append(question)
            question = {"question": line[len('Pergunta: '):]}
            options = {}
        elif line.startswith('A)'):
            options["A"] = line[len('A) '):]
        elif line.startswith('B)'):
            options["B"] = line[len('B) '):]
        elif line.startswith('C)'):
            options["C"] = line[len('C) '):]
        elif line.startswith('D)'):
            options["D"] = line[len('D) '):]
        elif line.startswith('Resposta Correta:'):
            question["correct_answer"] = line[len('Resposta Correta: '):]

    if question:
        question["options"] = options
        questions.append(question)

    return questions
