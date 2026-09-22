def get_study_prompt(user_input, mode="Normal", subject="General"):

    base = f"Topic: {user_input}"

    if subject == "Math":
        base += "\nSolve step-by-step with formulas."

    elif subject == "Programming":
        base += "\nExplain with code examples."

    elif subject == "Science":
        base += "\nExplain with real-life examples."

    if mode == "Beginner":
        return f"{base}\nExplain in very simple language."

    elif mode == "Exam Revision":
        return f"{base}\nGive short notes."

    return f"{base}\nExplain clearly with examples."
