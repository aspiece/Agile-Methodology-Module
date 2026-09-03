import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = path.resolve(import.meta.dirname, "..");
const outputDir = path.join(root, "outputs", "workbook-prototype");
const previewDir = path.join(root, "outputs", "workbook-previews");
const resourcePath = path.join(root, "resources", "Module_Resource_Collection.xlsx");
await fs.mkdir(outputDir, { recursive: true });
await fs.mkdir(previewDir, { recursive: true });
await fs.mkdir(path.dirname(resourcePath), { recursive: true });

const wb = Workbook.create();
wb.comments.setSelf({ displayName: "User" });

const colors = {
  teal: "#005A70",
  blue: "#2980B9",
  cyan: "#00A3A6",
  green: "#27AE60",
  orange: "#E67E22",
  sky: "#F2F9FD",
  paper: "#FFFFFF",
  ink: "#222222",
  muted: "#5A5A5A",
  line: "#D6E2E6",
  amberBg: "#FFF9F3",
};

const sheets = {};
for (const name of [
  "Start Here", "Course Setup", "Standards", "Resources", "Lesson Blueprint",
  "Lesson Content", "Checks for Understanding", "Application Activities", "Program Scenarios",
  "Assessment Bank", "Decisions & Issues"
]) {
  const sheet = wb.worksheets.add(name);
  sheet.showGridLines = false;
  sheets[name] = sheet;
}

function title(sheet, text, subtitle, endColumn) {
  sheet.getRange(`A1:${endColumn}1`).merge();
  sheet.getRange("A1").values = [[text]];
  sheet.getRange(`A1:${endColumn}1`).format = {
    fill: colors.teal,
    font: { bold: true, color: colors.paper, size: 18 },
    rowHeight: 32,
    verticalAlignment: "center",
  };
  sheet.getRange(`A2:${endColumn}2`).merge();
  sheet.getRange("A2").values = [[subtitle]];
  sheet.getRange(`A2:${endColumn}2`).format = {
    fill: colors.sky,
    font: { color: colors.ink, italic: true },
    wrapText: true,
    rowHeight: 34,
    verticalAlignment: "center",
  };
}

function writeTable(sheet, startRow, headers, rows, tableName, widths = {}) {
  const startCol = 1;
  const endCol = headers.length;
  const letters = n => {
    let value = "";
    while (n > 0) { n--; value = String.fromCharCode(65 + (n % 26)) + value; n = Math.floor(n / 26); }
    return value;
  };
  const matrix = [headers, ...rows];
  const range = sheet.getRange(`A${startRow}:${letters(endCol)}${startRow + rows.length}`);
  range.values = matrix;
  range.format.wrapText = true;
  range.format.verticalAlignment = "top";
  range.format.borders = { insideVertical: { style: "thin", color: colors.line } };
  const header = sheet.getRange(`A${startRow}:${letters(endCol)}${startRow}`);
  header.format = {
    fill: colors.blue,
    font: { bold: true, color: colors.paper },
    wrapText: true,
    rowHeight: 38,
    verticalAlignment: "center",
  };
  const table = sheet.tables.add(`A${startRow}:${letters(endCol)}${startRow + rows.length}`, true, tableName);
  table.style = "TableStyleMedium2";
  table.showBandedRows = true;
  for (let index = 1; index <= endCol; index++) {
    sheet.getRange(`${letters(index)}:${letters(index)}`).format.columnWidth = widths[index] || 18;
  }
  sheet.freezePanes.freezeRows(startRow);
  return { range, startRow, endRow: startRow + rows.length, endCol };
}

// Start Here
{
  const s = sheets["Start Here"];
  title(s, "Eight-Week CTE Module: Resource Collection Workbook", "Designers provide standards and approved resources. Codex uses this workbook to propose, draft, and validate the eight-lesson module.", "H");
  s.getRange("A4:H4").merge();
  s.getRange("A4").values = [["How to use this workbook"]];
  s.getRange("A4:H4").format = { fill: colors.orange, font: { bold: true, color: colors.paper, size: 14 }, rowHeight: 26 };
  s.getRange("A5:H10").values = [
    ["1", "Complete Course Setup and enter the authoritative standards.", null, null, null, null, null, null],
    ["2", "Add resources selected by the designer. Include transcripts or caption information for required media.", null, null, null, null, null, null],
    ["3", "Ask Codex to propose the eight-lesson blueprint. Review topics, objectives, optional steps, pacing, and application focus.", null, null, null, null, null, null],
    ["4", "After blueprint approval, ask Codex to draft checks, program applications, and assessments in the remaining tabs.", null, null, null, null, null, null],
    ["5", "Approve or revise each drafted item. Only Approved items are used for release outputs.", null, null, null, null, null, null],
    ["6", "Generate the site and platform assessment exports, preview them, and publish only after authorization.", null, null, null, null, null, null],
  ];
  s.getRange("A5:A10").format = { fill: colors.teal, font: { bold: true, color: colors.paper }, horizontalAlignment: "center" };
  s.getRange("B5:H10").merge(true);
  s.getRange("A5:H10").format.wrapText = true;
  s.getRange("A5:H10").format.rowHeight = 34;
  s.getRange("A12:D12").values = [["Readiness check", "Current count", "Expected", "Status"]];
  s.getRange("A12:D12").format = { fill: colors.blue, font: { bold: true, color: colors.paper } };
  s.getRange("A13:A17").values = [["Standards entered"], ["Approved resources"], ["Lesson rows"], ["Approved checks"], ["Approved assessment items"]];
  s.getRange("B13:B17").formulas = [
    ["=COUNTIF('Standards'!$A$5:$A$204,\"?*\")"],
    ["=COUNTIF('Resources'!$Q$5:$Q$204,\"Approved\")"],
    ["=COUNTA('Lesson Blueprint'!$A$5:$A$12)"],
    ["=COUNTIF('Checks for Understanding'!$U$5:$U$204,\"Approved\")"],
    ["=COUNTIF('Assessment Bank'!$Y$5:$Y$304,\"Approved\")"],
  ];
  s.getRange("C13:C17").values = [[">0"], [">0"], [8], ["As drafted"], ["As drafted"]];
  s.getRange("D13:D17").formulas = [
    ["=IF(B13>0,\"Started\",\"Needed\")"], ["=IF(B14>0,\"Started\",\"Needed\")"],
    ["=IF(B15=8,\"Ready\",\"Check\")"], ["=IF(B16>0,\"Started\",\"Pending\")"],
    ["=IF(B17>0,\"Started\",\"Pending\")"],
  ];
  s.getRange("A13:D17").format.borders = { preset: "inside", style: "thin", color: colors.line };
  s.getRange("D13:D17").conditionalFormats.add("containsText", { text: "Ready", format: { fill: "#E9F7EF", font: { color: colors.green, bold: true } } });
  s.getRange("D13:D17").conditionalFormats.add("containsText", { text: "Needed", format: { fill: colors.amberBg, font: { color: "#9A4A00", bold: true } } });
  s.getRange("A:A").format.columnWidth = 22;
  s.getRange("B:H").format.columnWidth = 18;
  s.freezePanes.freezeRows(2);
}

// Course Setup
{
  const s = sheets["Course Setup"];
  title(s, "Course Setup", "These values apply to the full eight-week module. Established defaults are prefilled and should change only through an approved template revision.", "D");
  const rows = [
    ["Course title", "", "Designer", "Required"],
    ["Short title", "", "Designer", "Required"],
    ["Module purpose", "", "Designer", "Required"],
    ["Module type", "CTE", "Template default", "CTE requires program-specific .5 applications"],
    ["Audience", "Grades 11–12 CTE students", "Template default", "Fixed"],
    ["Number of lessons", 8, "Template default", "Fixed"],
    ["Minutes per lesson", 50, "Template default", "Includes .6 assessment"],
    ["Reading level", "Grades 7–8", "Template default", "Student-facing text"],
    ["Accessibility target", "WCAG 2.2 AA and UDL", "Template default", "Fixed"],
    ["Mastery threshold", 0.8, "Template default", "Fixed"],
    ["Assessment attempts", 3, "Template default", "Fixed"],
    ["Assessment location", "Return to the course", "Template default", "No student data collected by public site"],
    ["Designer or team", "", "Designer", "Optional"],
    ["Feedback form URL", "", "Designer", "Optional"],
  ];
  writeTable(s, 4, ["Setting", "Value", "Authority", "Notes"], rows, "CourseSetupTable", {1: 25, 2: 36, 3: 20, 4: 48});
  s.getRange("B13").format.numberFormat = "0%";
}

// Standards
{
  const s = sheets["Standards"];
  title(s, "Content Standards", "Enter the authoritative standards that Codex must use to propose lesson topics and objectives.", "H");
  const rows = [["", "", "", "", "Required", "", "", "Not Started"]];
  writeTable(s, 4, ["Standard ID", "Full Standard Wording", "Issuing Organization", "Source URL", "Priority", "Designer Notes", "Evidence or Clarification", "Status"], rows, "StandardsTable", {1: 18, 2: 55, 3: 26, 4: 40, 5: 14, 6: 36, 7: 36, 8: 16});
  s.getRange("E5:E204").dataValidation = { rule: { type: "list", values: ["Required", "Supporting"] } };
  s.getRange("H5:H204").dataValidation = { rule: { type: "list", values: ["Not Started", "Ready for Analysis", "Needs Clarification"] } };
}

// Resources
{
  const s = sheets["Resources"];
  title(s, "Designer-Selected Resources", "Record trustworthy videos, transcripts, readings, websites, documents, and graphics. One instructional step should normally use one primary resource.", "R");
  const headers = ["Resource ID", "Title", "Resource Type", "URL or File Path", "Publisher or Author", "Publication Date", "Runtime Minutes", "Transcript URL or Path", "Captions Verified", "Accessibility Notes", "Standard IDs", "Suggested Lesson", "Suggested Step", "Designer Notes", "Instructional Purpose", "Source or Attribution", "Approval Status", "Link Check"];
  const rows = [["R001", "", "Video", "", "", null, null, "", "Not Checked", "", "", null, "Step .2", "", "", "", "Not Reviewed", "Not Checked"]];
  writeTable(s, 4, headers, rows, "ResourcesTable", {1: 14, 2: 34, 3: 18, 4: 42, 5: 24, 6: 16, 7: 14, 8: 42, 9: 18, 10: 32, 11: 18, 12: 14, 13: 14, 14: 34, 15: 36, 16: 32, 17: 18, 18: 16});
  s.getRange("C5:C204").dataValidation = { rule: { type: "list", values: ["Video", "Transcript", "Reading", "Website", "Document", "Graphic", "Audio", "Other"] } };
  s.getRange("I5:I204").dataValidation = { rule: { type: "list", values: ["Verified", "Not Checked", "Not Applicable"] } };
  s.getRange("M5:M204").dataValidation = { rule: { type: "list", values: ["Step .2", "Step .3", "Step .4", "Step .5", "Unassigned"] } };
  s.getRange("Q5:Q204").dataValidation = { rule: { type: "list", values: ["Not Reviewed", "Approved", "Rejected", "Needs Follow-Up"] } };
  s.getRange("R5:R204").dataValidation = { rule: { type: "list", values: ["Not Checked", "Working", "Broken", "Restricted"] } };
}

// Lesson Blueprint
{
  const s = sheets["Lesson Blueprint"];
  title(s, "Eight-Lesson Blueprint", "Codex proposes the topics, objectives, optional steps, applications, and pacing from approved standards and resources. The designer approves each lesson before drafting.", "R");
  const headers = ["Lesson", "Proposed Title", "Topic and Purpose", "Standard IDs", "Draft Learning Objectives", "Vocabulary", ".2 Focus", ".2 Resource ID", "Use .3?", ".3 Focus and Resource", "Use .4?", ".4 Focus and Resource", ".5 Application Focus", "Activity Completion Mode", ".6 Evidence of Learning", "Estimated Minutes", "Designer Status", "Designer Notes"];
  const rows = Array.from({length: 8}, (_, index) => [index + 1, `Lesson ${index + 1} Topic`, "", "", "", "", "", "", "No", "", "No", "", "", "Designer Decision", "", 50, "Not Reviewed", ""]);
  writeTable(s, 4, headers, rows, "LessonBlueprintTable", {1: 10, 2: 30, 3: 42, 4: 18, 5: 50, 6: 28, 7: 36, 8: 18, 9: 12, 10: 40, 11: 12, 12: 40, 13: 42, 14: 25, 15: 40, 16: 15, 17: 18, 18: 34});
  s.getRange("I5:I12").dataValidation = { rule: { type: "list", values: ["Yes", "No"] } };
  s.getRange("K5:K12").dataValidation = { rule: { type: "list", values: ["Yes", "No"] } };
  s.getRange("N5:N12").dataValidation = { rule: { type: "list", values: ["Interactive Lesson", "Course Response", "Course Document Submission", "Instructor-Facilitated", "Combined", "Designer Decision"] } };
  s.getRange("Q5:Q12").dataValidation = { rule: { type: "list", values: ["Not Reviewed", "Approved", "Revise"] } };
}

// Lesson Content
{
  const s = sheets["Lesson Content"];
  title(s, "Draft Student-Facing Lesson Content", "Codex drafts concise, source-supported instruction here after the blueprint is approved. Each row represents one instructional step; .3 and .4 are added only when needed.", "P");
  const headers = ["Lesson", "Step", "Step Title", "Instructional Purpose", "Your Next Move", "Student-Facing Instruction", "Primary Resource ID", "Additional Source IDs", "Graphic Path", "Graphic Alt Text", "Graphic Caption", "Check Override Reason", "Estimated Minutes", "Reading-Level Check", "Approval Status", "Designer Notes"];
  const rows = Array.from({length: 8}, (_, index) => [index + 1, "Step .2", "Connect and Learn", "", "", "", "", "", "", "", "", "", 12, "Not Checked", "Not Reviewed", ""]);
  writeTable(s, 4, headers, rows, "LessonContentTable", {1: 10, 2: 10, 3: 30, 4: 38, 5: 48, 6: 68, 7: 20, 8: 22, 9: 34, 10: 48, 11: 38, 12: 40, 13: 16, 14: 20, 15: 18, 16: 34});
  s.getRange("B5:B204").dataValidation = { rule: { type: "list", values: ["Step .2", "Step .3", "Step .4"] } };
  s.getRange("N5:N204").dataValidation = { rule: { type: "list", values: ["Not Checked", "Pass", "Revise"] } };
  s.getRange("O5:O204").dataValidation = { rule: { type: "list", values: ["Not Reviewed", "Approved", "Revise", "Rejected"] } };
}

// Checks for Understanding
{
  const s = sheets["Checks for Understanding"];
  title(s, "Checks for Understanding", "Codex drafts at least one meaningful check for each instructional step unless the designer records an approved reason to omit it.", "V");
  const headers = ["Lesson", "Step", "Question ID", "Standard IDs", "Objective IDs", "Question Type", "Prompt", "Option A", "Option B", "Option C", "Option D", "Option E", "Option F", "Correct Answer(s)", "Correct Feedback", "Incorrect Feedback", "Source IDs", "Cognitive Level", "Designer Rationale", "Override Reason", "Approval Status", "Designer Notes"];
  const rows = [[1, "Step .2", "CFU-1-2-01", "", "", "Multiple Choice", "", "", "", "", "", "", "", "", "", "", "", "Understand", "", "", "Not Reviewed", ""]];
  writeTable(s, 4, headers, rows, "ChecksTable", {1: 10, 2: 10, 3: 18, 4: 18, 5: 18, 6: 20, 7: 48, 8: 32, 9: 32, 10: 32, 11: 32, 12: 32, 13: 32, 14: 20, 15: 40, 16: 40, 17: 18, 18: 18, 19: 38, 20: 36, 21: 18, 22: 34});
  s.getRange("B5:B204").dataValidation = { rule: { type: "list", values: ["Step .2", "Step .3", "Step .4"] } };
  s.getRange("F5:F204").dataValidation = { rule: { type: "list", values: ["Multiple Choice", "Multiple Select", "True/False", "Dropdown", "Short Answer", "Extended Response"] } };
  s.getRange("R5:R204").dataValidation = { rule: { type: "list", values: ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"] } };
  s.getRange("U5:U204").dataValidation = { rule: { type: "list", values: ["Not Reviewed", "Approved", "Revise", "Rejected"] } };
}

// Application Activities
{
  const s = sheets["Application Activities"];
  title(s, "Required .5 Application Activities", "Every lesson includes an authentic application. CTE modules require meaningful program-specific pathways.", "M");
  const headers = ["Lesson", "Activity ID", "Activity Title", "Purpose", "Standard IDs", "Objective IDs", "Directions", "Completion Mode", "Student Product or Evidence", "Estimated Minutes", "Feedback or Exemplar Plan", "Approval Status", "Designer Notes"];
  const rows = Array.from({length: 8}, (_, index) => [index + 1, `APP-${index + 1}-01`, "", "", "", "", "", "Designer Decision", "", 15, "", "Not Reviewed", ""]);
  writeTable(s, 4, headers, rows, "ApplicationsTable", {1: 10, 2: 18, 3: 30, 4: 42, 5: 18, 6: 18, 7: 55, 8: 28, 9: 36, 10: 15, 11: 42, 12: 18, 13: 34});
  s.getRange("H5:H204").dataValidation = { rule: { type: "list", values: ["Interactive Lesson", "Course Response", "Course Document Submission", "Instructor-Facilitated", "Combined", "Designer Decision"] } };
  s.getRange("L5:L204").dataValidation = { rule: { type: "list", values: ["Not Reviewed", "Approved", "Revise", "Rejected"] } };
}

// Program Scenarios
{
  const s = sheets["Program Scenarios"];
  title(s, "Program-Specific Application Scenarios", "A CTE scenario counts only when it uses an authentic decision, task, artifact, safety issue, tool, client, stakeholder, or workplace condition.", "N");
  const headers = ["Lesson", "Activity ID", "Program", "Scenario ID", "Situation", "Prompt 1", "Prompt 2", "Prompt 3", "Exemplar or Feedback", "Source IDs", "Subject-Matter Verification", "Coverage Quality", "Approval Status", "Designer Notes"];
  const rows = [[1, "APP-1-01", "", "SCN-1-001", "", "", "", "", "", "", "Needed", "Not Reviewed", "Not Reviewed", ""]];
  writeTable(s, 4, headers, rows, "ProgramScenariosTable", {1: 10, 2: 18, 3: 28, 4: 18, 5: 48, 6: 40, 7: 40, 8: 40, 9: 48, 10: 18, 11: 24, 12: 20, 13: 18, 14: 34});
  s.getRange("K5:K304").dataValidation = { rule: { type: "list", values: ["Needed", "Verified", "Not Applicable"] } };
  s.getRange("L5:L304").dataValidation = { rule: { type: "list", values: ["Not Reviewed", "Meaningful", "Superficial", "Needs Revision"] } };
  s.getRange("M5:M304").dataValidation = { rule: { type: "list", values: ["Not Reviewed", "Approved", "Revise", "Rejected"] } };
}

// Assessment Bank
{
  const s = sheets["Assessment Bank"];
  title(s, "Portable Assessment Bank", "This is the canonical source for Google Forms, Google Classroom, Canvas, and platform-neutral exports. Use portable item types by default.", "AA");
  const headers = ["Lesson", "Question ID", "Standard IDs", "Objective IDs", "Question Type", "Prompt", "Option A", "Option B", "Option C", "Option D", "Option E", "Option F", "Correct Answer(s)", "Points", "Correct Feedback", "Incorrect Feedback", "Source IDs", "Cognitive Level", "Randomization Group", "Required", "Google Forms Override", "Canvas Override", "Conversion Notes", "Reflection Item", "Approval Status", "Designer Notes", "Portability Check"];
  const rows = [[1, "A-1-01", "", "", "Multiple Choice", "", "", "", "", "", "", "", "", 1, "", "", "", "Understand", "L1-Core", "Yes", "", "", "", "No", "Not Reviewed", "", "Not Checked"]];
  writeTable(s, 4, headers, rows, "AssessmentBankTable", {1: 10, 2: 18, 3: 18, 4: 18, 5: 20, 6: 48, 7: 32, 8: 32, 9: 32, 10: 32, 11: 32, 12: 32, 13: 20, 14: 12, 15: 40, 16: 40, 17: 18, 18: 18, 19: 20, 20: 14, 21: 38, 22: 38, 23: 38, 24: 16, 25: 18, 26: 34, 27: 18});
  s.getRange("E5:E304").dataValidation = { rule: { type: "list", values: ["Multiple Choice", "Multiple Select", "True/False", "Dropdown", "Short Answer", "Extended Response", "Unscored Reflection"] } };
  s.getRange("R5:R304").dataValidation = { rule: { type: "list", values: ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"] } };
  s.getRange("T5:T304").dataValidation = { rule: { type: "list", values: ["Yes", "No"] } };
  s.getRange("X5:X304").dataValidation = { rule: { type: "list", values: ["Yes", "No"] } };
  s.getRange("Y5:Y304").dataValidation = { rule: { type: "list", values: ["Not Reviewed", "Approved", "Revise", "Rejected"] } };
  s.getRange("AA5:AA304").dataValidation = { rule: { type: "list", values: ["Not Checked", "Portable", "Approved Platform Difference", "Blocked"] } };
}

// Decisions & Issues
{
  const s = sheets["Decisions & Issues"];
  title(s, "Design Decisions and Unresolved Issues", "Use this log for assumptions, missing evidence, conflicts, approved exceptions, accessibility concerns, and platform limitations.", "K");
  const headers = ["Item ID", "Date", "Lesson or Scope", "Type", "Description", "Evidence or Source", "Recommendation", "Owner", "Status", "Decision or Resolution", "Approval Date"];
  const rows = [["D-001", null, "Course", "Open Question", "", "", "", "", "Open", "", null]];
  writeTable(s, 4, headers, rows, "DecisionsTable", {1: 14, 2: 14, 3: 18, 4: 22, 5: 48, 6: 38, 7: 42, 8: 20, 9: 16, 10: 45, 11: 16});
  s.getRange("D5:D204").dataValidation = { rule: { type: "list", values: ["Open Question", "Source Conflict", "Missing Resource", "Accessibility", "Pacing", "Assessment", "Program Coverage", "Platform", "Approved Exception"] } };
  s.getRange("I5:I204").dataValidation = { rule: { type: "list", values: ["Open", "In Progress", "Resolved", "Accepted Risk"] } };
  s.getRange("B5").format.numberFormat = "yyyy-mm-dd";
  s.getRange("K5").format.numberFormat = "yyyy-mm-dd";
}

const final = await SpreadsheetFile.exportXlsx(wb);
const outputPath = path.join(outputDir, "Module_Resource_Collection.xlsx");
await final.save(outputPath);
await final.save(resourcePath);

for (const [name, sheet] of Object.entries(sheets)) {
  const preview = await wb.render({ sheetName: name, autoCrop: "all", scale: 1, format: "png" });
  const safe = name.toLowerCase().replaceAll(" ", "-").replaceAll("&", "and");
  await fs.writeFile(path.join(previewDir, `${safe}.png`), new Uint8Array(await preview.arrayBuffer()));
}

const inspection = await wb.inspect({
  kind: "workbook,sheet,table",
  maxChars: 9000,
  tableMaxRows: 4,
  tableMaxCols: 8,
  tableMaxCellChars: 100,
});
await fs.writeFile(path.join(outputDir, "inspection.ndjson"), inspection.ndjson, "utf8");

const errors = await wb.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
});
await fs.writeFile(path.join(outputDir, "formula-errors.ndjson"), errors.ndjson, "utf8");

console.log(JSON.stringify({ outputPath, resourcePath, previewDir }, null, 2));
