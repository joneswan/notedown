import os

import nose.tools as nt

import notedown

simple_backtick = """
```
code1
    space_indent


more code
```

text1
``

```
code2
	tab_indent
~~~
```

text2"""

simple_tilde = """
~~~
code1
    space_indent


more code
~~~

text1
``

~~~~
code2
	tab_indent
~~~
~~~~

text2"""

simple_indented = """
    code1
        space_indent


    more code

text1
``

	code2
		tab_indent
	~~~

text2"""

simple_code_cells = ['code1\n    space_indent\n\n\nmore code',
                     'code2\n	tab_indent\n~~~']
# note: ipython markdown cells do not end with a newline unless
# explicitly present.
simple_markdown_cells = ['text1\n``', 'text2']

alt_lang = """
This is how you write a code block in another language:

```bash
echo "This is bash ${BASH_VERSION}!"
```
"""

alt_lang_code = '%%bash\necho "This is bash ${BASH_VERSION}!"'


sample_markdown = u"""### Create IPython Notebooks from markdown

This is a simple tool to convert markdown with code into an IPython
Notebook.

Usage:

```
notedown input.md > output.ipynb
```

It is really simple and separates your markdown into code and not
code. Code goes into code cells, not-code goes into markdown cells.

Installation:

    pip install notedown
"""

# Generate the sample notebook from the markdown using
#
#    import notedown
#    reader = notedown.MarkdownReader()
#    sample_notebook = reader.reads(sample_markdown)
#    writer = notedown.JSONWriter()
#    print writer.writes(sample_notebook)
#
# which is defined in create_json_notebook() below

sample_notebook = r"""{
 "metadata": {},
 "nbformat": 3,
 "nbformat_minor": 0,
 "worksheets": [
  {
   "cells": [
    {
     "cell_type": "markdown",
     "metadata": {},
     "source": [
      "### Create IPython Notebooks from markdown\n",
      "\n",
      "This is a simple tool to convert markdown with code into an IPython\n",
      "Notebook.\n",
      "\n",
      "Usage:"
     ]
    },
    {
     "cell_type": "code",
     "collapsed": false,
     "input": [
      "notedown input.md > output.ipynb"
     ],
     "language": "python",
     "metadata": {},
     "outputs": []
    },
    {
     "cell_type": "markdown",
     "metadata": {},
     "source": [
      "It is really simple and separates your markdown into code and not\n",
      "code. Code goes into code cells, not-code goes into markdown cells.\n",
      "\n",
      "Installation:"
     ]
    },
    {
     "cell_type": "code",
     "collapsed": false,
     "input": [
      "pip install notedown"
     ],
     "language": "python",
     "metadata": {},
     "outputs": []
    }
   ],
   "metadata": {}
  }
 ]
}"""


roundtrip_markdown = u"""## A roundtrip test

Here is a code cell:

```python
a = 1
```

and here is another one:

```python
b = 2
```
"""


def create_json_notebook(markdown):
    reader = notedown.MarkdownReader()
    writer = notedown.JSONWriter()

    notebook = reader.reads(markdown)
    json_notebook = writer.writes(notebook)
    return json_notebook


def test_notedown():
    """Integration test the whole thing."""
    from difflib import ndiff
    notebook = create_json_notebook(sample_markdown)
    diff = ndiff(sample_notebook.splitlines(1), notebook.splitlines(1))
    print '\n'.join(diff)
    nt.assert_multi_line_equal(create_json_notebook(sample_markdown),
                               sample_notebook)


def parse_cells(text, regex):
    reader = notedown.MarkdownReader(code_regex=regex)
    return reader.parse_blocks(text)


def separate_code_cells(cells):
    codetype = notedown.MarkdownReader.code
    code_cells = [c['content'] for c in cells if c['type'] == codetype]
    return code_cells


def separate_markdown_cells(cells):
    markdowntype = notedown.MarkdownReader.markdown
    markdown_cells = [c['content'] for c in cells if c['type'] == markdowntype]
    return markdown_cells


def test_parse_gfm():
    """Test with GFM code blocks."""
    all_cells = parse_cells(simple_backtick, 'fenced')

    code_cells = separate_code_cells(all_cells)
    markdown_cells = separate_markdown_cells(all_cells)

    print "out: ", code_cells
    print "ref: ", simple_code_cells
    print "out: ", markdown_cells
    print "ref: ", simple_markdown_cells
    assert(code_cells == simple_code_cells)
    assert(markdown_cells == simple_markdown_cells)


def test_parse_tilde():
    """Test with ~~~ delimited code blocks."""
    all_cells = parse_cells(simple_tilde, 'fenced')

    code_cells = separate_code_cells(all_cells)
    markdown_cells = separate_markdown_cells(all_cells)

    assert(code_cells == simple_code_cells)
    assert(markdown_cells == simple_markdown_cells)


def test_parse_indented():
    """Test with indented code blocks."""
    all_cells = parse_cells(simple_indented, 'indented')

    code_cells = separate_code_cells(all_cells)
    markdown_cells = separate_markdown_cells(all_cells)

    print "out: ", code_cells
    print "ref: ", simple_code_cells
    print "out: ", markdown_cells
    print "ref: ", simple_markdown_cells
    assert(code_cells == simple_code_cells)
    assert(markdown_cells == simple_markdown_cells)


def test_alt_lang():
    """Specifying a language that isn't python should generate
    code blocks using %%language magic."""
    all_cells = parse_cells(alt_lang, 'fenced')

    code_cells = separate_code_cells(all_cells)

    assert(code_cells[0] == alt_lang_code)


def test_format_agnostic():
    """Test whether we can process markdown with either fenced or
    indented blocks."""
    fenced_cells = parse_cells(simple_backtick, None)
    indented_cells = parse_cells(simple_indented, None)

    fenced_code_cells = separate_code_cells(fenced_cells)
    indented_code_cells = separate_code_cells(indented_cells)

    fenced_markdown_cells = separate_markdown_cells(fenced_cells)
    indented_markdown_cells = separate_markdown_cells(indented_cells)

    assert(fenced_code_cells == indented_code_cells)
    assert(fenced_markdown_cells == indented_markdown_cells)


def test_pre_process_text():
    """test the stripping of blank lines"""
    block = {}
    ref = "\t \n\n   \t\n\ntext \t \n\n\n"
    block['content'] = ref
    notedown.MarkdownReader.pre_process_text_block(block)
    expected = "\n   \t\n\ntext \t \n"
    print "---"
    print "in: "
    print ref
    print "---"
    print "out: "
    print block['content']
    print "---"
    print "expected: "
    print expected
    print "---"
    assert(block['content'] == expected)


def test_roundtrip():
    """Run nbconvert using our custom markdown template to recover
    original markdown from a notebook.
    """
    # create a notebook from the markdown
    mr = notedown.MarkdownReader()
    roundtrip_notebook = mr.to_notebook(roundtrip_markdown)

    # write the notebook into json
    jw = notedown.JSONWriter()
    notebook_json = jw.writes(roundtrip_notebook)

    # write the json back into notebook
    jr = notedown.JSONReader()
    notebook = jr.reads(notebook_json)

    # convert notebook to markdown
    mw = notedown.MarkdownWriter(template_file='notedown/templates/markdown.tpl', strip_outputs=True)
    markdown = mw.writes(notebook)

    nt.assert_multi_line_equal(roundtrip_markdown, markdown)


def test_template_load():
    """MarkdownWriter should be able to load a template from an
    absolute path. IPython requires a relative path.
    """
    template_abspath = os.path.abspath('notedown/templates/markdown.tpl')
    writer = notedown.MarkdownWriter(template_file=template_abspath)
    import jinja2
    assert(isinstance(writer.exporter.template, jinja2.Template))


def test_markdown_markdown():
    mr = notedown.MarkdownReader()
    mw = notedown.MarkdownWriter(notedown.markdown_template)
    nb = mr.reads(roundtrip_markdown)
    mw.writes(nb)
