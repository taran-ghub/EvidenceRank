from pathlib import Path

import pymupdf


OUTPUT_DIRECTORY = Path("data/incoming")
OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)


RESUME_TEXT = """
AARAV SHARMA
Junior Full Stack Developer

SKILLS
Python, JavaScript, React, Node.js, Express, MongoDB, Git

PROJECTS
Inventory Management Platform
Built a React dashboard for managing product inventory.
Developed REST APIs using Node.js and Express.
Stored product and customer data in MongoDB.
Used Git and GitHub for version control and collaboration.

EXPERIENCE
Software Development Intern
Worked with a three-member engineering team.
Reduced API response time by 30 percent through query optimization.

EDUCATION
Bachelor of Technology in Computer Science
"""


def create_normal_resume() -> None:
    document = pymupdf.open()
    page = document.new_page(width=595, height=842)

    page.insert_textbox(
        pymupdf.Rect(55, 50, 540, 790),
        RESUME_TEXT,
        fontsize=11,
        fontname="helv",
        lineheight=1.25,
    )

    output_path = OUTPUT_DIRECTORY / "normal_resume.pdf"
    document.save(output_path)
    document.close()

    print(f"Created: {output_path}")


def create_scanned_resume() -> None:
    source_document = pymupdf.open()
    source_page = source_document.new_page(width=595, height=842)

    source_page.insert_textbox(
        pymupdf.Rect(55, 50, 540, 790),
        RESUME_TEXT,
        fontsize=11,
        fontname="helv",
        lineheight=1.25,
    )

    image = source_page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
    image_bytes = image.tobytes("png")
    source_document.close()

    scanned_document = pymupdf.open()
    scanned_page = scanned_document.new_page(width=595, height=842)

    scanned_page.insert_image(
        scanned_page.rect,
        stream=image_bytes,
    )

    output_path = OUTPUT_DIRECTORY / "scanned_resume.pdf"
    scanned_document.save(output_path)
    scanned_document.close()

    print(f"Created: {output_path}")


if __name__ == "__main__":
    create_normal_resume()
    create_scanned_resume()