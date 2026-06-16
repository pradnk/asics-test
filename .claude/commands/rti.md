# RTI Application Generator

Generate a filled RTI application under Section 6(1) of the Right to Information Act, 2005.

## Usage

```
/rti <brief description of what you want to know>
```

**Examples:**
- `/rti Who were the contractors for the road at MG Road, Bengaluru for the last 10 years`
- `/rti Expenditure on Aarogya Setu scheme implementation in Karnataka 2020-2023`
- `/rti Building approval status for plot at Survey No. 45, Whitefield, Bengaluru`

## What this command does

1. Parses your description to identify what records you need, which department holds them, and the relevant time period
2. Maps the subject to the correct public authority (PWD, BBMP, Revenue Dept, etc.)
3. Generates 5–8 specific, document-focused RTI questions (following RTI Act best practices — no "why/how", only record requests)
4. Asks for your applicant details (name, address, mobile, email) if not already provided
5. Produces a ready-to-submit `.docx` RTI application

## Instructions to Claude

When this command is invoked:

- The user's input (everything after `/rti`) is their subject description.
- Follow the `rti` skill exactly: extract what/where/when, identify the public authority, generate specific document-request questions, collect applicant details, build and save the `.docx`, then present it.
- If the subject is ambiguous (multiple possible departments), pick the most likely one and include a Section 6(3) transfer clause.
- If no time period is specified, default to "last 5 years".
- If no applicant details are provided, ask for them before generating the document. If the user says "use placeholders", fill with bracketed placeholders.