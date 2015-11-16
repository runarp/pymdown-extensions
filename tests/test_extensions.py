"""Test extension libraries."""
from __future__ import unicode_literals
import yaml
import os
import markdown
import difflib
import codecs
import nose
import copy

CURRENT_DIR = os.path.dirname(__file__)


def compare_results(cfg, testfile, update=False, force_update_all=False):
    """Compare test reslts."""

    extension = []
    extension_config = {}
    for k, v in cfg['extensions'].items():
        extension.append(k)
        if v:
            extension_config[k] = v

    if update:
        generate_html(testfile, extension, extension_config, force_update_all)
    else:
        check_markdown(testfile, extension, extension_config)


def generate_html(testfile, extension, extension_config, force_update_all):
    """Generate html from markdown."""

    expected_html = os.path.splitext(testfile)[0] + '.html'
    if (
        force_update_all or
        not os.path.exists(expected_html) or
        os.path.getmtime(expected_html) < os.path.getmtime(testfile)
    ):
        print('Updated: %s' % expected_html)
        markdown.markdownFromFile(
            input=testfile, output=expected_html, encoding='utf-8',
            extensions=extension, extension_config=extension_config
        )


def check_markdown(testfile, extension, extension_config):
    """Check the markdown."""

    expected_html = os.path.splitext(testfile)[0] + '.html'
    with codecs.open(testfile, 'r', encoding='utf-8') as f:
        source = f.read()

    results = markdown.Markdown(
        extensions=extension, extension_config=extension_config
    ).convert(source)

    try:
        with codecs.open(expected_html, 'r', encoding='utf-8') as f:
            expected = f.read().replace("\r\n", "\n")
    except Exception:
        expected = ''

    diff = [
        l for l in difflib.unified_diff(
            expected.splitlines(True),
            results.splitlines(True),
            expected_html,
            os.path.join(os.path.dirname(testfile), 'results.html'),
            n=3
        )
    ]
    if diff:
        raise Exception(
            'Output from "%s" failed to match expected '
            'output.\n\n%s' % (testfile, ''.join(diff))
        )


def test_extensions():
    """Test extensions."""

    for filename in os.listdir(CURRENT_DIR):
        directory = os.path.join(CURRENT_DIR, filename)
        if os.path.isdir(directory):
            cfg_path = os.path.join(directory, 'tests.yml')
            if os.path.exists(cfg_path):
                with codecs.open(cfg_path, 'r', encoding='utf-8') as f:
                    cfg = yaml.load(f.read())
                for testfile in os.listdir(directory):
                    if testfile.endswith('.txt'):
                        key = os.path.splitext(testfile)[0]
                        test_cfg = copy.deepcopy(cfg['__default__'])
                        if 'extensions' not in test_cfg:
                            test_cfg['extensions'] = {}
                        for k, v in cfg.get(key, {}).items():
                            for k1, v1 in v.items():
                                test_cfg[k][k1] = v1
                        yield compare_results, test_cfg, os.path.join(directory, testfile)


def run():
    """Run nosetests."""

    nose.main()