def count_cor_wng_ans(student_tests):
    correct_ans = 0
    wrong_ans = 0

    for test in student_tests:

        if test.result_answer_1 == 1:
            correct_ans += 1
        if test.result_answer_2 == 1:
            correct_ans += 1
        if test.result_answer_3 == 1:
            correct_ans += 1
        if test.result_answer_4 == 1:
            correct_ans += 1
        if test.result_answer_5 == 1:
            correct_ans += 1

        if test.result_answer_1 == 0:
            wrong_ans += 1
        if test.result_answer_2 == 0:
            wrong_ans += 1
        if test.result_answer_3 == 0:
            wrong_ans += 1
        if test.result_answer_4 == 0:
            wrong_ans += 1
        if test.result_answer_5 == 0:
            wrong_ans += 1
    return [correct_ans, wrong_ans]
