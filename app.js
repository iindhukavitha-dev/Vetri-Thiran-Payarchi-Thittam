const task = document.getElementById("task");
const input = document.getElementById("input");
const submit = document.getElementById("submit");
const clear = document.getElementById("clear");

const status = document.getElementById("status");
const resultCard = document.getElementById("resultCard");
const result = document.getElementById("result");


let currentQuiz = [];


function setStatus(message) {
    status.textContent = message;
}


function showResultHTML(html) {
    result.innerHTML = html;
    resultCard.classList.remove("hidden");
}


function clearResult() {
    result.innerHTML = "";
    resultCard.classList.add("hidden");
    currentQuiz = [];
}


function escapeHTML(value) {
    const div = document.createElement("div");
    div.textContent = String(value);
    return div.innerHTML;
}


clear.addEventListener("click", () => {

    input.value = "";

    setStatus("");

    clearResult();

});


task.addEventListener("change", () => {

    const selectedTask = task.value;

    clearResult();

    if (selectedTask === "qa") {

        input.placeholder =
            "Example: Which is the largest ocean?";

    } else if (selectedTask === "explain") {

        input.placeholder =
            "Example: Explain inheritance in Java";

    } else if (selectedTask === "quiz") {

        input.placeholder =
            "Example: Python programming basics";

    } else if (selectedTask === "summarize") {

        input.placeholder =
            "Paste the lesson or text you want to summarize";

    } else if (selectedTask === "learn") {

        input.placeholder =
            "Example: I want to learn Python from beginner to advanced";

    }

});


submit.addEventListener("click", async () => {

    const selectedTask = task.value;
    const text = input.value.trim();


    if (!text) {

        setStatus("Please enter something first.");

        input.focus();

        return;

    }


    submit.disabled = true;

    clearResult();

    setStatus("Generating...");


    try {

        let url;
        let body;


        if (selectedTask === "qa") {

            url = "/qa";

            body = {
                question: text
            };

        } else if (selectedTask === "explain") {

            url = "/explain";

            body = {
                text: text
            };

        } else if (selectedTask === "quiz") {

            url = "/quiz";

            body = {
                text: text,
                count: 3
            };

        } else if (selectedTask === "summarize") {

            url = "/summarize";

            body = {
                text: text
            };

        } else if (selectedTask === "learn") {

            url = "/learn/recommendations";

            body = {
                text: text
            };

        }


        const response = await fetch(url, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(body)

        });


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail || "Something went wrong."
            );

        }


        if (selectedTask === "qa") {

            showResultHTML(
                `<div class="answer">
                    ${escapeHTML(data.answer)}
                </div>`
            );

        } else if (selectedTask === "explain") {

            showResultHTML(
                `<div class="answer">
                    ${escapeHTML(data.explanation)}
                </div>`
            );

        } else if (selectedTask === "quiz") {

            currentQuiz = Array.isArray(data.quiz)
                ? data.quiz
                : [];

            if (currentQuiz.length === 0) {
                throw new Error("No quiz questions were generated.");
            }

            showQuiz(currentQuiz);

        } else if (selectedTask === "summarize") {

            showResultHTML(
                `<div class="answer">
                    ${escapeHTML(data.summary)}
                </div>`
            );

        } else if (selectedTask === "learn") {

            showResultHTML(
                `<div class="answer">
                    ${escapeHTML(
                        typeof data.recommendations === "string"
                            ? data.recommendations
                            : JSON.stringify(
                                data.recommendations,
                                null,
                                2
                            )
                    )}
                </div>`
            );

        }


        setStatus(
            selectedTask === "quiz"
                ? "Quiz ready!"
                : "Done!"
        );


    } catch (error) {

        console.error(error);

        setStatus(
            "Error: " + error.message
        );

        showResultHTML(
            `<div class="error">
                Unable to generate a response.<br><br>
                ${escapeHTML(error.message)}
            </div>`
        );


    } finally {

        submit.disabled = false;

    }

});


function showQuiz(quiz) {

    let html = "";

    html += `
        <div class="quiz-container">

            <h2>Quiz</h2>

            <p class="quiz-instruction">
                Select one answer for each question.
                The correct answers will be shown after you submit.
            </p>
    `;


    quiz.forEach((question, index) => {

        html += `
            <div class="quiz-question">

                <h3>
                    Question ${index + 1}
                </h3>

                <p class="question-text">
                    ${escapeHTML(question.question)}
                </p>

                <div class="quiz-options">
        `;


        question.options.forEach((option, optionIndex) => {

            const inputId =
                `question-${index}-option-${optionIndex}`;


            html += `
                <label
                    class="quiz-option"
                    for="${inputId}"
                >

                    <input
                        type="radio"
                        id="${inputId}"
                        name="question-${index}"
                        value="${escapeHTML(option)}"
                    >

                    <span>
                        ${escapeHTML(option)}
                    </span>

                </label>
            `;

        });


        html += `
                </div>

            </div>
        `;

    });


    html += `

            <button
                type="button"
                id="submitQuiz"
                class="quiz-submit"
            >
                Submit Quiz
            </button>

            <div
                id="quizResult"
                class="quiz-result"
            ></div>

        </div>
    `;


    showResultHTML(html);


    const submitQuiz =
        document.getElementById("submitQuiz");


    submitQuiz.addEventListener(
        "click",
        submitQuizAnswers
    );

}


function submitQuizAnswers() {

    let score = 0;

    let answered = 0;


    const resultContainer =
        document.getElementById("quizResult");


    let reviewHTML = "";


    currentQuiz.forEach((question, index) => {

        const selected =
            document.querySelector(
                `input[name="question-${index}"]:checked`
            );


        let userAnswer = "";

        if (selected) {

            userAnswer = selected.value;

            answered++;

        }


        const correctAnswer =
            question.answer;


        const isCorrect =
            userAnswer === correctAnswer;


        if (isCorrect) {

            score++;

        }


        reviewHTML += `

            <div class="quiz-review
                ${isCorrect ? "correct" : "incorrect"}">

                <h3>
                    Question ${index + 1}
                </h3>

                <p>
                    <strong>
                        ${escapeHTML(question.question)}
                    </strong>
                </p>

                <p>
                    Your answer:
                    <strong>
                        ${
                            userAnswer
                                ? escapeHTML(userAnswer)
                                : "Not answered"
                        }
                    </strong>
                </p>

                <p>
                    Correct answer:
                    <strong>
                        ${escapeHTML(correctAnswer)}
                    </strong>
                </p>

                <p>
                    ${
                        isCorrect
                            ? "✓ Correct"
                            : "✗ Incorrect"
                    }
                </p>

                <p>
                    <strong>Explanation:</strong><br>
                    ${escapeHTML(question.explanation)}
                </p>

            </div>

        `;

    });


    const total = currentQuiz.length;

    const percentage =
        Math.round((score / total) * 100);


    resultContainer.innerHTML = `

        <div class="score-box">

            <h2>
                Quiz Completed!
            </h2>

            <p class="score">
                Score: ${score} / ${total}
            </p>

            <p>
                Percentage: ${percentage}%
            </p>

            <p>
                Answered: ${answered} / ${total}
            </p>

        </div>

        <h2>
            Answer Review
        </h2>

        ${reviewHTML}

    `;


    document
        .getElementById("submitQuiz")
        .disabled = true;


    document
        .querySelectorAll(".quiz-option")
        .forEach(option => {

            option.style.pointerEvents = "none";

        });


    setStatus("Quiz submitted!");

}