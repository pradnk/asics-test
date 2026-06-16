---
name: rti-generator
description: >
  Generate a filled RTI (Right to Information) application as a .docx file based on the user's subject description.
  Use this skill whenever the user mentions RTI, Right to Information, filing an RTI application, or wants to request
  government records/documents. Trigger on phrases like "file an RTI", "RTI for", "raise RTI", "RTI application about",
  or any request involving obtaining government information, contractor details, public expenditure, government decisions,
  or official records through the RTI Act 2005. Also trigger when a user describes wanting to know about a government
  scheme, public works project, policy implementation, or public authority decision and the word "RTI" appears anywhere
  in the conversation.
---

# RTI Application Generator

You generate a professionally filled RTI application under Section 6(1) of the Right to Information Act, 2005, based on the user's brief description of what information they want.

## Your workflow

### Step 1: Extract key information from the user's description

Parse the user's subject to identify:
- **What** they want to know (contractors, expenditure, files, decisions, inspection reports, approvals, etc.)
- **Where** (specific address, district, project name, scheme name, file number if given)
- **When** (time period — default to "last 5 years" if not specified)
- **Which authority** holds this information (see department mapping below)

### Step 2: Identify the right public authority

Map the subject to the most likely department. If ambiguous, pick the most likely one and note that the application includes a Section 6(3) transfer request to handle redirection.

| Subject area | Public authority |
|---|---|
| Roads, bridges, footpaths | Public Works Department (PWD) / Municipal Corporation Roads Dept |
| Water supply, sewage, drainage | Municipal Corporation / Water Board / BWSSB / HMWSSB |
| Building permits, land use | Local Body / Development Authority / BBMP / GHMC |
| Government contracts, tenders | Concerned department + District Collector office |
| Schools, education schemes | State Education Department / District Education Officer |
| Public health, hospitals | State Health Department / Civil Surgeon Office |
| Police, crime records | State Police Department / Superintendent of Police office |
| Land records, registration | Revenue Department / Sub-Registrar Office |
| Central government schemes | Relevant Ministry / District Collectorate |
| Pensions, social welfare | State Social Welfare Department |

### Step 3: Ask for applicant details (if not already provided)

Before generating the document, ask:
> "To complete the RTI application, I need a few details:
> 1. Your full name
> 2. Your complete postal address
> 3. Mobile number
> 4. Email address
> 5. Date and place (or I'll use today's date and city from your address)"

If the user says to use placeholders, use:
- Name: [Your Full Name]
- Address: [Your Complete Address]
- Mobile: [Your Mobile Number]
- Email: [Your Email Address]

### Step 4: Generate specific RTI information requests

This is the most important step. RTI questions must be about **records and documents**, not opinions or explanations.

**RTI drafting rules:**
- Ask for specific documents: work orders, tenders, contracts, registers, file notings, inspection reports, expenditure statements, sanction orders, completion certificates, correspondence
- Ask for names/designations of officers (not explanations of decisions)
- Use specific date ranges
- Never ask "why" or "how" — rephrase as "provide copies of all file notings/orders/approvals related to..."
- Each point should be independently answerable
- Aim for 5–8 well-targeted questions

**Example transformation:**

User says: "Who were the contractors for the road at XYZ?"

RTI generates:
1. Provide a list of all contractors/firms awarded contracts for construction or maintenance of the road at [XYZ address] from [year] to [year], along with the contract value for each.
2. Provide certified copies of all work orders, tender documents, and agreements issued for road work at [XYZ address] during the said period.
3. Provide copies of all completion certificates and inspection reports for road work at [XYZ address] during the said period.
4. Provide the name and designation of the officer who inspected and certified the completion of each work.
5. Provide copies of all expenditure statements and payment vouchers for road work at [XYZ address] during the said period.

Add domain-specific requests as appropriate:
- For expenditure: utilization certificates, audit reports
- For land/property: mutation records, survey maps, encumbrance certificates
- For government schemes: beneficiary lists, disbursement records, eligibility criteria applied
- For personnel/appointments: appointment orders, qualification records, seniority lists

### Step 5: Build the .docx file

- Read `.claude/assets/rti_template.md` to get the canonical document structure and boilerplate text. The generated document must follow this template exactly — same section order, same boilerplate sentences (opening, certified copies clause, Section 6(3) transfer clause, electronic format preference).
- Copy the script at `.claude/scripts/rti_generator_template.js` to `.claude/scripts/generate_rti_application.js` and edit the variables at the top of the **copied** script at `.claude/scripts/rti_generator.js`: 
  - `authority` — the public authority name
  - `officeAddress` — the PIO office address
  - `infoRequests` — array of 5–8 RTI questions for this specific request
  - `applicantName`, `applicantAddress`, `applicantMobile`, `applicantEmail` — from user or placeholders
  - The output filename in `fs.writeFileSync(...)` — use `RTI_Application_<short_topic>.docx`
- Run the script with: `NODE_PATH=/Users/pradeep/.nvm/versions/node/v24.14.0/lib/node_modules node .claude/scripts/generate_rti_application.js`
- If `docx` is not installed globally, install it with `npm install -g docx` and then run the script.

### Template updates

If a generated RTI application requires a structural change, new section, or new boilerplate that isn't in `.claude/assets/rti_template.md`, **ask the user for consent before updating the template file**. Only update it after explicit approval.

## Output

After generating the file:
1. Save as `RTI_Application_<topic>.docx`
2. Present it with `present_files`
3. Briefly note:
   - Which department to address it to
   - RTI fee: ₹10 for Central govt; state fees vary (user should confirm their state's schedule)
   - They should attach fee payment proof when submitting
