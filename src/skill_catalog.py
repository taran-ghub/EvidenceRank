
from __future__ import annotations
import re


SKILL_CATALOG = {
    "python": {
        "label": "Python",
        "aliases": ["python", "python3"],
        "related": [
            "django",
            "flask",
            "fastapi",
            "pandas",
            "numpy",
        ],
    },
    "java": {
        "label": "Java",
        "aliases": ["java", "java 8", "java 11", "java 17"],
        "related": [
            "spring",
            "spring boot",
            "hibernate",
            "maven",
        ],
    },
    "javascript": {
        "label": "JavaScript",
        "aliases": ["javascript", "js", "ecmascript"],
        "related": [
            "typescript",
            "react",
            "node.js",
            "express.js",
        ],
    },
    "typescript": {
        "label": "TypeScript",
        "aliases": ["typescript", "ts"],
        "related": ["javascript", "react", "angular", "node.js"],
    },
    "cpp": {
        "label": "C++",
        "aliases": ["c++", "cpp"],
        "related": ["object oriented programming", "stl"],
    },
    "csharp": {
        "label": "C#",
        "aliases": ["c#", "c sharp", "csharp"],
        "related": [".net", "asp.net"],
    },
        "golang": {
        "label": "Go",
        "aliases": ["golang", "go language", "go"],
        "related": [
            "microservices",
            "backend development",
        ],
    },
    "php": {
        "label": "PHP",
        "aliases": ["php"],
        "related": ["laravel", "wordpress"],
    },
    "html": {
        "label": "HTML",
        "aliases": ["html", "html5"],
        "related": ["web development", "frontend development"],
    },
    "css": {
        "label": "CSS",
        "aliases": ["css", "css3"],
        "related": [
            "sass",
            "scss",
            "tailwind css",
            "bootstrap",
        ],
    },
    "react": {
        "label": "React",
        "aliases": ["react", "react.js", "reactjs"],
        "related": [
            "next.js",
            "redux",
            "frontend development",
            "component based ui",
        ],
    },
    "angular": {
        "label": "Angular",
        "aliases": ["angular", "angular.js", "angularjs"],
        "related": [
            "typescript",
            "rxjs",
            "frontend development",
        ],
    },
    "vue": {
        "label": "Vue.js",
        "aliases": ["vue", "vue.js", "vuejs"],
        "related": ["frontend development", "pinia", "vuex"],
    },
    "nextjs": {
        "label": "Next.js",
        "aliases": ["next.js", "nextjs"],
        "related": [
            "react",
            "server side rendering",
            "frontend development",
        ],
    },
    "nodejs": {
        "label": "Node.js",
        "aliases": ["node.js", "nodejs", "node js"],
        "related": [
            "express",
            "express.js",
            "javascript backend",
            "backend development",
            "rest api",
        ],
    },
    "express": {
        "label": "Express.js",
        "aliases": ["express", "express.js", "expressjs"],
        "related": ["node.js", "rest api", "backend development"],
    },
    "django": {
        "label": "Django",
        "aliases": ["django", "django rest framework", "drf"],
        "related": ["python", "backend development", "rest api"],
    },
    "flask": {
        "label": "Flask",
        "aliases": ["flask"],
        "related": ["python", "backend development", "rest api"],
    },
    "fastapi": {
        "label": "FastAPI",
        "aliases": ["fastapi", "fast api"],
        "related": ["python", "backend development", "rest api"],
    },
    "springboot": {
        "label": "Spring Boot",
        "aliases": ["spring boot", "springboot"],
        "related": ["java", "spring", "microservices", "rest api"],
    },
    "dotnet": {
        "label": ".NET",
        "aliases": [".net", "dotnet", "asp.net", "asp.net core"],
        "related": ["c#", "backend development", "web api"],
    },
    "rest_api": {
        "label": "REST API Development",
        "aliases": [
            "rest api",
            "restful api",
            "restful services",
            "web api",
        ],
        "related": [
            "backend development",
            "node.js",
            "express",
            "django",
            "flask",
            "fastapi",
        ],
    },
    "graphql": {
        "label": "GraphQL",
        "aliases": ["graphql", "graph ql"],
        "related": ["api development", "apollo"],
    },
    "microservices": {
        "label": "Microservices",
        "aliases": [
            "microservices",
            "microservice architecture",
        ],
        "related": [
            "distributed systems",
            "docker",
            "kubernetes",
            "backend development",
        ],
    },
    "sql": {
        "label": "SQL",
        "aliases": ["sql", "structured query language"],
        "related": ["relational database", "database queries"],
    },
    "mysql": {
        "label": "MySQL",
        "aliases": ["mysql", "my sql"],
        "related": ["sql", "relational database"],
    },
    "postgresql": {
        "label": "PostgreSQL",
        "aliases": ["postgresql", "postgres", "postgre sql"],
        "related": ["sql", "relational database"],
    },
    "mongodb": {
        "label": "MongoDB",
        "aliases": ["mongodb", "mongo db", "mongoose"],
        "related": [
            "nosql",
            "document database",
            "database development",
        ],
    },
    "redis": {
        "label": "Redis",
        "aliases": ["redis"],
        "related": ["caching", "in memory database"],
    },
    "git": {
        "label": "Git",
        "aliases": ["git", "github", "gitlab", "bitbucket"],
        "related": [
            "version control",
            "source control",
            "collaborative development",
        ],
    },
    "docker": {
        "label": "Docker",
        "aliases": ["docker", "dockerfile", "docker compose"],
        "related": ["containers", "containerization", "devops"],
    },
    "kubernetes": {
        "label": "Kubernetes",
        "aliases": ["kubernetes", "k8s"],
        "related": [
            "container orchestration",
            "docker",
            "devops",
        ],
    },
    "aws": {
        "label": "Amazon Web Services",
        "aliases": ["aws", "amazon web services"],
        "related": [
            "ec2",
            "s3",
            "lambda",
            "cloud computing",
        ],
    },
    "azure": {
        "label": "Microsoft Azure",
        "aliases": ["azure", "microsoft azure"],
        "related": ["cloud computing", "azure functions"],
    },
    "gcp": {
        "label": "Google Cloud Platform",
        "aliases": ["gcp", "google cloud", "google cloud platform"],
        "related": ["cloud computing", "cloud run"],
    },
    "cicd": {
        "label": "CI CD",
        "aliases": [
            "ci/cd",
            "cicd",
            "continuous integration",
            "continuous deployment",
        ],
        "related": [
            "github actions",
            "jenkins",
            "devops",
        ],
    },
    "linux": {
        "label": "Linux",
        "aliases": ["linux", "ubuntu", "unix"],
        "related": ["shell scripting", "bash", "operating systems"],
    },
    "testing": {
        "label": "Software Testing",
        "aliases": [
            "software testing",
            "unit testing",
            "integration testing",
            "automated testing",
        ],
        "related": [
            "pytest",
            "jest",
            "junit",
            "selenium",
        ],
    },
    "machine_learning": {
        "label": "Machine Learning",
        "aliases": ["machine learning", "ml"],
        "related": [
            "scikit-learn",
            "tensorflow",
            "pytorch",
            "predictive modeling",
        ],
    },
    "data_analysis": {
        "label": "Data Analysis",
        "aliases": [
            "data analysis",
            "data analytics",
            "exploratory data analysis",
            "eda",
        ],
        "related": ["pandas", "numpy", "sql", "visualization"],
    },
    "communication": {
        "label": "Communication",
        "aliases": [
            "communication",
            "communication skills",
            "written communication",
            "verbal communication",
        ],
        "related": [
            "presented",
            "documented",
            "stakeholder communication",
        ],
    },
    "teamwork": {
        "label": "Teamwork",
        "aliases": [
            "teamwork",
            "team player",
            "collaboration",
        ],
        "related": [
            "worked with a team",
            "cross functional team",
            "group project",
        ],
    },
    "problem_solving": {
        "label": "Problem Solving",
        "aliases": [
            "problem solving",
            "analytical skills",
            "critical thinking",
        ],
        "related": [
            "optimized",
            "debugged",
            "resolved",
            "troubleshooting",
        ],
    },
}


def alias_appears_in_text(
    alias: str,
    text: str,
) -> bool:
    """
    Match a skill as a complete term.

    This prevents short aliases such as go, js, ts, and ml
    from matching inside unrelated words.
    """
    normalized_alias = alias.casefold().strip()
    normalized_text = text.casefold()

    escaped_alias = re.escape(normalized_alias)
    escaped_alias = escaped_alias.replace(
        r"\ ",
        r"[\s-]+",
    )

    alphanumeric_alias = re.sub(
        r"[^a-z0-9]",
        "",
        normalized_alias,
    )

    is_short_alias = len(alphanumeric_alias) <= 3

    if is_short_alias:
        left_boundary = r"(?<![\w.])"
    else:
        left_boundary = r"(?<!\w)"

    plural_suffix = ""

    if normalized_alias.endswith(
        ("api", "service", "skill", "system")
    ):
        plural_suffix = "s?"

    pattern = (
        left_boundary
        + escaped_alias
        + plural_suffix
        + r"(?!\w)"
    )

    return bool(
        re.search(
            pattern,
            normalized_text,
            flags=re.IGNORECASE,
        )
    )


def find_catalog_skills(text: str) -> list[dict]:
    matches: list[dict] = []

    for skill_id, skill_data in SKILL_CATALOG.items():
        matched_aliases = [
            alias
            for alias in skill_data["aliases"]
            if alias_appears_in_text(alias, text)
        ]

        if matched_aliases:
            matches.append(
                {
                    "skill_id": skill_id,
                    "label": skill_data["label"],
                    "matched_aliases": matched_aliases,
                    "aliases": skill_data["aliases"],
                    "related": skill_data["related"],
                }
            )

    return matches
    normalized_text = text.casefold()
    matches: list[dict] = []

    for skill_id, skill_data in SKILL_CATALOG.items():
        matched_aliases = []

        for alias in skill_data["aliases"]:
            if alias.casefold() in normalized_text:
                matched_aliases.append(alias)

        if matched_aliases:
            matches.append(
                {
                    "skill_id": skill_id,
                    "label": skill_data["label"],
                    "matched_aliases": matched_aliases,
                    "aliases": skill_data["aliases"],
                    "related": skill_data["related"],
                }
            )

    return matches


def get_skill(skill_id: str) -> dict | None:
    return SKILL_CATALOG.get(skill_id)