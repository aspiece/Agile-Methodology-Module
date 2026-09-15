# Eight-Week CTE Module Template

This repository turns designer-approved standards and resources into an accessible eight-lesson student course. It preserves the visual treatment and interaction patterns established in the AI Literacy course while keeping the instructional content neutral and replaceable.

## Fixed lesson structure

Every module contains eight lessons. Each lesson uses these semantic step numbers:

- `.1` Lesson overview — required
- `.2` Connect and Learn — required, one primary video or equivalent resource, and a check for understanding
- `.3` Additional instruction or guided practice — optional; includes a check unless an approved override is recorded
- `.4` Additional instruction or guided practice — optional; includes a check unless an approved override is recorded
- Apply Your Learning — required; takes the next available step number
- Lesson assessment handoff — required; follows the application with no gap

The progress indicator counts only the steps that exist. Optional steps are not created merely to fill space.

## Instructional defaults

- Audience: grades 11–12 CTE students
- Student-facing reading target: grades 7–8
- Weekly learner time: approximately 50 minutes, including the lesson assessment
- Accessibility target: WCAG 2.2 AA and Universal Design for Learning
- CTE application: the application step provides meaningful program-specific practice when the module is designated as CTE
- Assessment location: learners return to their course; the public site does not collect student information
- Mastery: 80%, up to three attempts, highest score retained, questions and appropriate choices shuffled, correct answers hidden, and results released by the instructor

## Designer workflow

1. Copy this repository.
2. Enter standards, approved resources, and requirements in `resources/Module_Resource_Collection.xlsx`.
3. Ask Codex to analyze the workbook and draft the Eight-Lesson Blueprint.
4. Review and approve the proposed topics, objectives, sequence, optional steps, pacing, and applications.
5. Ask Codex to draft checks for understanding and assessments in the workbook.
6. Review and approve the questions.
7. Export the workbook to `content/course.json` and build the site.
8. Preview and validate before publishing.

## Build locally

The checked-in `content/course.json` contains neutral placeholders so the template can be previewed immediately.

```powershell
python tools/build_course.py
python tools/validate_course.py
python -m http.server 8765
```

Open `http://127.0.0.1:8765/`.

## Content boundaries

- The designer supplies authoritative standards and selects trustworthy resources.
- Codex extracts, organizes, and rewrites learner-relevant information.
- Codex keeps source locators for instructional claims and assessment answers.
- Unsupported additions and unresolved conflicts are flagged for review.
- Graphics are included only when they improve learning. No empty image placeholders appear in generated lessons.
