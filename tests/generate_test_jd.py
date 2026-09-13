from pathlib import Path

import pymupdf


OUTPUT_PATH = Path("data/incoming/test_job_description.pdf")


JD_TEXT = """
Junior Full Stack Developer Intern

ABOUT THE ROLE

We are looking for a developer who can help build and maintain
a web-based product with our engineering team.

KEY RESPONSIBILITIES

- Build responsive user interfaces for the platform.
- Develop RESTful APIs and backend services.
- Work with developers to debug and improve application performance.
- Write maintainable and tested software.

REQUIRED SKILLS

- Strong knowledge of JavaScript, HTML, and CSS.
- Hands-on experience with React and Node.js.
- Experience working with MongoDB or PostgreSQL.
- Familiarity with Git and collaborative version control.
- Candidates must have good problem-solving and communication skills.
- Bachelor degree in Computer Science or a related engineering field.
- At least 1 year of project or internship experience.

PREFERRED QUALIFICATIONS

- Experience with Docker and AWS would be a plus.
- Familiarity with automated testing is preferred.
- Knowledge of TypeScript is nice to have.
"""


def main() -> None:
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    document = pymupdf.open()
    page = document.new_page(
        width=595,
        height=842,
    )

    remaining_space = page.insert_textbox(
        pymupdf.Rect(50, 40, 545, 810),
        JD_TEXT,
        fontsize=10.5,
        fontname="helv",
        lineheight=1.2,
    )

    if remaining_space < 0:
        raise RuntimeError(
            "The test JD did not fit on the PDF page."
        )

    document.save(OUTPUT_PATH)
    document.close()

    print(f"Created: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()