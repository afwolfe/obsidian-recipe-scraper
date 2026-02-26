import argparse
from typing import Any
from urllib.request import urlopen
from recipe_scrapers import scrape_html


class SafeScraper:
    """Safe facade for AbstractScraper. Returns None when an attribute raises an Exception."""

    def __init__(self, scraper):
        self._scraper = scraper

    def __getattr__(self, name) -> Any:
        method = getattr(self._scraper, name, None)
        if callable(method):

            def safe_call(*args, **kwargs) -> Any:
                try:
                    return method(*args, **kwargs)
                except Exception:
                    return None

            return safe_call
        return method


def get_recipe(url: str) -> SafeScraper:
    html = urlopen(url).read().decode("utf-8")
    scraper = scrape_html(html, org_url=url)

    return SafeScraper(scraper)


def append_or_extend(list_to_add_to: list, to_add: str | list | None):
    if to_add is not None:
        list_to_add_to.extend(to_add if isinstance(to_add, list) else [to_add])


def get_tags(recipe: SafeScraper):
    tags = []
    append_or_extend(tags, recipe.cooking_method())
    append_or_extend(tags, recipe.category())
    append_or_extend(tags, recipe.cuisine())
    kw = recipe.keywords()
    if kw is not None:
        if isinstance(kw, str):
            kw = kw.split(",")
        append_or_extend(tags, kw)
    return sorted(tags)


def recipe_to_obsidian_markdown(recipe: SafeScraper):
    """
    Converts a scraped recipe to an Obsidian Markdown file.

    Args:
        recipe: AbstractScraper

    Returns:
        str: A Markdown string representing the recipe.
    """

    recipe = SafeScraper(recipe)
    markdown_lines: list[str | None] = []

    # Add frontmatter
    markdown_lines.append("---")
    markdown_lines.append("aliases:")
    markdown_lines.append(f"source: {recipe.url}")
    tags = get_tags(recipe)
    if tags:
        markdown_lines.append("tags:")
        for t in tags:
            markdown_lines.append(f"  - {t.replace(' ', '-').lower()}")

    rating = recipe.ratings()
    markdown_lines.append(f"rating: {rating}" if rating else None)
    markdown_lines.append("---")

    # Heading and description
    markdown_lines.append(f"# {recipe.title()}\n")
    markdown_lines.append(recipe.description())

    # Add info
    markdown_lines.append("\n")
    markdown_lines.append(
        f"Prep Time: {recipe.prep_time()}" if recipe.prep_time() else None
    )
    markdown_lines.append(
        f"Total Time: {recipe.total_time()}" if recipe.total_time() else None
    )
    markdown_lines.append(f"Servings: {recipe.yields()}" if recipe.yields() else None)

    markdown_lines.append("\n> Notes: \n")

    # Add ingredients as a checklist
    markdown_lines.append("## Ingredients")
    markdown_lines.append("#ingredients")
    markdown_lines.extend(f"- [ ] {ingredient}" for ingredient in recipe.ingredients())
    markdown_lines.append("\n")

    # Add directions by section
    markdown_lines.append("## Directions\n")

    for idx, step in enumerate(recipe.instructions_list()):
        markdown_lines.append(f"{idx + 1}. {step}")

    return "\n".join(line for line in markdown_lines if line is not None)


def write_recipe_to_file(recipe: SafeScraper, outfile=None):
    md_lines = recipe_to_obsidian_markdown(recipe)
    filename = outfile if outfile else f"{recipe.title()}.md"
    with open(filename, "w") as md_file:
        md_file.write(md_lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Converts scraped recipes to Obsidian Markdown"
    )
    parser.add_argument("url", type=str, help="The URL to process")
    parser.add_argument(
        "--outfile", type=str, required=False, help="The name of the file to write to"
    )
    args = parser.parse_args()

    recipe = get_recipe(args.url)
    write_recipe_to_file(recipe, args.outfile)
