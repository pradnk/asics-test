const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, BorderStyle, WidthType, UnderlineType
} = require('docx');
const fs = require('fs');

// ─── Edit these variables for each RTI application ───────────────────────────

const authority = "[Department / Public Authority Name]";
const division  = "[Division / Wing]";
const officeAddress = "[Office Address, City – PIN, State, India]";

const subjectLine = "[Brief description of subject and time period]";
const infoIntro   = "[Subject/location], for the period [YYYY to YYYY]";
const transferAuthorities = "[alternate authority 1], [alternate authority 2]";

const infoRequests = [
  "Please provide [specific information request 1].",
  "Please provide [specific information request 2].",
  "Please provide [specific information request 3].",
  "Please provide [specific information request 4].",
  "Please provide [specific information request 5].",
];

const applicantName    = "[Your Full Name]";
const applicantAddress = "[Your Complete Address]";
const applicantMobile  = "[Your Mobile Number]";
const applicantEmail   = "[Your Email Address]";
const date  = "16 June 2026";
const place = "Bengaluru";

const outputFile = "RTI_Application_Output.docx";

// ─────────────────────────────────────────────────────────────────────────────

const noBorder  = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: noBorder, bottom: noBorder, left: noBorder, right: noBorder };

function cell(text, width, bold = false) {
  return new TableCell({
    borders: noBorders,
    width: { size: width, type: WidthType.DXA },
    margins: { top: 60, bottom: 60, left: 0, right: 80 },
    children: [new Paragraph({
      children: [new TextRun({ text, size: 24, bold, font: "Arial" })]
    })]
  });
}

function labelRow(label, value) {
  return new TableRow({ children: [cell(label, 2200, true), cell(value, 7160)] });
}

function sectionHeading(text) {
  return new Paragraph({
    spacing: { before: 280, after: 120 },
    children: [new TextRun({ text, bold: true, size: 24, font: "Arial" })]
  });
}

function para(text, opts = {}) {
  return new Paragraph({
    spacing: { before: 80, after: 80 },
    children: [new TextRun({ text, size: 24, font: "Arial", ...opts })]
  });
}

function twoColTable(rows) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2200, 7160],
    rows,
  });
}

const doc = new Document({
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [

      // Title — bold + underlined, centred
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 160 },
        children: [new TextRun({
          text: "APPLICATION UNDER RIGHT TO INFORMATION ACT, 2005",
          bold: true, size: 28, font: "Arial",
          underline: { type: UnderlineType.SINGLE }
        })]
      }),

      // Subtitle — italics, centred
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 360 },
        children: [new TextRun({ text: "Section 6(1) of the RTI Act, 2005", italics: true, size: 24, font: "Arial" })]
      }),

      // TO
      sectionHeading("TO"),
      para("The Public Information Officer (PIO)"),
      para(authority),
      para(division),
      para(officeAddress),

      // APPLICANT DETAILS
      sectionHeading("APPLICANT DETAILS"),
      twoColTable([
        labelRow("Name",    ": " + applicantName),
        labelRow("Address", ": " + applicantAddress),
        labelRow("Mobile",  ": " + applicantMobile),
        labelRow("Email",   ": " + applicantEmail),
        labelRow("Date",    ": " + date),
      ]),

      // SUBJECT
      sectionHeading("SUBJECT"),
      para(subjectLine),

      // PAYMENT OF FEE
      sectionHeading("PAYMENT OF FEE"),
      para("Application fee of Rs. 10/- is enclosed as Indian Postal Order / Demand Draft / Court Fee Stamp as applicable."),
      para("Below Poverty Line (BPL) applicants are exempted from fee as per Section 7(5) of the RTI Act. [If applicable, BPL card details: ____________]"),

      // INFORMATION SOUGHT
      sectionHeading("INFORMATION SOUGHT"),
      para(`Under Section 6(1) of the Right to Information Act, 2005, I hereby request the following information relating to ${infoIntro}:`),

      new Paragraph({ spacing: { before: 120, after: 0 }, children: [] }),

      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [600, 8760],
        rows: infoRequests.map((text, i) => new TableRow({
          children: [
            new TableCell({
              borders: noBorders,
              width: { size: 600, type: WidthType.DXA },
              margins: { top: 80, bottom: 80, left: 0, right: 120 },
              children: [new Paragraph({ children: [new TextRun({ text: `${i + 1}.`, bold: true, size: 24, font: "Arial" })] })]
            }),
            new TableCell({
              borders: noBorders,
              width: { size: 8760, type: WidthType.DXA },
              margins: { top: 80, bottom: 80, left: 0, right: 0 },
              children: [new Paragraph({ children: [new TextRun({ text, size: 24, font: "Arial" })] })]
            })
          ]
        }))
      }),

      // TRANSFER CLAUSE
      sectionHeading("TRANSFER CLAUSE (Section 6(3))"),
      para(`If the requested information is not held by ${authority} but by another public authority (such as ${transferAuthorities}), I request that this application be transferred to the concerned authority as per Section 6(3) of the RTI Act, 2005, and I be informed accordingly.`),

      // DECLARATION
      sectionHeading("DECLARATION"),
      para("I state that the information sought does not fall within the restrictions contained in Section 8 of the RTI Act, 2005, and to the best of my knowledge it pertains to your authority."),

      // Date / Place table
      new Paragraph({ spacing: { before: 300, after: 0 }, children: [] }),
      twoColTable([
        labelRow("Date",  ": " + date),
        labelRow("Place", ": " + place),
      ]),

      // Signature block
      new Paragraph({ spacing: { before: 360, after: 80 }, children: [new TextRun({ text: "Signature of Applicant", size: 24, font: "Arial" })] }),
      new Paragraph({ spacing: { before: 0, after: 60 }, children: [new TextRun({ text: applicantName, bold: true, size: 24, font: "Arial" })] }),
      para(applicantAddress),
      para(applicantMobile + " | " + applicantEmail),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(outputFile, buf);
  console.log("Done. File saved as " + outputFile);
});
