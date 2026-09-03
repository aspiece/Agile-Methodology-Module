from __future__ import annotations

import html
import json
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "course.json"
LESSONS = ROOT / "lessons"


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def paragraphs(items: list[str] | None) -> str:
    return "".join(f"<p>{esc(item)}</p>" for item in (items or []) if item)


def navigation(lessons: list[dict], current: int | None = None, prefix: str = "") -> str:
    links = []
    for lesson in lessons:
        attrs = ' aria-current="page"' if lesson["number"] == current else ""
        links.append(f'<a href="{prefix}lessons/lesson-{lesson["number"]}.html"{attrs}>Lesson {lesson["number"]}</a>')
    return "".join(links)


def resource_lookup(data: dict) -> dict[str, dict]:
    return {str(item.get("id")): item for item in data.get("resources", []) if item.get("id")}


def render_resources(ids: list[str], resources: dict[str, dict]) -> str:
    cards = []
    for resource_id in ids or []:
        resource = resources.get(str(resource_id))
        if not resource:
            continue
        title = esc(resource.get("title") or "Learning resource")
        url = esc(resource.get("url"))
        transcript = esc(resource.get("transcript_url"))
        description = esc(resource.get("description"))
        actions = []
        if url:
            actions.append(f'<a href="{url}">Open {title}</a>')
        if transcript:
            actions.append(f'<a href="{transcript}">Open transcript</a>')
        cards.append(
            '<section class="resource-card">'
            f'<h3>{title}</h3>'
            f'<p>{description}</p>'
            f'<div class="resource-actions">{"".join(actions)}</div>'
            '</section>'
        )
    return "".join(cards)


def render_question(check: dict | None, lesson_number: int, step_number: str) -> str:
    if not check:
        reason = esc(check.get("override_reason")) if isinstance(check, dict) else ""
        note = f" Designer decision: {reason}" if reason else ""
        return f'<p class="placeholder-note">A check for understanding has not been approved for this step.{note}</p>'
    choices = []
    input_type = "checkbox" if check.get("type") == "multiple_select" else "radio"
    name = f"check-{lesson_number}-{step_number}"
    for choice in check.get("choices", []):
        choices.append(
            f'<label><input type="{input_type}" name="{esc(name)}" value="{esc(choice.get("id"))}"> '
            f'<span>{esc(choice.get("text"))}</span></label>'
        )
    correct = esc(json.dumps([str(value) for value in check.get("correct", [])]))
    return (
        '<section class="question-set" aria-label="Check for understanding">'
        f'<article class="question" data-correct="{correct}" '
        f'data-feedback-correct="{esc(check.get("feedback_correct"))}" '
        f'data-feedback-incorrect="{esc(check.get("feedback_incorrect"))}">'
        '<h3>Check for understanding</h3>'
        f'<p>{esc(check.get("prompt"))}</p>'
        f'<div class="choices">{"".join(choices)}</div>'
        '<button class="check-answer" type="button">Check my answer</button>'
        '<div class="feedback" role="status" hidden></div>'
        '</article></section>'
    )


def render_sources(source_ids: list[str] | None, resources: dict[str, dict]) -> str:
    entries = []
    for source_id in source_ids or []:
        source = resources.get(str(source_id))
        if not source:
            continue
        label = esc(source.get("title") or source_id)
        url = esc(source.get("url"))
        entries.append(f'<li><a href="{url}">{label}</a></li>' if url else f'<li>{label}</li>')
    if not entries:
        return ""
    return '<details class="source-foundation"><summary>Source Foundation</summary><ul>' + "".join(entries) + "</ul></details>"


def render_overview(lesson: dict) -> str:
    number = lesson["number"]
    objectives = "".join(f"<li>{esc(item)}</li>" for item in lesson.get("objectives", []))
    vocabulary = []
    for item in lesson.get("vocabulary", []):
        vocabulary.append(
            f'<li><button class="vocab-link" type="button" data-term="{esc(item.get("term"))}" '
            f'data-definition="{esc(item.get("definition"))}">{esc(item.get("term"))}</button></li>'
        )
    vocab_html = f'<h3>Vocabulary</h3><ul>{"".join(vocabulary)}</ul>' if vocabulary else ""
    return (
        f'<section class="lesson-step overview" data-step-label="{number}.1">'
        '<p class="eyebrow">Lesson overview</p>'
        f'<h2>{esc(lesson.get("title"))}</h2>'
        '<div class="overview-grid"><div>'
        f'<p>{esc(lesson.get("purpose"))}</p>'
        '<h3>Learning objectives</h3>'
        f'<ul class="objective-cards">{objectives}</ul>'
        '</div><aside class="overview-panel">'
        f'<h3>Plan your time</h3><p>Plan for about {esc(lesson.get("estimated_minutes", 50))} minutes, including the lesson assessment.</p>'
        f'{vocab_html}</aside></div></section>'
    )


def render_instruction(lesson: dict, suffix: str, step: dict, resources: dict[str, dict]) -> str:
    number = lesson["number"]
    focus = esc(step.get("focus") or "Focus on the main idea you will need for the application.")
    source_ids = list(dict.fromkeys((step.get("source_ids") or []) + (step.get("resource_ids") or [])))
    graphic = step.get("graphic") or {}
    graphic_html = ""
    if graphic.get("path"):
        graphic_html = (
            '<figure class="instructional-figure"><button class="image-zoom" type="button" aria-label="Enlarge instructional graphic">'
            f'<img src="../{esc(graphic.get("path"))}" alt="{esc(graphic.get("alt"))}"></button>'
            f'<figcaption>{esc(graphic.get("caption"))}</figcaption></figure>'
        )
    return (
        f'<section class="lesson-step" data-step-label="{number}.{suffix}" hidden>'
        f'<p class="eyebrow">Step {number}.{suffix}</p><h2>{esc(step.get("title"))}</h2>'
        f'<div class="next-move"><p><strong>Your next move:</strong> {focus}</p></div>'
        f'{paragraphs(step.get("body"))}'
        f'{graphic_html}'
        f'{render_resources(step.get("resource_ids", []), resources)}'
        f'{render_question(step.get("check"), number, suffix)}'
        f'{render_sources(source_ids, resources)}'
        '</section>'
    )


def render_application(lesson: dict, step: dict) -> str:
    number = lesson["number"]
    directions = "".join(f"<li>{esc(item)}</li>" for item in step.get("directions", []))
    scenarios = step.get("program_scenarios", [])
    if scenarios:
        options = "".join(f'<option value="{esc(item.get("program"))}">{esc(item.get("program"))}</option>' for item in scenarios)
        cards = []
        for index, item in enumerate(scenarios, start=1):
            prompts = []
            for prompt_index, prompt in enumerate(item.get("prompts", []), start=1):
                field_id = f"scenario-{number}-{index}-{prompt_index}"
                prompts.append(f'<label for="{field_id}">{esc(prompt)}</label><textarea id="{field_id}" rows="3"></textarea>')
            cards.append(
                f'<article class="scenario-card program-scenario-card" data-program="{esc(item.get("program"))}" hidden>'
                f'<p class="scenario-category">Your selected program: {esc(item.get("program"))}</p>'
                f'<p><strong>Situation:</strong> {esc(item.get("situation"))}</p>{"".join(prompts)}'
                '<button class="scenario-exemplar" type="button">Compare with an exemplar</button>'
                f'<div class="feedback exemplar-feedback" role="status" hidden>{esc(item.get("exemplar"))}</div></article>'
            )
        scenario_html = (
            '<div class="application-card program-application"><label for="program-select"><strong>Select your career program</strong></label>'
            f'<select id="program-select"><option value="">Choose a program</option>{options}</select>'
            '<button class="step-button program-start" type="button">Start my scenario</button>'
            '<p class="save-note">Complete your selected program first. You may choose another program afterward for optional practice.</p>'
            f'<div class="scenario-deck">{"".join(cards)}</div></div>'
        )
    else:
        scenario_html = '<p class="placeholder-note">Program-specific scenarios will appear here after designer approval.</p>'
    mode = step.get("completion_mode", "designer_decision").replace("_", " ")
    return (
        f'<section class="lesson-step classroom-activity" data-step-label="{number}.5" hidden>'
        f'<p class="eyebrow">Step {number}.5 · Apply your learning</p><h2>{esc(step.get("title"))}</h2>'
        f'<p>{esc(step.get("intro"))}</p><ol>{directions}</ol>{scenario_html}'
        f'<p><strong>Completion mode:</strong> {esc(mode.title())}</p>'
        '</section>'
    )


def render_assessment(lesson: dict, step: dict, mastery: dict) -> str:
    number = lesson["number"]
    return (
        f'<section class="lesson-step assessment-callout" data-step-label="{number}.6" hidden>'
        f'<p class="eyebrow">Step {number}.6 · Lesson assessment</p><h2>{esc(step.get("title"))}</h2>'
        '<div class="next-move"><p><strong>Your next move:</strong> Return to your course and complete the lesson assessment. '
        f'You may attempt it up to {esc(mastery.get("attempts", 3))} times. The mastery target is {esc(mastery.get("threshold_percent", 80))}%. '
        'Follow your instructor’s directions for submission and results.</p></div>'
        '<p>The public lesson site does not collect your assessment answers or personal information.</p>'
        '</section>'
    )


def render_lesson(data: dict, lesson: dict, resources: dict[str, dict]) -> str:
    course = data["course"]
    lessons = data["lessons"]
    number = lesson["number"]
    steps = lesson.get("steps", {})
    sections = [render_overview(lesson)]
    for suffix in ("2", "3", "4"):
        step = steps.get(suffix)
        if step:
            sections.append(render_instruction(lesson, suffix, step, resources))
    sections.append(render_application(lesson, steps["5"]))
    sections.append(render_assessment(lesson, steps["6"], course.get("mastery", {})))
    step_count = len(sections)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{esc(lesson.get('purpose'))}"><title>Lesson {number}: {esc(lesson.get('title'))} | {esc(course.get('short_title'))}</title>
<link rel="stylesheet" href="../assets/styles.css"></head>
<body data-lesson="{number}"><a class="skip-link" href="#main">Skip to lesson</a>
<header class="site-header classroom-header"><a class="brand" href="../index.html">{esc(course.get('short_title'))}</a><span class="classroom-label">Lesson {number}: {esc(lesson.get('title'))}</span><button class="menu-button" aria-expanded="false" aria-controls="course-nav">Lessons</button><nav id="course-nav">{navigation(lessons, number, '../')}</nav></header>
<main id="main"><header class="lesson-hero"><p class="lesson-identity">Lesson {number}: {esc(lesson.get('title'))}</p>
<div class="step-progress"><div class="progress-text"><span id="step-status">Step {number}.1</span><span id="step-count">1 of {step_count}</span></div><div class="progress" role="progressbar" aria-label="Lesson progress" aria-valuemin="1" aria-valuemax="{step_count}" aria-valuenow="1"><span style="width:{100 / step_count:.2f}%"></span></div></div></header>
<div class="stepper">{''.join(sections)}<p class="sr-only" id="step-announcement" aria-live="polite"></p>
<nav class="step-controls" aria-label="Lesson step navigation"><button class="step-button secondary" id="previous-step" type="button">← Previous step</button><button class="step-button" id="next-step" type="button">Next step →</button></nav><p class="step-help">Your place in this lesson is saved automatically on this device.</p></div></main>
<footer><p>{esc(course.get('title'))}</p></footer><script src="../assets/app.js"></script></body></html>'''


def render_index(data: dict) -> str:
    course = data["course"]
    lessons = data["lessons"]
    cards = "".join(
        f'<a class="lesson-card" href="lessons/lesson-{item["number"]}.html"><span class="lesson-number">{item["number"]}</span><div><h2>{esc(item.get("title"))}</h2><p>Open lesson {item["number"]}</p></div></a>'
        for item in lessons
    )
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{esc(course.get('description'))}"><title>{esc(course.get('title'))}</title><link rel="stylesheet" href="assets/styles.css"></head>
<body><a class="skip-link" href="#main">Skip to course</a><header class="site-header"><a class="brand" href="index.html">{esc(course.get('short_title'))}</a><button class="menu-button" aria-expanded="false" aria-controls="course-nav">Lessons</button><nav id="course-nav">{navigation(lessons)}</nav></header>
<main id="main"><section class="home-hero"><div><p class="eyebrow">Eight-week learning module</p><h1>{esc(course.get('title'))}</h1><p class="lede">{esc(course.get('description'))}</p><a class="button" href="lessons/lesson-1.html">Start lesson 1</a></div><div class="routine" aria-label="Course sequence"><span>Connect</span><span>Learn</span><span>Apply</span><span>Assess</span></div></section>
<section class="course-map"><p class="eyebrow">Course map</p><h2>Eight lessons designed for focused weekly learning.</h2><div class="lesson-grid">{cards}</div></section></main>
<footer><p>{esc(course.get('title'))}</p></footer><script src="assets/app.js"></script></body></html>'''


def main() -> None:
    data = json.loads(CONTENT.read_text(encoding="utf-8"))
    LESSONS.mkdir(exist_ok=True)
    resources = resource_lookup(data)
    (ROOT / "index.html").write_text(render_index(data), encoding="utf-8")
    for lesson in data["lessons"]:
        target = LESSONS / f"lesson-{lesson['number']}.html"
        target.write_text(render_lesson(data, lesson, resources), encoding="utf-8")
    print(f"Built {len(data['lessons'])} lessons from {CONTENT}")


if __name__ == "__main__":
    main()
