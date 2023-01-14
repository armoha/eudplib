cf) 데큐의 순회 순서: 왼쪽 -> 오른쪽 (tail -> head)

## appendleft의 동작 (cf. tail이 왼쪽, head가 오른쪽)
1. 데큐가 가득 차있나? (head도 1칸 옮겨야한다)
check_wrap 실행 -> wrap_head -> wrap_tail -> 마무리
2. 데큐에 빈 자리가 있나? (tail만 움직인다)
check_wrap 스킵 -> wrap_tail -> 마무리

0. 데큐 초기 상태
capacity = 7
self._length = 0
append_act + 16 = EPD(deque) + 87
appendleft_act + 16 = EPD(deque) + 87
jump + 4 = deque + 0
jumpleft + 4 = deque - 72
iter_init + 348 = EPD(deque) + 87
iter_init + 380 = deque - 72
[THx, x, x, x, x, x, x]

1. appendleft
check-wrap 스킵
wrap_tail 작동 {
    appendleft_act + 16 = EPD(deque) + 87 + 18 * 7
    jumpleft + 4 = deque + 72 * 6
    iter_init + 348 = EPD(deque) + 87 + 18 * 7
    iter_init + 380 = deque + 72 * 6
}
마무리 {
    appendleft_act + 16 = EPD(deque) + 87 + 18 * 6
    jumpleft + 4 = deque + 72 * 5
    appendleft_act 실행
    self._length = 1
    iter_init + 348 = EPD(deque) + 87 + 18 * 6
    iter_init + 380 = deque + 72 * 5
} [Hx, x, x, x, x, x, T1]

2. appendleft
check-wrap 스킵
wrap_tail 스킵
마무리 {
    appendleft_act + 16 = EPD(deque) + 87 + 18 * 5
    jumpleft + 4 = deque + 72 * 4
    appendleft_act 실행
    self._length = 2
    iter_init + 348 = EPD(deque) + 87 + 18 * 5
    iter_init + 380 = deque + 72 * 4
} [Hx, x, x, x, x, T2, 1]

3. appendleft
check-wrap 스킵
wrap_tail 스킵
마무리 {
    appendleft_act + 16 = EPD(deque) + 87 + 18 * 4
    jumpleft + 4 = deque + 72 * 3
    appendleft_act 실행
    self._length = 3
    iter_init + 348 = EPD(deque) + 87 + 18 * 4
    iter_init + 380 = deque + 72 * 3
} [Hx, x, x, x, T3, 2, 1]

4. appendleft
check-wrap 스킵
wrap_tail 스킵
마무리 {
    appendleft_act + 16 = EPD(deque) + 87 + 18 * 3
    jumpleft + 4 = deque + 72 * 2
    appendleft_act 실행
    self._length = 4
    iter_init + 348 = EPD(deque) + 87 + 18 * 3
    iter_init + 380 = deque + 72 * 2
} [Hx, x, x, T4, 3, 2, 1]

5. appendleft
check-wrap 스킵
wrap_tail 스킵
마무리 {
    appendleft_act + 16 = EPD(deque) + 87 + 18 * 2
    jumpleft + 4 = deque + 72 * 1
    appendleft_act 실행
    self._length = 5
    iter_init + 348 = EPD(deque) + 87 + 18 * 2
    iter_init + 380 = deque + 72 * 1
} [Hx, x, T5, 4, 3, 2, 1]

6. appendleft
check-wrap 스킵
wrap_tail 스킵
마무리 {
    appendleft_act + 16 = EPD(deque) + 87 + 18 * 1
    jumpleft + 4 = deque + 0
    appendleft_act 실행
    self._length = 6
    iter_init + 348 = EPD(deque) + 87 + 18 * 1
    iter_init + 380 = deque + 0
} [Hx, T6, 5, 4, 3, 2, 1]

7. appendleft
check-wrap 스킵
wrap_tail 스킵
마무리 {
    appendleft_act + 16 = EPD(deque) + 87
    jumpleft + 4 = deque - 72
    appendleft_act 실행
    self._length = 7
    iter_init + 348 = EPD(deque) + 87
    iter_init + 380 = deque - 72
} [HT7, 6, 5, 4, 3, 2, 1]

8. appendleft
check-wrap 작동 {
    append_act + 16 = EPD(deque) + 87 - 18
    jump + 4 = deque - 72
    self._length = 6
}
wrap_head 작동 {
    append_act + 16 = EPD(deque) + 87 + 18 * 6
    jump + 4 = deque + 72 * 6
}
wrap_tail 작동 {
    appendleft_act + 16 = EPD(deque) + 87 + 18 * 7
    jumpleft + 4 = deque + 72 * 6
    iter_init + 348 = EPD(deque) + 87 + 18 * 7
    iter_init + 380 = deque + 72 * 6
}
마무리 {
    appendleft_act + 16 = EPD(deque) + 87 + 18 * 6
    jumpleft + 4 = deque + 72 * 5
    appendleft_act 실행
    self._length = 7
    iter_init + 348 = EPD(deque) + 87 + 18 * 6
    iter_init + 380 = deque + 72 * 5
} [H7, 6, 5, 4, 3, 2, T8]

9. appendleft
check-wrap 작동 {
    append_act + 16 = EPD(deque) + 87 + 18 * 5
    jump + 4 = deque + 72 * 5
    self._length = 6
}
wrap_head 스킵
wrap_tail 스킵
마무리 {
    appendleft_act + 16 = EPD(deque) + 87 + 18 * 5
    jumpleft + 4 = deque + 72 * 4
    appendleft_act 실행
    self._length = 7
    iter_init + 348 = EPD(deque) + 87 + 18 * 5
    iter_init + 380 = deque + 72 * 4
} [H7, 6, 5, 4, 3, T9, 8]

## pop의 동작 (cf. tail이 왼쪽, head가 오른쪽)
### 데큐가 비어있는지 체크하지 않는다!
head비교 -> jump -> 데큐 -> retpoint

0. 데큐 초기 상태
capacity = 7
self._length = 0
append_act + 16 = EPD(deque) + 87
appendleft_act + 16 = EPD(deque) + 87
jump + 4 = deque + 0
jumpleft + 4 = deque - 72
iter_init + 348 = EPD(deque) + 87
iter_init + 380 = deque - 72
[THx, x, x, x, x, x, x]

7. appendleft
check-wrap 스킵
wrap_tail 스킵
마무리 {
    appendleft_act + 16 = EPD(deque) + 87
    jumpleft + 4 = deque - 72
    appendleft_act 실행
    self._length = 7
    iter_init + 348 = EPD(deque) + 87
    iter_init + 380 = deque - 72
} [HT7, 6, 5, 4, 3, 2, 1]

1. _pop
head비교 작동 {
    append_act + 16 = EPD(deque) + 87 + 18 * 7
    jump + 4 = deque + 72 * 7
}
jump 작동 {
    append_act + 16 = EPD(deque) + 87 + 18 * 6
    jump + 4 = deque + 72 * 6
    self._length = 6
}
데큐 트리거 작동 { 1을 꺼내온다 }

2. _pop
head비교 스킵
jump 작동 {
    append_act + 16 = EPD(deque) + 87 + 18 * 5
    jump + 4 = deque + 72 * 5
    self._length = 5
}
데큐 트리거 작동 { 2를 꺼내온다 }

## popleft의 동작 (cf. tail이 왼쪽, head가 오른쪽)
### 데큐가 비어있는지 체크하지 않는다!
jumpleft -> 데큐 -> wraparound

0. 데큐 초기 상태
capacity = 7
self._length = 0
append_act + 16 = EPD(deque) + 87
appendleft_act + 16 = EPD(deque) + 87
jump + 4 = deque + 0
jumpleft + 4 = deque - 72
iter_init + 348 = EPD(deque) + 87
iter_init + 380 = deque - 72
[THx, x, x, x, x, x, x]

7. appendleft
check-wrap 스킵
wrap_tail 스킵
마무리 {
    appendleft_act + 16 = EPD(deque) + 87
    jumpleft + 4 = deque - 72
    appendleft_act 실행
    self._length = 7
    iter_init + 348 = EPD(deque) + 87
    iter_init + 380 = deque - 72
} [HT7, 6, 5, 4, 3, 2, 1]

1. popleft
jumpleft 작동 {
    appendleft_act + 16 = EPD(deque) + 87 + 18
    jumpleft + 4 = deque + 0
    iter_init + 348 = EPD(deque) + 87 + 18
    iter_init + 380 = deque + 0
    self._length = 6
}
데큐 트리거 작동 { 6을 꺼내온다 }
wraparound 스킵