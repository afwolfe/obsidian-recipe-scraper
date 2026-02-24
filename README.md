# obsidian-recipe-scraper

Uses [hhursev/recipe-scrapers](https://github.com/hhursev/recipe-scrapers) to parse recipes into Markdown for use in Obsidian or elsewhere.

## Why?

[RecipeMD](https://recipemd.org/) exists as a standard for representing recipes in Markdown and [recipemd-extract](https://github.com/RecipeMD/recipemd-extract) can scrape recipes with `recipe-scrapers`. Why build another tool?

The template in this tool is loosely based on the one described in this Obsidian Forum post and has some advantages over pure Markdown: <https://forum.obsidian.md/t/obsidian-as-recipe-manager-and-shopping-list-tutorial/40799>

* Ingredients are written with checkboxes and tagged with `#ingredients` for integration with the [Checklist plugin](https://github.com/delashum/obsidian-checklist-plugin)
* Frontmatter tags enable automatic organization of new recipes

## Usage

```shell
python install -e . # Install dependencies
python main.py $RECIPE_URL [--outfile path/to/file.md] # Convert the provided recipe to Markdown
```
