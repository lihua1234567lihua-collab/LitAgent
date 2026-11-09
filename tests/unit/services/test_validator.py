from agent.step_validator import validate_paper_search


def paper(title: str, year: int, openalex_id: str) -> dict:
    return {
        "title": title,
        "publication_year": year,
        "openalex_id": openalex_id,
    }


def test_paper_count_and_year_pass():
    results = [
        paper("Paper A", 2020, "W1"),
        paper("Paper B", 2021, "W2"),
        paper("Paper C", 2024, "W3"),
    ]

    result = validate_paper_search(
        "Find at least 3 papers from 2020-2024",
        results,
    )

    assert result["passed"] is True
    assert result["source"] == "deterministic"
    assert result["failed_constraints"] == []


def test_paper_count_failure():
    results = [
        paper("Paper A", 2020, "W1"),
        paper("Paper B", 2021, "W2"),
    ]

    result = validate_paper_search(
        "Find at least 3 papers",
        results,
    )

    assert result["passed"] is False
    assert any(
        item["type"] == "paper_count"
        for item in result["failed_constraints"]
    )


def test_year_failure():
    results = [
        paper("Paper A", 2018, "W1"),
        paper("Paper B", 2021, "W2"),
    ]

    result = validate_paper_search(
        "Find papers from 2020-2024",
        results,
    )

    assert result["passed"] is False
    assert any(
        item["type"] == "paper_year"
        for item in result["failed_constraints"]
    )


def test_duplicate_papers_failure():
    results = [
        paper("Paper A", 2020, "W1"),
        paper("Paper A duplicate", 2020, "W1"),
    ]

    result = validate_paper_search(
        "Find papers",
        results,
    )

    assert result["passed"] is False
    assert any(
        item["type"] == "duplicate_papers"
        for item in result["failed_constraints"]
    )


def test_missing_required_field_failure():
    results = [
        {
            "title": "Paper A",
            "publication_year": 2020,
        }
    ]

    result = validate_paper_search(
        "Find papers",
        results,
    )

    assert result["passed"] is False
    assert any(
        item["type"] == "required_field"
        for item in result["failed_constraints"]
    )