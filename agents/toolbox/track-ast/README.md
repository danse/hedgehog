# GHC AST facts for `track-levels.py`

`Facts.hs` parses the statement groups emitted by `scripts/tidal-groups.sh`
(the live Emacs sender's grouping) with GHC's parser API. It writes one fact
per line:

```text
LINE BIND ("bedPlay" ((pvar "t")) (chain # ...))
LINE STMT (op "$" (var "d2") (var "bass"))
```

`track-levels.py` reads those S-expressions and keeps the level/energy model.
Record fields keep their bound expressions, so selector calls such as
`koto utopia` can be resolved from the parsed facts. `parseDeclaration` handles
bindings and type declarations; expression groups
fall back to `parseStmt`. A group neither parser accepts emits an `ERROR` fact,
so silent source-language gaps are visible. Nothing here starts GHCi, OSC,
SuperDirt or sclang. `build.sh` compiles the helper with the installed GHC into
a versioned user cache and is called on demand; compiler output goes to stderr.

The GHC parser is version-specific. If the installed GHC changes, `build.sh`
uses a different cache directory and rebuilds.
