"""Edge-case tests for caption summarization fallbacks."""

from scipreprocess.preprocessing import (
    CAPTION_SUMMARY_WORD_LIMIT,
    clean_text,
    summarize_caption,
)


def test_summarize_caption_empty_returns_empty_string():
    """Empty or whitespace captions should produce an empty summary."""

    assert summarize_caption("") == ""
    assert summarize_caption("   \n  ") == ""


def test_summarize_caption_single_sentence_trimmed():
    """A single sentence caption is returned as-is once trimmed."""

    caption = "Single sentence caption with trailing spaces.   "
    expected = "Single sentence caption with trailing spaces."

    assert summarize_caption(caption) == expected


def test_summarize_caption_truncates_when_over_word_limit():
    """Captions exceeding the word limit are truncated with an ellipsis."""

    words = [f"word{i}" for i in range(CAPTION_SUMMARY_WORD_LIMIT + 5)]
    caption = " ".join(words)
    expected = " ".join(words[:CAPTION_SUMMARY_WORD_LIMIT]) + "…"

    assert summarize_caption(caption) == expected


def test_summarize_caption_returns_cleaned_caption_when_tokenization_empty():
    """If tokenization yields no tokens, fall back to the cleaned caption."""

    caption = "  .??!  "
    cleaned = clean_text(caption)

    assert cleaned  # Guard to ensure fallback behaviour is exercised
    assert summarize_caption(caption) == cleaned
