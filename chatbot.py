def get_chatbot_response(question):
    question = question.lower().strip()

    if not question:
        return "Please enter a question."

    # Workout questions
    if "workout" in question or "exercise" in question:
        return (
            "For beginners, start with simple exercises like walking, "
            "squats, push-ups and stretching. Start slowly and increase "
            "the intensity gradually."
        )

    # Diet questions
    elif "diet" in question or "food" in question or "eat" in question:
        return (
            "For a healthy diet, include vegetables, fruits, whole grains, "
            "protein-rich foods and enough water. Choose food according "
            "to your fitness goal."
        )

    # Protein
    elif "protein" in question:
        return (
            "Good protein sources include eggs, milk, curd, paneer, "
            "dal, beans, soy, chicken and fish."
        )

    # Water
    elif "water" in question or "drink" in question:
        return (
            "Stay hydrated throughout the day. Your water requirement "
            "can vary depending on activity, weather and individual needs."
        )

    # BMI
    elif "bmi" in question:
        return (
            "BMI is calculated using your weight and height. "
            "Your project uses BMI to help provide personalized "
            "fitness recommendations."
        )

    # Weight gain
    elif "weight gain" in question or "gain weight" in question:
        return (
            "For weight gain, focus on nutritious calorie-rich foods "
            "and adequate protein along with strength training."
        )

    # Weight loss
    elif "weight loss" in question or "lose weight" in question:
        return (
            "For weight loss, combine regular physical activity with "
            "a balanced diet and appropriate calorie intake."
        )

    # Greetings
    elif "hello" in question or "hi" in question or "hey" in question:
        return (
            "Hello! I am your AI Fitness Assistant. "
            "You can ask me about workouts, diet, protein, water or BMI."
        )

    else:
        return (
            "I can help you with workouts, diet, protein, water, BMI, "
            "weight loss and weight gain. Please ask a fitness-related question."
        )