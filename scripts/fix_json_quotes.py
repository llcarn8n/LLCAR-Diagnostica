#!/usr/bin/env python3
"""Fix unescaped double-quotes inside JSON string values.

Improved heuristic: when a '"' is followed by ',' then non-'"' char,
it's treated as an inner unescaped quote (not a string close).
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BACKSLASH = '\\'


def fix_unescaped_quotes(content):
    """Fix unescaped double-quotes inside JSON string values."""
    result = []
    i = 0
    in_string = False

    while i < len(content):
        c = content[i]

        # Handle escape sequences (e.g. \", \\, \n, etc.)
        if c == BACKSLASH and i + 1 < len(content):
            result.append(c)
            result.append(content[i + 1])
            i += 2
            continue

        if c == '"':
            if not in_string:
                in_string = True
                result.append(c)
                i += 1
                continue
            else:
                # Determine if this is a closing quote or an unescaped inner quote.
                # Look ahead past whitespace.
                j = i + 1
                while j < len(content) and content[j] in ' \t\r\n':
                    j += 1

                if j >= len(content):
                    # End of file - treat as closing
                    in_string = False
                    result.append(c)
                    i += 1
                    continue

                next_structural = content[j]

                if next_structural in ':}]':
                    # Unambiguously closing (key end, object/array end)
                    in_string = False
                    result.append(c)
                elif next_structural == ',':
                    # Ambiguous: could be closing string in array/object,
                    # OR inner quote followed by comma-separated Chinese text.
                    # Check what comes AFTER the comma (skip whitespace).
                    k = j + 1
                    while k < len(content) and content[k] in ' \t\r\n':
                        k += 1
                    after_comma = content[k] if k < len(content) else ''

                    if after_comma == '"' or after_comma in '}]':
                        # Next item starts with a quote or closes the container.
                        # This looks like a genuine string close.
                        in_string = False
                        result.append(c)
                    else:
                        # After comma comes a non-quote char (e.g. Chinese text).
                        # This is an inner unescaped quote - escape it.
                        result.append(BACKSLASH)
                        result.append('"')
                else:
                    # Any other char after '"' means it's an inner quote
                    result.append(BACKSLASH)
                    result.append('"')
                i += 1
                continue

        result.append(c)
        i += 1

    return ''.join(result)


for batch in ['batch_026', 'batch_185']:
    path = f'knowledge-base/translate_batches/{batch}_out.json'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    fixed = fix_unescaped_quotes(content)

    try:
        data = json.loads(fixed)
        print(f'{batch}: FIXED OK ({len(data)} records)')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(fixed)
        print(f'  Saved.')
    except json.JSONDecodeError as e:
        print(f'{batch}: Still broken at pos={e.pos}: {e}')
        ctx = fixed[max(0, e.pos - 80):e.pos + 80]
        print(f'  Context: {repr(ctx)}')
