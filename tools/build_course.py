from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "course.json"
LESSONS = ROOT / "lessons"


VIDEO_FOCUS_PROMPTS = {
    "R001": "Watch for how a short team meeting can surface progress, next steps, and blockers without becoming a long status report.",
    "R002": "Watch for what Agile means and why teams use short cycles, feedback, and adaptation.",
    "R003": "Watch for what belongs in a Product Backlog and why the order of backlog items can change as the team learns.",
    "R005": "Watch for how a team chooses sprint work by balancing priority, capacity, and the sprint goal.",
    "R008": "Watch for the main Scrum accountabilities and how each role helps the team deliver useful work.",
    "R009": "Watch for what makes an Agile team cross-functional and self-organizing during software work.",
    "R010": "Watch for the decisions a team makes during Sprint Planning before it begins the sprint.",
    "R011": "Watch for how the Sprint Backlog helps a team see its plan, track work, and protect quality during a sprint.",
    "R012": "Watch for how a usable Increment and a Definition of Done help a team know whether work is truly complete.",
    "R013": "Watch for how the Daily Scrum helps developers inspect progress and adjust their plan for the next workday.",
    "R014": "Watch for how a Sprint Review uses completed work and stakeholder feedback to guide the next product decision.",
    "R015": "Watch for how a Sprint Retrospective focuses on improving the team’s process, not judging the product demo.",
    "R016": "Watch for how Scrum artifacts make product goals, sprint work, and completed increments visible.",
    "R017": "Watch for the big-picture purpose of Scrum and how it organizes teamwork around short cycles of product work.",
    "R018": "Watch for how acceptance criteria make a user story testable before the team starts building.",
    "R019": "Watch for why Agile teams use short cycles, feedback, and adaptation when project needs change.",
    "R020": "Watch for how the Agile Manifesto connects values, principles, practices, learning, and customer needs. Then use the reading to study the four values.",
    "R021": "Watch for the user-story format and how a story keeps the team focused on user value.",
    "R022": "Watch for how cards and columns help a team see what work is ready, active, blocked, or done.",
}


VIDEO_DISPLAY_TITLES = {
    "R002": "What Is Agile? | Atlassian Answered",
    "R008": "Scrum Roles",
    "R017": "What Is Scrum?",
    "R019": "Why Agile Teams Use Short Cycles",
    "R020": "The Agile Mindset: A Different Way of Working",
    "R021": "How to Write Good User Stories",
    "R022": "What Is Kanban?",
}


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def paragraphs(items: list[str] | None) -> str:
    return "".join(f"<p>{esc(item)}</p>" for item in (items or []) if item)


def bullet_list(items: list[str] | None, class_name: str = "lesson-list") -> str:
    entries = "".join(f"<li>{esc(item)}</li>" for item in (items or []) if item)
    if not entries:
        return ""
    return f'<ul class="{esc(class_name)}">{entries}</ul>'


def navigation(lessons: list[dict], current: int | None = None, prefix: str = "") -> str:
    links = []
    for lesson in lessons:
        attrs = ' aria-current="page"' if lesson["number"] == current else ""
        links.append(f'<a href="{prefix}lessons/lesson-{lesson["number"]}.html"{attrs}>Lesson {lesson["number"]}</a>')
    return "".join(links)


def resource_lookup(data: dict) -> dict[str, dict]:
    return {str(item.get("id")): item for item in data.get("resources", []) if item.get("id")}


def lesson_href(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    if parsed.scheme or url.startswith("#") or url.startswith("../"):
        return url
    return f"../{url}"


def youtube_embed_url(url: str) -> str:
    parsed = urlparse(url or "")
    host = parsed.netloc.lower()
    path = parsed.path.strip("/")
    video_id = ""
    if host.endswith("youtu.be"):
        video_id = path.split("/")[0]
    elif "youtube.com" in host:
        if path == "watch":
            video_id = parse_qs(parsed.query).get("v", [""])[0]
        elif path.startswith(("embed/", "shorts/")):
            parts = path.split("/")
            if len(parts) > 1:
                video_id = parts[1]
    if not video_id:
        return ""
    return f"https://www.youtube.com/embed/{video_id}"


def is_video_resource(resource_id: str, resources: dict[str, dict]) -> bool:
    resource = resources.get(str(resource_id))
    if not resource:
        return False
    return str(resource.get("type") or "").lower() == "video" and bool(youtube_embed_url(resource.get("url") or ""))


def split_resource_ids(ids: list[str] | None, resources: dict[str, dict]) -> tuple[list[str], list[str]]:
    video_ids = []
    other_ids = []
    for resource_id in ids or []:
        if is_video_resource(str(resource_id), resources):
            video_ids.append(str(resource_id))
        else:
            other_ids.append(str(resource_id))
    return video_ids, other_ids


def strip_step_label(text: str, label: str) -> str:
    value = str(text or "").strip()
    for separator in ("—", "-", ":"):
        prefix = f"{label} {separator}"
        if value.upper().startswith(prefix.upper()):
            return value[len(prefix):].strip()
    if value.upper() == label.upper():
        return ""
    return value


def connect_topic(title: str) -> str:
    value = str(title or "").strip()
    for prefix in ("Connect and Learn:", "Connect & Learn:"):
        if value.lower().startswith(prefix.lower()):
            return value[len(prefix):].strip()
    return value


def step_type_label(step: dict, suffix: str) -> str:
    kind = step.get("type")
    if kind in {"connect", "learn"}:
        return "Learn and check"
    if kind == "application" or suffix == "application":
        return "Practical application"
    if kind == "assessment" or suffix == "assessment":
        return "Lesson assessment"
    return "Lesson step"


def estimated_time(step: dict) -> str:
    minutes = step.get("estimated_minutes")
    if not minutes:
        return ""
    return f'<p class="step-time">Estimated time: {esc(minutes)} minutes</p>'


def next_move(text: str, icon: str = "▶️") -> str:
    return f'<div class="next-move"><p><span aria-hidden="true">{icon}</span> <strong>Your next move:</strong> {esc(text)}</p></div>'


def render_resources(ids: list[str], resources: dict[str, dict], include_video_prompt: bool = True) -> str:
    cards = []
    for resource_id in ids or []:
        resource = resources.get(str(resource_id))
        if not resource:
            continue
        source_title = esc(resource.get("title") or "Learning resource")
        title = esc(VIDEO_DISPLAY_TITLES.get(str(resource_id), resource.get("title") or "Learning resource"))
        url = esc(resource.get("url"))
        transcript = esc(lesson_href(resource.get("transcript_url") or ""))
        description = esc(resource.get("description"))
        embed_url = youtube_embed_url(resource.get("url") or "") if str(resource.get("type") or "").lower() == "video" else ""
        media = ""
        if embed_url:
            prompt_html = ""
            if include_video_prompt:
                prompt = esc(VIDEO_FOCUS_PROMPTS.get(str(resource_id), "Watch the video. Focus on the idea you will use in the next activity."))
                prompt_html = (
                    '<div class="next-move video-focus"><p><span aria-hidden="true">▶️</span> <strong>Your next move:</strong> '
                    f'{prompt}</p></div>'
                )
            media = (
                f'{prompt_html}'
                '<div class="video-embed">'
                f'<iframe src="{esc(embed_url)}" title="Video: {title}" loading="lazy" '
                'referrerpolicy="strict-origin-when-cross-origin" '
                'allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
                'allowfullscreen></iframe></div>'
            )
        actions = []
        if url:
            actions.append(f'<a href="{url}">Open video in new tab</a>' if embed_url else f'<a href="{url}">Open {source_title}</a>')
        if transcript:
            actions.append(f'<a href="{transcript}">Open transcript</a>')
        cards.append(
            '<section class="resource-card">'
            f'<h3>{title}</h3>'
            f'<p>{description}</p>'
            f'{media}'
            f'<div class="resource-actions">{"".join(actions)}</div>'
            '</section>'
        )
    return "".join(cards)


def render_optional_videos(source_ids: list[str] | None, primary_ids: list[str] | None, resources: dict[str, dict]) -> str:
    primary = {str(item) for item in (primary_ids or [])}
    video_ids = []
    for source_id in source_ids or []:
        key = str(source_id)
        source = resources.get(key)
        if not source or key in primary:
            continue
        if is_video_resource(key, resources):
            video_ids.append(key)
    video_ids = list(dict.fromkeys(video_ids))
    if not video_ids:
        return ""
    return (
        '<details class="optional-video-support"><summary>Optional video support</summary>'
        f'{render_resources(video_ids, resources)}'
        '</details>'
    )


def render_question(check_data, lesson_number: int, step_number: str) -> str:
    checks = check_data if isinstance(check_data, list) else ([check_data] if check_data else [])
    checks = [check for check in checks if check]
    if not checks:
        reason = esc(check_data.get("override_reason")) if isinstance(check_data, dict) else ""
        note = f" Designer decision: {reason}" if reason else ""
        return f'<p class="placeholder-note">A check for understanding has not been approved for this step.{note}</p>'
    articles = []
    for index, check in enumerate(checks, start=1):
        choices = []
        input_type = "checkbox" if check.get("type") == "multiple_select" else "radio"
        name = f"check-{lesson_number}-{step_number}-{index}"
        for choice in check.get("choices", []):
            choices.append(
                f'<label><input type="{input_type}" name="{esc(name)}" value="{esc(choice.get("id"))}"> '
                f'<span>{esc(choice.get("text"))}</span></label>'
            )
        correct = esc(json.dumps([str(value) for value in check.get("correct", [])]))
        articles.append(
            f'<article class="question" data-correct="{correct}" '
            f'data-feedback-correct="{esc(check.get("feedback_correct"))}" '
            f'data-feedback-incorrect="{esc(check.get("feedback_incorrect"))}">'
            f'<h4>Question {index}</h4>'
            f'<p>{esc(check.get("prompt"))}</p>'
            f'<div class="choices">{"".join(choices)}</div>'
            '<button class="check-answer" type="button">Check my answer</button>'
            '<div class="feedback" role="status" hidden></div>'
            '</article>'
        )
    return (
        '<section class="question-set" aria-label="Check for understanding">'
        '<h3>Check for understanding</h3>'
        f'{"".join(articles)}</section>'
    )


def render_sources(source_ids: list[str] | None, resources: dict[str, dict]) -> str:
    entries = []
    for source_id in source_ids or []:
        source = resources.get(str(source_id))
        if not source:
            continue
        label = esc(source.get("title") or source_id)
        url = esc(source.get("url"))
        transcript = esc(lesson_href(source.get("transcript_url") or ""))
        links = []
        if url:
            links.append(f'<a href="{url}">{label}</a>')
        else:
            links.append(label)
        if transcript:
            links.append(f'<a href="{transcript}">transcript</a>')
        entries.append(f'<li>{" ".join(links)}</li>')
    if not entries:
        return ""
    return '<details class="source-foundation"><summary>Source Foundation</summary><ul>' + "".join(entries) + "</ul></details>"


def render_overview(lesson: dict, standards: dict[str, dict]) -> str:
    number = lesson["number"]
    objective_items = []
    for item in lesson.get("objectives", []):
        for objective in str(item).split("|"):
            student_text = re.sub(r"^L\d+-O\d+\s+", "", objective.strip())
            if student_text:
                objective_items.append(f"<li>{esc(student_text)}</li>")
    objectives = "".join(objective_items)
    pacing_rows = lesson.get("pacing_at_a_glance", [])
    pacing_items = "".join(
        f'<li><span>{esc(item.get("label"))}</span><strong>{esc(item.get("minutes"))} min</strong></li>'
        for item in pacing_rows
    )
    pacing_total = sum(int(item.get("minutes", 0)) for item in pacing_rows)
    pacing_html = (
        '<h3>Pacing at a glance</h3>'
        f'<ul class="lesson-pacing">{pacing_items}</ul>'
        f'<p class="pacing-total"><strong>Total: about {pacing_total} minutes</strong></p>'
        if pacing_rows else
        f'<h3>Pacing at a glance</h3><p>Plan for about {esc(lesson.get("estimated_minutes", 50))} minutes.</p>'
    )
    vocabulary = []
    for item in lesson.get("vocabulary", []):
        vocabulary.append(
            f'<li><button class="vocab-link" type="button" data-term="{esc(item.get("term"))}" '
            f'data-definition="{esc(item.get("definition"))}">{esc(item.get("term"))}</button></li>'
        )
    vocab_html = f'<h3>Vocabulary</h3><ul>{"".join(vocabulary)}</ul>' if vocabulary else ""
    student_hub = lesson.get("student_hub") or {}
    student_hub_html = ""
    if student_hub:
        hub_bullets = bullet_list(student_hub.get("bullets", []))
        hub_image = esc(student_hub.get("image") or "assets/images/student-hub-phone.png")
        hub_alt = esc(student_hub.get("alt") or "Student Hub app shown on a smartphone.")
        hub_body = student_hub.get("body") or []
        if isinstance(hub_body, str):
            hub_body = [hub_body]
        challenge = student_hub.get("challenge")
        challenge_html = (
            f'<h4>Your first team challenge</h4><p>{esc(challenge)}</p>' if challenge else ""
        )
        role_heading = student_hub.get("role_heading")
        role_heading_html = f'<h4>{esc(role_heading)}</h4>' if role_heading else ""
        student_hub_html = (
            f'<section class="lesson-project-anchor" aria-labelledby="student-hub-title-{number}">'
            f'<figure><img src="../{hub_image}" width="280" height="336" alt="{hub_alt}">'
            f'<figcaption>{esc(student_hub.get("caption") or "Student Hub is the continuing software project for this module.")}</figcaption></figure>'
            f'<div><p class="eyebrow">{esc(student_hub.get("eyebrow") or "Project connection")}</p>'
            f'<h3 id="student-hub-title-{number}">{esc(student_hub.get("title") or "Student Hub in this lesson")}</h3>'
            f'{paragraphs(hub_body)}{challenge_html}{role_heading_html}{hub_bullets}</div></section>'
        )
    standards_items = []
    for standard_id in lesson.get("standards", []):
        standard = standards.get(str(standard_id), {})
        standards_items.append(
            f'<li><strong>{esc(standard_id)}</strong> {esc(standard.get("text") or "Standard wording unavailable.")}</li>'
        )
    standards_html = (
        f'<section class="lesson-standards" aria-labelledby="lesson-standards-title-{number}">'
        f'<h3 id="lesson-standards-title-{number}">Agile standards covered</h3>'
        f'<ul>{"".join(standards_items)}</ul></section>'
        if standards_items else ""
    )
    return (
        f'<section class="lesson-step overview" data-step-label="{number}.1">'
        '<p class="eyebrow">Lesson overview</p>'
        f'<h2>{esc(lesson.get("title"))}</h2>'
        '<div class="overview-grid"><div>'
        f'<p>{esc(lesson.get("purpose"))}</p>'
        '<h3>Learning objectives</h3>'
        f'<ul class="objective-cards">{objectives}</ul>'
        '</div><aside class="overview-panel">'
        f'{pacing_html}'
        f'{vocab_html}</aside></div>{student_hub_html}{standards_html}</section>'
    )


def render_instruction(lesson: dict, suffix: str, step: dict, resources: dict[str, dict]) -> str:
    number = lesson["number"]
    focus_text = step.get("focus") or "Focus on the main idea you will need for the application."
    focus = esc(focus_text)
    source_ids = list(dict.fromkeys((step.get("source_ids") or []) + (step.get("resource_ids") or [])))
    video_resource_ids, reading_resource_ids = split_resource_ids(step.get("resource_ids", []), resources)
    graphic = step.get("graphic") or {}
    graphic_html = ""
    if graphic.get("path"):
        graphic_html = (
            '<figure class="instructional-figure"><button class="image-zoom" type="button" aria-label="Enlarge instructional graphic">'
            f'<img src="../{esc(graphic.get("path"))}" alt="{esc(graphic.get("alt"))}"></button>'
            f'<figcaption>{esc(graphic.get("caption"))}</figcaption></figure>'
        )
    worked_example = step.get("worked_example") or {}
    worked_example_html = ""
    if worked_example.get("steps"):
        example_rows = "".join(
            f'<div class="worked-example-row"><dt>{esc(item.get("label"))}</dt><dd>{esc(item.get("text"))}</dd></div>'
            for item in worked_example.get("steps", [])
        )
        worked_example_html = (
            '<section class="worked-example" aria-labelledby="worked-example-title">'
            f'<h3 id="worked-example-title">{esc(worked_example.get("title"))}</h3>'
            f'<p>{esc(worked_example.get("intro"))}</p><dl>{example_rows}</dl></section>'
        )
    if step.get("type") == "connect":
        body_items = [strip_step_label(item, "LEARN") for item in (step.get("body") or [])]
        after_graphic_items = step.get("after_graphic") or []
        topic = esc(connect_topic(step.get("title") or ""))
        connect_prompt = esc(strip_step_label(focus_text, "CONNECT") or focus_text)
        watch_heading = "<h2>Watch</h2>" if video_resource_ids else ""
        return (
            f'<section class="lesson-step" data-step-label="{number}.{suffix}" hidden>'
            f'<p class="eyebrow">Step {number}.{suffix} · {step_type_label(step, suffix)}</p><h2>Connect</h2>'
            f'<p class="step-topic">{topic}</p>'
            f'{estimated_time(step)}'
            f'{next_move(strip_step_label(focus_text, "CONNECT") or focus_text, "🚗")}'
            f'{watch_heading}'
            f'{render_resources(video_resource_ids, resources, include_video_prompt=False)}'
            '<h2>Learn</h2>'
            f'{next_move("Read the short explanation below. Look for how planning, feedback, and change work together.", "📖")}'
            f'{paragraphs(body_items)}'
            f'{graphic_html}'
            f'{paragraphs(after_graphic_items)}'
            f'{render_resources(reading_resource_ids, resources)}'
            f'{render_question(step.get("checks") or step.get("check"), number, suffix)}'
            f'{render_optional_videos(step.get("source_ids", []), step.get("resource_ids", []), resources)}'
            f'{render_sources(source_ids, resources)}'
            '</section>'
        )
    return (
        f'<section class="lesson-step" data-step-label="{number}.{suffix}" hidden>'
        f'<p class="eyebrow">Step {number}.{suffix} · {step_type_label(step, suffix)}</p><h2>{esc(step.get("title"))}</h2>'
        f'{estimated_time(step)}'
        f'{next_move(focus_text, "▶️" if video_resource_ids else "📖")}'
        f'{render_resources(video_resource_ids, resources, include_video_prompt=False)}'
        f'{paragraphs(step.get("body"))}'
        f'{bullet_list(step.get("bullets"))}'
        f'{graphic_html}'
        f'{paragraphs(step.get("after_graphic"))}'
        f'{worked_example_html}'
        f'{render_resources(reading_resource_ids, resources)}'
        f'{render_optional_videos(step.get("source_ids", []), step.get("resource_ids", []), resources)}'
        f'{render_question(step.get("checks") or step.get("check"), number, suffix)}'
        f'{render_sources(source_ids, resources)}'
        '</section>'
    )


def render_application(lesson: dict, step: dict, suffix: str) -> str:
    number = lesson["number"]
    directions = "".join(f"<li>{esc(item)}</li>" for item in step.get("directions", []))
    response_choices = step.get("response_choices") or {}
    response_choices_html = ""
    if response_choices.get("options"):
        response_options = "".join(f"<li>{esc(item)}</li>" for item in response_choices.get("options", []))
        response_choices_html = (
            '<aside class="response-choices" aria-labelledby="response-choices-title">'
            f'<h3 id="response-choices-title">{esc(response_choices.get("title"))}</h3>'
            f'<p>{esc(response_choices.get("intro"))}</p><ul>{response_options}</ul></aside>'
        )
    response_template = step.get("response_template") or {}
    response_template_html = ""
    if response_template.get("fields"):
        template_fields = "".join(
            f'<li><span>{esc(field)}</span></li>' for field in response_template.get("fields", [])
        )
        response_template_html = (
            '<section class="response-template" aria-labelledby="response-template-title">'
            f'<h3 id="response-template-title">{esc(response_template.get("title"))}</h3>'
            f'<p>{esc(response_template.get("intro"))}</p>'
            f'<ul>{template_fields}</ul></section>'
        )
    decision_table = step.get("decision_table") or {}
    decision_table_html = ""
    if decision_table.get("rows"):
        if decision_table.get("layout") == "cards":
            cards = []
            for row in decision_table.get("rows", []):
                decision, lead, reason = (row + ["", "", ""])[:3]
                cards.append(
                    '<article class="decision-guide-card">'
                    f'<h4>{esc(decision)}</h4>'
                    '<dl>'
                    f'<div><dt>Choose</dt><dd>{esc(lead)}</dd></div>'
                    f'<div><dt>Why</dt><dd>{esc(reason)}</dd></div>'
                    '</dl></article>'
                )
            decision_table_html = (
                '<section class="decision-guide" aria-labelledby="decision-guide-title">'
                f'<h3 id="decision-guide-title">{esc(decision_table.get("title"))}</h3>'
                f'<p>{esc(decision_table.get("intro"))}</p>'
                f'<div class="decision-guide-grid">{"".join(cards)}</div></section>'
            )
        else:
            columns = decision_table.get("columns", [])
            header_cells = "".join(f"<th scope=\"col\">{esc(column)}</th>" for column in columns)
            body_rows = []
            for row in decision_table.get("rows", []):
                cells = "".join(f"<td>{esc(cell)}</td>" for cell in row)
                body_rows.append(f"<tr>{cells}</tr>")
            decision_table_html = (
                '<section class="decision-guide" aria-labelledby="decision-guide-title">'
                f'<h3 id="decision-guide-title">{esc(decision_table.get("title"))}</h3>'
                f'<p>{esc(decision_table.get("intro"))}</p>'
                '<div class="table-scroll"><table>'
                f'<thead><tr>{header_cells}</tr></thead>'
                f'<tbody>{"".join(body_rows)}</tbody>'
                '</table></div></section>'
            )
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
            '<div class="application-card program-application"><label for="program-select"><strong>Select your career field</strong></label>'
            f'<select id="program-select"><option value="">Choose a field</option>{options}</select>'
            '<button class="step-button program-start" type="button">Start my scenario</button>'
            '<p class="save-note">Complete one career scenario. You may choose another afterward for optional practice.</p>'
            f'<div class="scenario-deck">{"".join(cards)}</div></div>'
        )
    else:
        scenario_html = '<p class="placeholder-note">Program-specific scenarios will appear here after designer approval.</p>'
    team_handoff = step.get("team_handoff") or {}
    team_handoff_html = ""
    if team_handoff.get("prompt"):
        handoff_id = f"team-handoff-{number}"
        team_handoff_html = (
            '<section class="team-handoff" aria-labelledby="team-handoff-title">'
            f'<h3 id="team-handoff-title">{esc(team_handoff.get("title"))}</h3>'
            f'<label for="{handoff_id}">{esc(team_handoff.get("prompt"))}</label>'
            f'<textarea id="{handoff_id}" rows="2"></textarea>'
            f'<p class="save-note">{esc(team_handoff.get("help"))}</p></section>'
        )
    return (
        f'<section class="lesson-step classroom-activity" data-step-label="{number}.{suffix}" hidden>'
        f'<p class="eyebrow">Step {number}.{suffix} · Practical application</p><h2>{esc(step.get("title"))}</h2>'
        f'{estimated_time(step)}'
        f'<p>{esc(step.get("intro"))}</p><ol>{directions}</ol>{response_choices_html}{decision_table_html}{response_template_html}{scenario_html}{team_handoff_html}'
        '</section>'
    )


def render_assessment(lesson: dict, step: dict, mastery: dict, suffix: str) -> str:
    number = lesson["number"]
    return (
        f'<section class="lesson-step assessment-callout" data-step-label="{number}.{suffix}" hidden>'
        f'<p class="eyebrow">Step {number}.{suffix} · Lesson assessment</p><h2>{esc(step.get("title"))}</h2>'
        f'{estimated_time(step)}'
        '<div class="next-move"><p><span aria-hidden="true">✅</span> <strong>Your next move:</strong> Return to your course and complete the lesson assessment. '
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
    standards = {str(item.get("id")): item for item in data.get("standards", [])}
    sections = [render_overview(lesson, standards)]
    for suffix in ("2", "3", "4"):
        step = steps.get(suffix)
        if step:
            sections.append(render_instruction(lesson, suffix, step, resources))
    instructional_suffixes = [suffix for suffix in ("2", "3", "4") if steps.get(suffix)]
    application_suffix = str(max(map(int, instructional_suffixes)) + 1)
    assessment_suffix = str(int(application_suffix) + 1)
    application_step = steps.get("application") or steps.get("5")
    assessment_step = steps.get("assessment") or steps.get("6")
    sections.append(render_application(lesson, application_step, application_suffix))
    sections.append(render_assessment(lesson, assessment_step, course.get("mastery", {}), assessment_suffix))
    step_count = len(sections)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{esc(lesson.get('purpose'))}"><title>Lesson {number}: {esc(lesson.get('title'))} | {esc(course.get('short_title'))}</title>
<link rel="stylesheet" href="../assets/styles.css?v=20260912-6"></head>
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
    project_name = esc(course.get("project_name") or "Module project")
    project_summary = esc(course.get("project_summary") or "")
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{esc(course.get('description'))}"><title>{esc(course.get('title'))}</title><link rel="stylesheet" href="assets/styles.css?v=20260912-2"></head>
<body><a class="skip-link" href="#main">Skip to course</a><header class="site-header"><a class="brand" href="index.html">{esc(course.get('short_title'))}</a><button class="menu-button" aria-expanded="false" aria-controls="course-nav">Lessons</button><nav id="course-nav">{navigation(lessons)}</nav></header>
<main id="main"><section class="home-hero"><div><p class="eyebrow">Eight-week learning module</p><h1>{esc(course.get('title'))}</h1><p class="lede">{esc(course.get('description'))}</p><a class="button" href="lessons/lesson-1.html">Start lesson 1</a></div><div class="routine" aria-label="Course sequence"><span>Connect</span><span>Learn</span><span>Apply</span><span>Assess</span></div></section>
<section class="project-spotlight" aria-labelledby="project-title"><div class="project-visual"><img src="assets/images/student-hub-phone.png" width="280" height="336" alt="A smartphone displaying a calendar-style app icon with a checkmark and event markers."></div><div class="project-copy"><p class="eyebrow">Module project</p><h2 id="project-title">{project_name}</h2><p class="project-summary">{project_summary}</p><h3>How the project develops</h3><ol class="project-path" aria-label="Student Hub Agile workflow"><li><span aria-hidden="true">1</span>User needs</li><li><span aria-hidden="true">2</span>Backlog</li><li><span aria-hidden="true">3</span>Sprint plan</li><li><span aria-hidden="true">4</span>Increment</li><li><span aria-hidden="true">5</span>Feedback</li><li><span aria-hidden="true">6</span>Improve</li></ol></div></section>
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
