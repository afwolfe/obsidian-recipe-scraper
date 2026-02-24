import argparse
from urllib.request import urlopen
from recipe_scrapers import AbstractScraper, scrape_html


def get_recipe(url: str):
    html = urlopen(url).read().decode("utf-8")
    scraper = scrape_html(html, org_url=url)

    return scraper


def append_or_extend(list_to_add_to: list, to_add: str | list):
    if to_add is not None:
        list_to_add_to.extend(to_add if isinstance(to_add, list) else [to_add])


def get_tags(recipe: AbstractScraper):
    recipe_json = recipe.to_json()
    tags = []
    append_or_extend(tags, recipe_json.get("cookingMethod"))
    append_or_extend(tags, recipe_json.get("recipeCategory"))
    append_or_extend(tags, recipe_json.get("recipeCuisine"))
    kw = recipe_json.get("keywords")
    if kw is not None:
        if isinstance(kw, str):
            kw = kw.split(",")
        append_or_extend(tags, kw)
    return tags


def recipe_to_obsidian_markdown(recipe: AbstractScraper):
    """
    Converts a scraped recipe to an Obsidian Markdown file.

    Args:
        recipe: AbstractScraper

    Returns:
        str: A Markdown string representing the recipe.
    """

    markdown_lines = []

    # Add frontmatter
    markdown_lines.append("---")
    markdown_lines.append("aliases:")
    markdown_lines.append(f"source: {recipe.url}")
    tags = get_tags(recipe)
    markdown_lines.append(
        f"tags: {','.join([t.replace(' ', '-').lower() for t in tags])}"
    )
    markdown_lines.append(f"rating: {recipe.ratings()}")
    markdown_lines.append("---")

    # Heading and description
    markdown_lines.append(f"# {recipe.title()}\n")
    markdown_lines.append(recipe.description())

    # Add info
    markdown_lines.append(f"Prep Time: {recipe.prep_time()}")
    markdown_lines.append(f"Total Time: {recipe.total_time()}")
    markdown_lines.append(f"Servings: {recipe.yields()}")

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

    return "\n".join(markdown_lines)


def write_recipe_to_file(recipe, outfile=None):
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
