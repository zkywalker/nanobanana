# Profile: General (通用兜底)

## Trigger Condition

When user input cannot be clearly matched to any other Profile (photo, illustration, diagram, text-heavy, minimal), fall back to this Profile.

## Behavior

**Only perform base optimization — no enhancement at all.**

Base optimization includes:
1. Format correction (tag-style → natural language)
2. Smart translation (translate descriptions, preserve in-image text)
3. Structuring (subject first)

## Design Principle

- Prefer less optimization over distorting user intent
- User didn't specify a style → don't add a style
- User didn't specify lighting → don't add lighting
- Faithfully convey the user's description; only perform format and language conversion

## Example

**User input**: 一只猫趴在键盘上

**Base optimization**: A cat lying on a keyboard

**Will NOT add**: any style, lighting, composition, or atmosphere descriptions

## When to Upgrade to Another Profile

If during analysis you discover clear style signals (e.g., "写实的", "动漫风格的", "画一个流程图"), reclassify to the corresponding Profile instead of staying in general.

General is the fallback choice, not the default choice. Always try to match a specific Profile first.
