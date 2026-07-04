import logging

from fastapi import APIRouter, HTTPException

from api.schemas import QuizResult, QuizSubmission


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tools/quiz", tags=["quiz"])


@router.post("/submit", response_model=QuizResult)
async def submit_quiz(submission: QuizSubmission):
    logger.info("Received submission for quiz_id: %s", submission.quiz_id)

    total_questions = len(submission.questions)
    if total_questions == 0:
        raise HTTPException(status_code=400, detail="Không có câu hỏi nào trong bài nộp.")

    correct_count = 0
    results = {}
    for question in submission.questions:
        user_answer_index = submission.answers.get(question.id)
        is_correct = user_answer_index == question.correct_answer_index
        results[question.id] = is_correct
        if is_correct:
            correct_count += 1

    score = (correct_count / total_questions) * 100
    logger.info(
        "Graded quiz %s: Score %.2f%% (%s/%s)",
        submission.quiz_id,
        score,
        correct_count,
        total_questions,
    )

    return QuizResult(
        quiz_id=submission.quiz_id,
        score=score,
        total_questions=total_questions,
        correct_count=correct_count,
        results=results,
        feedback=None,
    )
