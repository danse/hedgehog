;;; check-sender.el --- Regression checks for the Tidal sender -*- lexical-binding: t; -*-

;; Run with:
;;   emacs --batch -q --init-directory emacs -l emacs/init.el -l scripts/check-sender.el

(defvar hedgehog-sender-test-failures 0)

(defun hedgehog-sender-check (label input expected)
  "Check that INPUT groups into EXPECTED, reporting under LABEL."
  (let ((got (hedgehog--group-statements input)))
    (if (equal got expected)
        (princ (format "  ok    %s\n" label))
      (setq hedgehog-sender-test-failures (1+ hedgehog-sender-test-failures))
      (princ (format "  FAIL  %s\n    expected: %S\n    got:      %S\n"
                     label expected got)))))

(princ "Hedgehog sender grouping\n")

(hedgehog-sender-check
 "column-0 orbits"
 "d1 $ kick\nd2 $ snare\nd3 $ hats\n"
 '("d1 $ kick" "d2 $ snare" "d3 $ hats"))

(hedgehog-sender-check
 "indented orbits"
 "  d1 $ kick\n  d2 $ snare\n  d3 $ hats\n"
 '("  d1 $ kick" "  d2 $ snare" "  d3 $ hats"))

(hedgehog-sender-check
 "column-0 xfades"
 "xfadeIn 4 8 $ chords\nxfadeIn 2 8 $ silence\n"
 '("xfadeIn 4 8 $ chords" "xfadeIn 2 8 $ silence"))

(hedgehog-sender-check
 "indented xfades"
 "  xfadeIn 4 8 $ chords\n  xfadeIn 2 8 $ silence\n"
 '("  xfadeIn 4 8 $ chords" "  xfadeIn 2 8 $ silence"))

(hedgehog-sender-check
 "mixed orbit indentation"
 "d1 $ kick\n  d2 $ snare\n"
 '("d1 $ kick" "  d2 $ snare"))

(hedgehog-sender-check
 "multi-line single expression"
 "xfadeIn 4 8 $ stack\n  [chords, arp]\n"
 '("xfadeIn 4 8 $ stack\n  [chords, arp]"))

(hedgehog-sender-check
 "leading continuation operator"
 "d1 $ kick\n# gain 0.8\nd2 $ snare\n"
 '("d1 $ kick\n# gain 0.8" "d2 $ snare"))

(hedgehog-sender-check
 "let block then orbit"
 "let\n  x = 1\n  y = 2\nd1 $ x\n"
 '("let\n  x = 1\n  y = 2" "d1 $ x"))

(hedgehog-sender-check
 "indented let block then orbit"
 "  let\n    x = 1\n    y = 2\n  d1 $ x\n"
 '("  let\n    x = 1\n    y = 2" "  d1 $ x"))

(hedgehog-sender-check
 "let block then consecutive orbits"
 "let\n  x = 1\n  y = 2\nd1 $ x\nd2 $ y\n"
 '("let\n  x = 1\n  y = 2" "d1 $ x" "d2 $ y"))

(hedgehog-sender-check
 "indented let then consecutive orbits"
 "  let\n    x = 1\n    y = 2\n  d1 $ x\n  d2 $ y\n"
 '("  let\n    x = 1\n    y = 2" "  d1 $ x" "  d2 $ y"))

(hedgehog-sender-check
 "multi-line binding"
 "bassPulse =\n  slow 4 $ n \"bf2 ~\"\n    # s \"hedge_sine\"\nd1 $ bassPulse\n"
 '("bassPulse =\n  slow 4 $ n \"bf2 ~\"\n    # s \"hedge_sine\"" "d1 $ bassPulse"))

(hedgehog-sender-check
 "comments and blank lines"
 "-- intro\nd1 $ kick\n\n-- snare\nd2 $ snare\n"
 '("-- intro\nd1 $ kick" "-- snare\nd2 $ snare"))

(hedgehog-sender-check
 "blank lines between orbits"
 "d1 $ kick\n\nd2 $ snare\n\nd3 $ hats\n"
 '("d1 $ kick" "d2 $ snare" "d3 $ hats"))

(hedgehog-sender-check
 "emergence-style adjacent statements with a comment header"
 "d1 $ subDrone # gain 0.82\n-- the low pad appears under the drone\nxfadeIn 2 16 $ lowPad # lpf 520\n"
 '("d1 $ subDrone # gain 0.82"
   "-- the low pad appears under the drone\nxfadeIn 2 16 $ lowPad # lpf 520"))

;; The physical Ctrl+Return event must reach the project sender, not
;; tidal.el's tidal-run-multiple-lines (which wraps the whole paragraph).
(with-temp-buffer
  (tidal-mode)
  (dolist (spec '(("C-<return>" . hedgehog-eval-block)
                  ("C-RET"      . hedgehog-eval-block)
                  ("C-c C-e"    . hedgehog-eval-block)
                  ("C-c C-r"    . hedgehog-send-region)))
    (let ((got (key-binding (kbd (car spec)))))
      (if (eq got (cdr spec))
          (princ (format "  ok    key %s -> %s\n" (car spec) got))
        (setq hedgehog-sender-test-failures
              (1+ hedgehog-sender-test-failures))
        (princ (format "  FAIL  key %s -> %S (want %S)\n"
                       (car spec) got (cdr spec)))))))

(if (= hedgehog-sender-test-failures 0)
    (princ "All sender checks passed.\n")
  (princ (format "%d sender check(s) failed.\n" hedgehog-sender-test-failures))
  (kill-emacs 1))
