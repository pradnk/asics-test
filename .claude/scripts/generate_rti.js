const { Document, Packer, Paragraph, TextRun, AlignmentType, UnderlineType } = require('docx');
const fs = require('fs');

const authority = "BBMP Parks & Horticulture Wing";
const officeAddress = "BBMP Head Office, N.R. Square, Bengaluru – 560002";

const infoRequests = [
  "Provide certified copies of all sanction orders, approval letters, and administrative orders related to the establishment or development of the new park in BTM Layout 1st Stage, Bengaluru, in 2025.",
  "Provide the name(s) and designation(s) of the officer(s) who sanctioned and approved the new park in BTM Layout 1st Stage, Bengaluru, in 2025.",
  "Provide certified copies of all file notings, noting sheets, and internal correspondence related to the approval of the new park in BTM Layout 1st Stage, Bengaluru, in 2025.",
  "Provide certified copies of all work orders, tender documents, bid evaluation reports, and contracts issued for the development or construction of the new park in BTM Layout 1st Stage, Bengaluru, in 2025.",
  "Provide details of the estimated cost and actual expenditure incurred for the development of the new park in BTM Layout 1st Stage, Bengaluru, in 2025, along with copies of expenditure statements and payment vouchers.",
  "Provide certified copies of any land allotment orders, land transfer documents, or no-objection certificates related to the land on which the new park in BTM Layout 1st Stage, Bengaluru, has been developed.",
  "Provide the survey number(s), extent of land, and ownership details of the plot earmarked or allotted for the new park in BTM Layout 1st Stage, Bengaluru."
];

const applicantName = "[Your Full Name]";
const applicantAddress = "[Your Complete Address]";
const applicantMobile = "[Your Mobile Number]";
const applicantEmail = "[Your Email Address]";
const date = "16 June 2026";
const place = "Bengaluru";

const doc = new Document({
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 240 },
        children: [new TextRun({ text: "APPLICATION UNDER THE RIGHT TO INFORMATION ACT, 2005", bold: true, size: 28 })]
      }),
      new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: "To,", size: 24 })] }),
      new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: "The Central/State Public Information Officer (CPIO/SPIO)", bold: true, size: 24 })] }),
      new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: authority, size: 24 })] }),
      new Paragraph({ spacing: { after: 240 }, children: [new TextRun({ text: officeAddress, size: 24 })] }),
      new Paragraph({
        spacing: { after: 240 },
        children: [
          new TextRun({ text: "Subject: ", bold: true, size: 24 }),
          new TextRun({ text: "Application under Section 6(1) of the Right to Information Act, 2005 — Seeking information regarding approval of the new park in BTM Layout 1st Stage, Bengaluru, in 2025", size: 24, underline: { type: UnderlineType.SINGLE } })
        ]
      }),
      new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: "Sir/Madam,", size: 24 })] }),
      new Paragraph({
        spacing: { after: 240 },
        children: [new TextRun({ text: "I am an Indian citizen seeking information under the Right to Information Act, 2005.", size: 24 })]
      }),
      new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: "Kindly provide the following information:", bold: true, size: 24 })] }),
      ...infoRequests.map((req, i) =>
        new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: `${i + 1}. ${req}`, size: 24 })] })
      ),
      new Paragraph({
        spacing: { before: 240, after: 120 },
        children: [new TextRun({ text: "For each item above, kindly provide certified copies of the relevant records, files, correspondence, file notings, approvals, reports, registers, orders, and other documents available with the public authority, wherever applicable.", size: 24 })]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun({ text: "If any of the requested information is held by another public authority, kindly transfer the relevant portion of this application under Section 6(3) of the RTI Act.", size: 24 })]
      }),
      new Paragraph({
        spacing: { after: 240 },
        children: [new TextRun({ text: "I prefer to receive the information in electronic format wherever available.", size: 24 })]
      }),
      new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: "Applicant Details", bold: true, size: 24, underline: { type: UnderlineType.SINGLE } })] }),
      new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: `Name: ${applicantName}`, size: 24 })] }),
      new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: `Address: ${applicantAddress}`, size: 24 })] }),
      new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: `Mobile: ${applicantMobile}`, size: 24 })] }),
      new Paragraph({ spacing: { after: 240 }, children: [new TextRun({ text: `Email: ${applicantEmail}`, size: 24 })] }),
      new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: "Fee Payment Details:", bold: true, size: 24 })] }),
      new Paragraph({ spacing: { after: 240 }, children: [new TextRun({ text: "[Online Payment Reference / IPO Number / Other]", size: 24, color: "888888" })] }),
      new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: `Date: ${date}`, size: 24 })] }),
      new Paragraph({ spacing: { after: 240 }, children: [new TextRun({ text: `Place: ${place}`, size: 24 })] }),
      new Paragraph({ children: [new TextRun({ text: "Signature: _______________________", size: 24 })] }),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("RTI_Application_BTM_Park_Approval.docx", buf);
  console.log("Done. File saved as RTI_Application_MG_Road_Contractors.docx");
});
