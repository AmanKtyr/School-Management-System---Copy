function viewExamDetails(examId) {
    if (!examId || examId === 'undefined') {
        console.error('Invalid exam ID');
        return;
    }
    
    window.location.href = `/exams/exams/${examId}?session=${sessionId}&term=${termId}&exam_type=${examTypeId}&status=${status}`;
}