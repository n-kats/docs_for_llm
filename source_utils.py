from typing import Sequence


def split_text(
    text: str, max_length: int, max_overwrap: int, splitters: Sequence[str], splitter_limit: int
) -> list[str]:
    assert max_length > 0
    assert max_overwrap >= 0
    assert splitter_limit >= 0
    assert max_overwrap + splitter_limit < max_length
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_length
        if end > len(text):
            end = len(text)
        else:
            end_candidates = []
            for splitter in splitters:
                pos = text.rfind(splitter, end - split_limit, end)
                if pos != -1:
                    end_candidates.append(pos + len(splitter))
            if end_candidates:
                end = max(end_candidates)

        chunks.append(text[start:end])
        if end == len(text):
            break

        next_start = end - max_overwrap
        start_candidates = []
        for splitter in splitters:
            pos = text.find(splitter, next_start, next_start + split_limit)
            if pos != -1:
                start_candidates.append(pos + len(splitter))
        if start_candidates:
            next_start = min(start_candidates)

        assert start < next_start <= end
        start = next_start

    return chunks
