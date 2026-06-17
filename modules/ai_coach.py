from .context_engine import build_context_summary
from .recommendation_engine import build_recommendations


def build_ai_response(record, question):
    if not record:
        return "Please submit your lifestyle profile first so the coach can provide personalized guidance."

    summary = build_context_summary(record)
    question_text = question.strip().lower()

    if not question_text:
        return "Ask a question about your carbon footprint, emissions, or how to improve your habits."

    inappropriate = ["stupid", "shut up", "idiot", "hate", "kill", "fuck", "damn"]
    if any(term in question_text for term in inappropriate):
        return "I am here to help with carbon awareness. That request is inappropriate or unrelated to sustainability."

    if any(term in question_text for term in ["reduce", "lower", "improve", "better", "decrease", "cut", "should"]):
        if summary["primary_source"] == "Transportation":
            return "Your transportation habits are the largest source of emissions. Use public transport, walk for short trips, or combine errands to make a quick impact."
        if summary["primary_source"] == "Electricity":
            return "Electricity use is a key driver for your footprint. Switching to LED lights, unplugging idle devices, and reducing heating/cooling waste will lower your monthly total."
        if summary["primary_source"] == "Food":
            return "Your food choices have a strong effect. Try moving one or two meals per week toward plant-based dishes and reduce high-emission meats."
        if summary["primary_source"] == "Shopping":
            return "Shopping less and choosing reusable products helps lower your footprint. Focus on durable goods and avoid impulse buys."
        if summary["primary_source"] == "Air Travel":
            return "Air travel is your top contributor. Fly less often, choose direct flights, and offset emissions when you do travel."

    if any(term in question_text for term in ["why", "cause", "source", "highest", "main"]):
        return f"Your biggest emission source is {summary['primary_source']}. {summary['secondary_source']} is the next area to improve. Focus there for the greatest benefit."

    if any(term in question_text for term in ["progress", "track", "goal", "streak", "save"]):
        return "Track one sustainable action each day and review your progress weekly. Consistency is more important than perfection when reducing your footprint."

    if any(term in question_text for term in ["score", "rating", "impact"]):
        return f"Your sustainability score is {summary['sustainability_score']} out of 100. Lowering your top source and keeping steady improvements in transport, food, and energy use will help raise it."

    return "Based on your current profile, focus on your highest emission source first and make one small change each week. Ask how to reduce transport, electricity, food, shopping, or air travel emissions for more details."
