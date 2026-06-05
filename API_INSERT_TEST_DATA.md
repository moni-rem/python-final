# API Insert Test Data

This page contains ready-to-use POST payloads for the supported API endpoints in this project.

## Authentication

1. Obtain JWT access token:

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"adminpass"}'
```

2. Use the response access token in the header for authenticated POST requests:

```bash
-H "Authorization: Bearer <access_token>"
```

---

## 1) POST /api/users/

Requires admin access.

```bash
curl -X POST http://127.0.0.1:8000/api/users/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '<JSON_PAYLOAD>'
```

### User payloads

1.
```json
{ "username": "student1", "email": "student1@example.com", "first_name": "Student", "last_name": "One", "role": "student", "password": "TestPass123!" }
```
2.
```json
{ "username": "student2", "email": "student2@example.com", "first_name": "Student", "last_name": "Two", "role": "student", "password": "TestPass123!" }
```
3.
```json
{ "username": "student3", "email": "student3@example.com", "first_name": "Student", "last_name": "Three", "role": "student", "password": "TestPass123!" }
```
4.
```json
{ "username": "student4", "email": "student4@example.com", "first_name": "Student", "last_name": "Four", "role": "student", "password": "TestPass123!" }
```
5.
```json
{ "username": "student5", "email": "student5@example.com", "first_name": "Student", "last_name": "Five", "role": "student", "password": "TestPass123!" }
```
6.
```json
{ "username": "instructor1", "email": "instructor1@example.com", "first_name": "Instructor", "last_name": "One", "role": "instructor", "password": "InstructorPass123!" }
```
7.
```json
{ "username": "instructor2", "email": "instructor2@example.com", "first_name": "Instructor", "last_name": "Two", "role": "instructor", "password": "InstructorPass123!" }
```
8.
```json
{ "username": "instructor3", "email": "instructor3@example.com", "first_name": "Instructor", "last_name": "Three", "role": "instructor", "password": "InstructorPass123!" }
```
9.
```json
{ "username": "instructor4", "email": "instructor4@example.com", "first_name": "Instructor", "last_name": "Four", "role": "instructor", "password": "InstructorPass123!" }
```
10.
```json
{ "username": "instructor5", "email": "instructor5@example.com", "first_name": "Instructor", "last_name": "Five", "role": "instructor", "password": "InstructorPass123!" }
```
11.
```json
{ "username": "admin2", "email": "admin2@example.com", "first_name": "Admin", "last_name": "Two", "role": "admin", "password": "AdminPass123!" }
```
12.
```json
{ "username": "admin3", "email": "admin3@example.com", "first_name": "Admin", "last_name": "Three", "role": "admin", "password": "AdminPass123!" }
```
13.
```json
{ "username": "admin4", "email": "admin4@example.com", "first_name": "Admin", "last_name": "Four", "role": "admin", "password": "AdminPass123!" }
```
14.
```json
{ "username": "admin5", "email": "admin5@example.com", "first_name": "Admin", "last_name": "Five", "role": "admin", "password": "AdminPass123!" }
```
15.
```json
{ "username": "student6", "email": "student6@example.com", "first_name": "Student", "last_name": "Six", "role": "student", "password": "TestPass123!" }
```
16.
```json
{ "username": "student7", "email": "student7@example.com", "first_name": "Student", "last_name": "Seven", "role": "student", "password": "TestPass123!" }
```
17.
```json
{ "username": "student8", "email": "student8@example.com", "first_name": "Student", "last_name": "Eight", "role": "student", "password": "TestPass123!" }
```
18.
```json
{ "username": "student9", "email": "student9@example.com", "first_name": "Student", "last_name": "Nine", "role": "student", "password": "TestPass123!" }
```
19.
```json
{ "username": "student10", "email": "student10@example.com", "first_name": "Student", "last_name": "Ten", "role": "student", "password": "TestPass123!" }
```
20.
```json
{ "username": "student11", "email": "student11@example.com", "first_name": "Student", "last_name": "Eleven", "role": "student", "password": "TestPass123!" }
```

---

## 2) POST /api/categories/

Requires authentication.

```bash
curl -X POST http://127.0.0.1:8000/api/categories/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '<JSON_PAYLOAD>'
```

### Category payloads

1.
```json
{ "name": "Programming", "description": "Courses about software development and coding." }
```
2.
```json
{ "name": "Data Science", "description": "Analytics, machine learning, and data engineering." }
```
3.
```json
{ "name": "Design", "description": "UI/UX, graphic design, and product design topics." }
```
4.
```json
{ "name": "Business", "description": "Business strategy, marketing, and entrepreneurship." }
```
5.
```json
{ "name": "Health & Wellness", "description": "Health, wellness, and personal growth courses." }
```
6.
```json
{ "name": "Finance", "description": "Accounting, investing, and personal finance." }
```
7.
```json
{ "name": "Language Learning", "description": "Foreign language and communication skills." }
```
8.
```json
{ "name": "Photography", "description": "Photography, editing, and visual storytelling." }
```
9.
```json
{ "name": "Music", "description": "Music theory, instruments, and production." }
```
10.
```json
{ "name": "Writing", "description": "Creative writing, copywriting, and storytelling." }
```
11.
```json
{ "name": "Career Development", "description": "Job skills, resume writing, and interview prep." }
```
12.
```json
{ "name": "Education", "description": "Teaching methods, learning design, and training." }
```
13.
```json
{ "name": "Science", "description": "Physics, chemistry, biology, and science fundamentals." }
```
14.
```json
{ "name": "Arts", "description": "Painting, drawing, and creative arts." }
```
15.
```json
{ "name": "Lifestyle", "description": "Lifestyle, travel, and personal development." }
```
16.
```json
{ "name": "Technology", "description": "Tech trends, tools, and modern software systems." }
```
17.
```json
{ "name": "Engineering", "description": "Engineering fundamentals and applied engineering skills." }
```
18.
```json
{ "name": "Mathematics", "description": "Math concepts, statistics, and quantitative reasoning." }
```
19.
```json
{ "name": "Leadership", "description": "Leadership, management, and team building." }
```
20.
```json
{ "name": "Personal Development", "description": "Motivation, productivity, and self-improvement." }
```

---

## 3) POST /api/quiz-attempts/

Requires authentication. The payload must include `quiz_id`.

```bash
curl -X POST http://127.0.0.1:8000/api/quiz-attempts/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '<JSON_PAYLOAD>'
```

### Quiz attempt payloads

1.
```json
{ "quiz_id": 1, "text_response": "Answer: 4" }
```
2.
```json
{ "quiz_id": 1, "text_response": "Answer: POST" }
```
3.
```json
{ "quiz_id": 2, "text_response": "GET is for reading data." }
```
4.
```json
{ "quiz_id": 2, "text_response": "POST is used to create new records." }
```
5.
```json
{ "quiz_id": 1, "text_response": "The correct result is 4." }
```
6.
```json
{ "quiz_id": 2, "text_response": "GET requests should not change server state." }
```
7.
```json
{ "quiz_id": 1, "text_response": "My essay response is: 4." }
```
8.
```json
{ "quiz_id": 2, "text_response": "Use POST for submission forms." }
```
9.
```json
{ "quiz_id": 1, "text_response": "The response is numeric: 4." }
```
10.
```json
{ "quiz_id": 2, "text_response": "A GET request fetches resources." }
```
11.
```json
{ "quiz_id": 1, "text_response": "I choose answer 4." }
```
12.
```json
{ "quiz_id": 2, "text_response": "POST creates, PUT updates." }
```
13.
```json
{ "quiz_id": 1, "text_response": "Final answer: 4." }
```
14.
```json
{ "quiz_id": 2, "text_response": "Query parameters are often used with GET." }
```
15.
```json
{ "quiz_id": 1, "text_response": "I believe the answer is 4." }
```
16.
```json
{ "quiz_id": 2, "text_response": "POST sends a request body." }
```
17.
```json
{ "quiz_id": 1, "text_response": "The computed output is four." }
```
18.
```json
{ "quiz_id": 2, "text_response": "GET should be safe and idempotent." }
```
19.
```json
{ "quiz_id": 1, "text_response": "This is a quiz submission." }
```
20.
```json
{ "quiz_id": 2, "text_response": "This is a second quiz attempt." }
```

---

## Notes

- `POST /api/users/` is admin-only.
- `POST /api/categories/` and `POST /api/quiz-attempts/` require authentication.
- The server must already have `quiz` records for the `quiz_id` values used in the quiz attempt examples.
- If you need direct insert support for other endpoints such as `courses`, `modules`, `lessons`, `assignments`, `submissions`, `discussions`, or `comments`, I can patch serializers and viewsets to accept those payloads.
