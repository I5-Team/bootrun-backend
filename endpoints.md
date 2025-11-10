● 전체 엔드포인트를 기능별로 묶어서 각각 필수/선택/추가로 표시하여 정리하겠습니다.

  ---
  전체 엔드포인트 분류 (기능별)

  🔐 인증 (Authentication) - /auth

  1. POST /auth/register - 이메일 회원가입 [필수] 
  2. POST /auth/login - 이메일 로그인 [필수] 
  3. POST /auth/logout - 로그아웃 [필수] 
  4. POST /auth/email/verification/request - 이메일 인증 요청 [필수] 
  5. POST /auth/email/verification/confirm - 이메일 인증 확인 [필수] 
  6. POST /auth/social/google - Google 소셜 로그인 [선택] 
  7. POST /auth/social/github - Github 소셜 로그인 [선택] 
  8. POST /auth/refresh - 토큰 갱신 [추가] 
  9. GET /auth/verify - 토큰 검증 [추가] 
  10. POST /auth/password/reset/request - 비밀번호 재설정 요청 [추가]
  11. POST /auth/password/reset/confirm - 비밀번호 재설정 확인 [추가]

  ---
  👤 사용자 (User) - /users

  12. GET /users/me - 내 프로필 조회 [필수]
  13. PATCH /users/me - 프로필 수정 (이름, 성별, 생년월일) [필수]
  14. DELETE /users/me - 회원 탈퇴 [필수]
  15. GET /users/{user_id} - 특정 사용자 프로필 조회 [추가]
  16. POST /users/me/profile-image - 프로필 이미지 업로드 [추가]
  17. DELETE /users/me/profile-image - 프로필 이미지 삭제 [추가]
  18. POST /users/me/change-password - 비밀번호 변경 [추가]
  19. POST /users/me/change-email/request - 이메일 변경 요청 [추가]
  20. POST /users/me/change-email/confirm - 이메일 변경 확인 [추가]
  21. GET /users/me/activities - 내 활동 내역 [추가]
  22. GET /users/me/notifications - 내 알림 목록 [선택] (학습 기간 만료 알림)
  23. PATCH /users/me/notifications/{notification_id}/read - 알림 읽음 처리 [추가]
  24. POST /users/me/notifications/read-all - 모든 알림 읽음 처리 [추가]
  25. POST /users/restore - 계정 복구 (탈퇴 후 30일 이내) [추가]

  ---
  📚 강의 (Course) - /courses

  26. GET /courses - 전체 강의 목록 조회 (필터링, 카테고리별) [필수]
  27. GET /courses/{course_id} - 강의 상세 조회 [필수]
  28. GET /courses/{course_id}/chapters - 챕터 목록 조회 [필수]
  29. GET /courses/{course_id}/chapters/{chapter_id}/lectures - 강의 영상 목록 조회
  [필수]
  30. GET /courses/metadata - 강의 필터링 메타데이터 조회 [추가]
  31. GET /courses/{course_id}/chapters/{chapter_id} - 특정 챕터 상세 조회 [추가]
  32. GET /courses/{course_id}/chapters/{chapter_id}/lectures/{lecture_id} - 특정 강의       
  영상 상세 조회 [추가]

  ---
  🎓 수강 등록 및 학습 진행 (Enrollment) - /enrollments

  33. POST /enrollments - 수강 등록 [필수]
  34. GET /enrollments/my - 내 수강 목록 조회 [필수]
  35. POST /enrollments/progress - 학습 진행 생성 [필수]
  36. PATCH /enrollments/progress/lectures/{lecture_id} - 학습 진행 업데이트 [필수]
  37. GET /enrollments/progress/course/{course_id} - 강의별 학습 진행 조회 [필수]
  38. GET /enrollments/{enrollment_id} - 수강 상세 조회 [추가]
  39. DELETE /enrollments/{enrollment_id} - 수강 취소 [추가]
  40. GET /enrollments/dashboard - 학습자 대시보드 [추가]
  41. GET /enrollments/stats - 학습 통계 [추가]
  42. GET /enrollments/progress/lecture/{lecture_id} - 강의 영상별 진행 조회 [추가]

  ---
  🎯 미션 (Mission) - /missions

  43. GET /missions/courses/{course_id} - 강의별 미션 목록 [선택]
  44. GET /missions/{mission_id} - 미션 상세 조회 [선택]
  45. POST /missions/submissions - 미션 제출 [선택]
  46. GET /missions/{mission_id}/submissions - 미션 제출 내역 [선택]
  47. GET /missions/{mission_id}/progress - 미션 진행 현황 [선택]
  48. GET /missions/{mission_id}/stats - 미션 통계 (수강생 전체) [추가]

  ---
  💳 결제 (Payment) - /payments

  49. POST /payments - 결제 생성 [필수]
  50. POST /payments/{payment_id}/confirm - 결제 확인 [필수]
  51. GET /payments - 결제 목록 조회 [필수]
  52. GET /payments/{payment_id} - 결제 상세 조회 [선택] (마이페이지 결제 내역)
  53. POST /payments/{payment_id}/cancel - 결제 취소 (완료 전) [추가]
  54. GET /payments/{payment_id}/refund-check - 환불 가능 여부 확인 [추가]

  ---
  💸 환불 (Refund) - /payments/refunds

  55. POST /payments/refunds - 환불 요청 [필수]
  56. GET /payments/refunds/my - 내 환불 요청 목록 [추가]
  57. GET /payments/refunds/{refund_id} - 환불 상세 조회 [추가]
  58. DELETE /payments/refunds/{refund_id} - 환불 요청 취소 [추가]

  ---
  🎟️ 쿠폰 (Coupon) -  /coupons

  59. GET /coupons - 쿠폰 목록 조회 [추가]
  60. GET /coupons/{coupon_id} - 쿠폰 상세 조회 [추가]
  61. POST /coupons/validate - 쿠폰 유효성 검증 [추가]
  62. GET /coupons/my - 내 쿠폰 목록 [추가]

  ---
  🎓 수료증 (Certificate) - /certificates

  63. POST /certificates - 수료증 발급 [선택]
  64. GET /certificates/my - 내 수료증 목록 [선택]
  65. GET /certificates/{certificate_id} - 수료증 상세 조회 [선택]
  66. POST /certificates/{certificate_id}/pdf - 수료증 PDF 생성 [선택]
  67. POST /certificates/verify - 수료증 진위 확인 [선택]
  68. POST /certificates/check-eligibility - 수료 조건 확인 [추가]
  69. DELETE /certificates/{certificate_id} - 수료증 삭제 (관리자) [추가]

  ---
  💬 학습 Q&A (Question) - /questions

  70. GET /questions - 질문 목록 조회 [추가]
  71. GET /questions/{question_id} - 질문 상세 조회 [추가]
  72. POST /questions - 질문 작성 [추가]
  73. PATCH /questions/{question_id} - 질문 수정 [추가]
  74. DELETE /questions/{question_id} - 질문 삭제 [추가]
  75. POST /questions/{question_id}/comments - 답변 작성 [추가]
  76. PATCH /questions/{question_id}/comments/{comment_id} - 답변 수정 [추가]
  77. DELETE /questions/{question_id}/comments/{comment_id} - 답변 삭제 [추가]
  78. GET /questions/my/questions - 내가 작성한 질문 [추가]
  79. GET /questions/my/comments - 내가 작성한 답변 [추가]

  ---
  📊 관리자 - 대시보드 (Admin Dashboard) - /admin/dashboard

  80. GET /admin/dashboard/stats - 대시보드 통계 [필수]
  81. GET /admin/dashboard/daily-stats - 일별 통계 (접속자, 조회수) [필수]
  82. GET /admin/dashboard/revenue-stats - 매출 통계 [필수]
  83. GET /admin/dashboard/course-stats - 강의별 통계 [필수]
  84. GET /admin/dashboard/category-stats - 카테고리별 통계 [추가]
  85. GET /admin/dashboard/settings - 시스템 설정 조회 [추가]
  86. PATCH /admin/dashboard/settings - 시스템 설정 수정 [추가]

  ---
  👥 관리자 - 사용자 관리 (Admin Users) - /admin/users

  87. GET /admin/users - 사용자 목록 조회 [필수]
  88. GET /admin/users/{user_id} - 사용자 상세 조회 [필수]
  89. GET /admin/users/{user_id}/learning-report - 사용자 학습 리포트 [선택]
  90. PATCH /admin/users/{user_id}/activate - 사용자 활성화 [추가]
  91. PATCH /admin/users/{user_id}/deactivate - 사용자 비활성화 [추가]
  92. DELETE /admin/users/{user_id} - 사용자 삭제 [추가]
  93. GET /admin/users/export - 사용자 목록 엑셀 내보내기 [추가]

  ---
  📚 관리자 - 강의 관리 (Admin Courses) - /admin/courses

  94. GET /admin/courses - 강의 목록 조회 [필수]
  95. POST /admin/courses - 강의 생성 [필수]
  96. PATCH /admin/courses/{course_id} - 강의 수정 [필수]
  97. DELETE /admin/courses/{course_id} - 강의 삭제 [필수]
  98. POST /admin/courses/{course_id}/chapters - 챕터 추가 [필수]
  99. PATCH /admin/courses/{course_id}/chapters/{chapter_id} - 챕터 수정 [필수]
  100. POST /admin/courses/{course_id}/chapters/{chapter_id}/lectures - 강의 영상 추가       
  [필수]
  101. PATCH /admin/courses/{course_id}/chapters/{chapter_id}/lectures/{lecture_id} -        
  강의 영상 수정 [필수]
  102. POST /admin/courses/{course_id}/publish - 강의 공개 [추가]
  103. POST /admin/courses/{course_id}/unpublish - 강의 비공개 [추가]
  104. GET /admin/courses/{course_id}/analytics - 강의 분석 [추가]
  105. POST /admin/courses/{course_id}/duplicate - 강의 복제 [추가]
  106. GET /admin/courses/export - 강의 목록 엑셀 내보내기 [추가]
  107. DELETE /admin/courses/{course_id}/chapters/{chapter_id} - 챕터 삭제 [추가]
  108. DELETE /admin/courses/{course_id}/chapters/{chapter_id}/lectures/{lecture_id} -       
  강의 영상 삭제 [추가]

  ---
  💳 관리자 - 결제 및 환불 관리 (Admin Payments) - /admin/payments

  109. GET /admin/payments - 결제 목록 조회 [필수]
  110. GET /admin/payments/export - 결제 내역 엑셀 다운로드 [필수]
  111. GET /admin/payments/refunds - 환불 목록 조회 [필수]
  112. PATCH /admin/payments/refunds/{refund_id} - 환불 승인/거절 [필수]
  113. GET /admin/payments/refunds/{refund_id} - 환불 상세 조회 [추가]
  114. GET /admin/payments/refunds/export - 환불 내역 엑셀 내보내기 [추가]

  ---
  🎟️ 관리자 - 쿠폰 관리 (Admin Coupons) -  /admin/coupons

  115. GET /admin/coupons - 쿠폰 목록 조회 [추가]
  116. GET /admin/coupons/{coupon_id} - 쿠폰 상세 조회 [추가]
  117. POST /admin/coupons - 쿠폰 생성 [추가]
  118. PATCH /admin/coupons/{coupon_id} - 쿠폰 수정 [추가]
  119. DELETE /admin/coupons/{coupon_id} - 쿠폰 삭제 [추가]

  ---
  🎯 관리자 - 미션 관리 (Admin Missions) - /admin/missions

  120. POST /admin/missions/courses/{course_id}/missions - 미션 생성 [선택]
  121. PATCH /admin/missions/{mission_id} - 미션 수정 [선택]
  122. DELETE /admin/missions/{mission_id} - 미션 삭제 [선택]

  ---
  📊 전체 통계

  | 분류  | 개수   |
  |-----|------|
  | 필수  | 39개  |
  | 선택  | 18개  |
  | 추가  | 65개  |
  | 총합  | 122개 |

  기능별 분류

  - 🔐 인증: 11개 (필수 5 + 선택 2 + 추가 4)
  - 👤 사용자: 14개 (필수 3 + 선택 1 + 추가 10)
  - 📚 강의: 7개 (필수 4 + 추가 3)
  - 🎓 수강/학습: 10개 (필수 5 + 추가 5)
  - 🎯 미션: 6개 (선택 5 + 추가 1)
  - 💳 결제: 6개 (필수 3 + 선택 1 + 추가 2)
  - 💸 환불: 4개 (필수 1 + 추가 3)
  - 🎟️ 쿠폰: 4개 (추가 4)
  - 🎓 수료증: 7개 (선택 5 + 추가 2)
  - 💬 Q&A: 10개 (추가 10)
  - 📊 관리자 대시보드: 7개 (필수 4 + 추가 3)
  - 👥 관리자 사용자: 7개 (필수 2 + 선택 1 + 추가 4)
  - 📚 관리자 강의: 15개 (필수 8 + 추가 7)
  - 💳 관리자 결제: 6개 (필수 4 + 추가 2)
  - 🎟️ 관리자 쿠폰: 5개 (추가 5)
  - 🎯 관리자 미션: 3개 (선택 3)