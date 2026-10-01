import os
import re

from gemini_client import generate_text

_local_tokenizer = None
_local_model = None


BUILT_IN_EXPLANATIONS = {
    "python variables": """Python variables are names used to store data values.

Important points:
1. A variable is created when a value is assigned to it.
2. Python variables do not need a separate type declaration.
3. A variable can store different types of data.
4. The value stored in a variable can be changed.

Example:
name = "Madhan"
age = 18
marks = 85.5

Here, name, age, and marks are variables.""",

    "python": """Python is a high-level, interpreted programming language known for its simple and readable syntax.

Important points:
1. Python is easy to learn.
2. It supports object-oriented and functional programming.
3. It has many built-in libraries and frameworks.
4. Python is used in web development, AI, machine learning, data science, and automation.

Example:
print("Hello World")""",

    "java": """Java is a high-level, object-oriented programming language used to develop many types of applications.

Important points:
1. Java is platform independent because of the Java Virtual Machine.
2. It supports object-oriented programming.
3. Java provides exception handling and multithreading.
4. It is commonly used for desktop, web, enterprise, and Android-related development.

Example:
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello World");
    }
}""",

    "data structures": """Data structures are methods of organizing and storing data so that it can be accessed and processed efficiently.

Important points:
1. They organize data in a particular structure.
2. Different structures are suitable for different operations.
3. Common data structures include arrays, stacks, queues, linked lists, trees, and graphs.
4. Choosing the right data structure can improve program performance.

Example:
A stack follows LIFO, meaning Last In, First Out.""",

    "stack": """A stack is a linear data structure that follows the LIFO principle: Last In, First Out.

Important points:
1. The last inserted element is removed first.
2. Insertion is called push.
3. Removal is called pop.
4. The top operation can view the top element.

Example:
A stack of plates is similar to a stack data structure.""",

    "queue": """A queue is a linear data structure that follows the FIFO principle: First In, First Out.

Important points:
1. The first inserted element is removed first.
2. Insertion is called enqueue.
3. Removal is called dequeue.
4. Queues are commonly used in scheduling and waiting-line systems.

Example:
People standing in a ticket queue follow the FIFO principle.""",

    "linked list": """A linked list is a linear data structure made up of nodes. Each node contains data and a link to another node.

Important points:
1. Nodes are connected using links.
2. The size can grow or shrink dynamically.
3. Insertion and deletion can be efficient when the correct node is known.
4. A singly linked list contains a link to the next node.

Example:
Node1 -> Node2 -> Node3 -> NULL""",

    "machine learning": """Machine learning is a branch of artificial intelligence in which computers learn patterns from data and use those patterns to make predictions or decisions.

Important points:
1. Machine learning uses data to learn patterns.
2. Supervised learning uses labelled data.
3. Unsupervised learning finds patterns in unlabeled data.
4. Reinforcement learning learns through rewards and penalties.

Example:
A model can learn from previous house prices and predict the price of a new house.""",

    "classification": """Classification is a supervised machine learning task used to assign data to predefined categories or classes.

Important points:
1. It uses labelled training data.
2. The output is a category or class.
3. Common algorithms include decision trees, Naive Bayes, and logistic regression.
4. Classification is used for spam detection, disease prediction, and image recognition.

Example:
An email can be classified as Spam or Not Spam.""",

    "decision tree": """A decision tree is a machine learning model that makes decisions using a tree-like structure of conditions.

Important points:
1. The root is the starting decision.
2. Internal nodes represent tests or conditions.
3. Branches represent possible outcomes.
4. Leaf nodes represent the final prediction.

Example:
A decision tree can predict whether a person will buy a product based on age and income.""",

    "artificial intelligence": """Artificial Intelligence, or AI, is the field of computer science concerned with creating systems that can perform tasks that normally require human intelligence.

Important points:
1. AI can process information and identify patterns.
2. Machine learning is a major area of AI.
3. AI is used in chatbots, recommendation systems, robotics, and computer vision.
4. Generative AI can create text, images, code, and other content.

Example:
A chatbot that answers questions using an AI model is an example of AI."""
}


def _find_builtin_explanation(topic: str):
    topic_clean = topic.lower().strip()

    if topic_clean in BUILT_IN_EXPLANATIONS:
        return BUILT_IN_EXPLANATIONS[topic_clean]

    for key, answer in BUILT_IN_EXPLANATIONS.items():
        if key in topic_clean or topic_clean in key:
            return answer

    return None


def _local_explanation(topic: str) -> str:
    global _local_tokenizer, _local_model

    if _local_tokenizer is None or _local_model is None:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

        model_name = os.getenv(
            "LOCAL_EXPLANATION_MODEL",
            "google/flan-t5-small"
        )

        print("Loading small local AI model...")

        _local_tokenizer = AutoTokenizer.from_pretrained(model_name)
        _local_model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    prompt = (
        f"Explain {topic} for a college computer science beginner. "
        "Give a clear definition, three important points, and one simple example."
    )

    inputs = _local_tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=256
    )

    outputs = _local_model.generate(
        **inputs,
        max_new_tokens=150,
        num_beams=4,
        early_stopping=True,
        no_repeat_ngram_size=3
    )

    answer = _local_tokenizer.decode(
        outputs[0],
        skip_special_tokens=True
    ).strip()

    return answer


def _is_poor_answer(answer: str, topic: str) -> bool:
    if not answer:
        return True

    if len(answer.split()) < 8:
        return True

    bad_phrases = [
        "diffraction",
        "an diffraction",
        "prefix - a diffraction",
        "function - an diffraction"
    ]

    answer_lower = answer.lower()

    if any(phrase in answer_lower for phrase in bad_phrases):
        return True

    topic_words = [
        word.lower()
        for word in re.findall(r"[a-zA-Z]+", topic)
        if len(word) > 3
    ]

    if topic_words and not any(word in answer_lower for word in topic_words):
        return True

    return False


def explain_topic(topic: str) -> str:

    # 1. Try Gemini first.
    try:
        result = generate_text(
            f"Explain {topic} in simple language for a beginner. "
            f"Include a definition, key points, and an example."
        )

        if result:
            return result

    except Exception as e:
        print(f"Gemini unavailable: {e}")

    # 2. Try the local AI model.
    try:
        print("Using small local AI model...")

        result = _local_explanation(topic)

        if not _is_poor_answer(result, topic):
            return result

        print("Local AI answer was not reliable.")

    except Exception as e:
        print(f"Local AI unavailable: {e}")

    # 3. Use reliable built-in educational content.
    builtin = _find_builtin_explanation(topic)

    if builtin:
        print("Using built-in educational explanation...")
        return builtin

    # 4. Final generic fallback.
    return (
        f"{topic} is an important computer science topic. "
        "Please provide the topic with more details so that a suitable "
        "beginner-friendly explanation can be generated."
    )
def explain_topic(topic: str) -> str:

    # 1. Try Gemini first.
    try:
        result = generate_text(
            f"Explain {topic} in simple language for a beginner. "
            f"Include a definition, key points, and an example."
        )

        if result:
            return result

    except Exception as e:
        print(f"Gemini unavailable: {e}")

    # 2. Use reliable built-in explanations for known topics.
    builtin = _find_builtin_explanation(topic)

    if builtin:
        print("Using built-in educational explanation...")
        return builtin

    # 3. For unknown topics, try the local AI model.
    try:
        print("Using small local AI model...")

        result = _local_explanation(topic)

        if not _is_poor_answer(result, topic):
            return result

    except Exception as e:
        print(f"Local AI unavailable: {e}")

    # 4. Final fallback.
    return (
        f"{topic} is an important computer science topic. "
        "Please provide more details about the topic."
    )
