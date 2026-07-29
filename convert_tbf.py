#!/usr/bin/env python3
import argparse
import os
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class TreeNode:
    label: str
    children: Optional[List["TreeNode"]] = None
    word: Optional[str] = None

    def is_leaf(self) -> bool:
        return self.children is None

    def linearize(self) -> str:
        if self.is_leaf():
            return f"({self.label} {self.word})"
        return f"({self.label} {' '.join(child.linearize() for child in self.children)})"

    def leaves(self) -> List[Tuple[str, str]]:
        if self.is_leaf():
            if self.label == "-NONE-":
                return []
            return [(self.label, self.word)]
        out: List[Tuple[str, str]] = []
        for child in self.children:
            out.extend(child.leaves())
        return out


def tokenize_treebank(text: str) -> List[str]:
    return text.replace("(", " ( ").replace(")", " ) ").split()


def parse_tree(tokens: List[str], i: int) -> Tuple[TreeNode, int]:
    if i >= len(tokens) or tokens[i] != "(":
        raise ValueError(f"Expected '(' at token index {i}")
    i += 1
    if i < len(tokens) and tokens[i] == "(":
        children: List[TreeNode] = []
        while i < len(tokens) and tokens[i] == "(":
            child, i = parse_tree(tokens, i)
            children.append(child)
        if i >= len(tokens) or tokens[i] != ")":
            raise ValueError("Expected ')' to close unlabeled bracket")
        i += 1
        if len(children) == 1:
            return children[0], i
        return TreeNode(label="ROOT", children=children), i

    if i >= len(tokens):
        raise ValueError("Unexpected EOF after '('")
    label = tokens[i]
    i += 1
    if i >= len(tokens):
        raise ValueError(f"Unexpected EOF after label '{label}'")

    if tokens[i] == "(":
        children: List[TreeNode] = []
        while i < len(tokens) and tokens[i] == "(":
            child, i = parse_tree(tokens, i)
            children.append(child)
        if i >= len(tokens) or tokens[i] != ")":
            raise ValueError(f"Expected ')' to close non-terminal '{label}'")
        i += 1
        return TreeNode(label=label, children=children), i

    word = tokens[i]
    i += 1
    if i >= len(tokens) or tokens[i] != ")":
        raise ValueError(f"Expected ')' after terminal ({label} {word})")
    i += 1
    return TreeNode(label=label, word=word), i


def parse_forest(text: str) -> List[TreeNode]:
    tokens = tokenize_treebank(text)
    trees: List[TreeNode] = []
    i = 0
    while i < len(tokens):
        if tokens[i] != "(":
            raise ValueError(f"Unexpected token '{tokens[i]}' at index {i}")
        tree, i = parse_tree(tokens, i)
        trees.append(tree)
    return trees


def normalize_top(tree: TreeNode) -> TreeNode:
    if tree.label == "TOP" and not tree.is_leaf() and len(tree.children) == 1:
        return tree
    if tree.label in {"TOP", "ROOT"}:
        return TreeNode(label="TOP", children=[tree])
    return TreeNode(label="TOP", children=[tree])


def check_tagged_compatibility(tagged_sentences: List[str]) -> List[str]:
    issues: List[str] = []
    for sent_idx, sentence in enumerate(tagged_sentences, start=1):
        if not sentence.strip():
            issues.append(f"Sentence {sent_idx}: empty sentence after conversion.")
            continue
        for tok_idx, token in enumerate(sentence.split(), start=1):
            if "_" not in token:
                issues.append(
                    f"Sentence {sent_idx}, token {tok_idx}: missing '_' separator in '{token}'."
                )
                continue
            tag, word = token.split("_", 1)
            if not tag or not word:
                issues.append(
                    f"Sentence {sent_idx}, token {tok_idx}: malformed tag_word token '{token}'."
                )
            if "_" in tag or "_" in word:
                issues.append(
                    f"Sentence {sent_idx}, token {tok_idx}: additional '_' found in '{token}', "
                    "not safe for `main.py parse --pos-tag 0`."
                )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert bracketed .tbf trees into LAL-Parser friendly files."
    )
    parser.add_argument("--input", required=True, help="Input .tbf file path")
    parser.add_argument("--output-prefix", default=None, help="Output file prefix")
    parser.add_argument(
        "--strict-compat",
        action="store_true",
        help="Return non-zero if compatibility issues are found.",
    )
    args = parser.parse_args()

    input_path = args.input
    if args.output_prefix:
        output_prefix = args.output_prefix
    else:
        base_name = os.path.basename(input_path)
        output_prefix = os.path.join(os.path.dirname(input_path), base_name + ".lal")

    out_const = output_prefix + ".const.auto.clean"
    out_raw = output_prefix + ".raw.txt"
    out_tagged = output_prefix + ".tagged.txt"

    with open(input_path, "r", encoding="utf-8-sig") as f:
        text = f.read()
    trees = parse_forest(text)
    trees = [normalize_top(t) for t in trees]

    const_lines: List[str] = []
    raw_lines: List[str] = []
    tagged_lines: List[str] = []
    for tree in trees:
        leaves = tree.leaves()
        raw_lines.append(" ".join(word for _, word in leaves))
        tagged_lines.append(" ".join(f"{tag}_{word}" for tag, word in leaves))
        const_lines.append(tree.linearize())

    with open(out_const, "w", encoding="utf-8") as f:
        f.write("\n".join(const_lines) + "\n")
    with open(out_raw, "w", encoding="utf-8") as f:
        f.write("\n".join(raw_lines) + "\n")
    with open(out_tagged, "w", encoding="utf-8") as f:
        f.write("\n".join(tagged_lines) + "\n")

    issues = check_tagged_compatibility(tagged_lines)

    print(f"Converted {len(trees)} trees from: {input_path}")
    print(f"Constituency output: {out_const}")
    print(f"Raw sentence output: {out_raw}")
    print(f"Tagged sentence output: {out_tagged}")
    if issues:
        print("\nCompatibility check: FOUND ISSUES")
        for issue in issues[:20]:
            print(f"- {issue}")
        if len(issues) > 20:
            print(f"- ... and {len(issues) - 20} more")
        print("\nUse raw input with `--pos-tag 1|2`, or fix tagged token formatting.")
        return 2 if args.strict_compat else 0

    print("\nCompatibility check: OK for `python src_joint/main.py parse --pos-tag 0`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
