;;; tidal-groups.el --- emit sender groups for offline tools -*- lexical-binding: t; -*-

;; Run through scripts/tidal-groups.sh, which loads emacs/init.el first.
;; Output is NUL-separated quadruples, one per group:
;;   PATH \0 START-LINE \0 GROUP-TEXT \0 LINE-NUMBERS(csv) \0

(dolist (path (cdr argv))
  (with-temp-buffer
    (insert-file-contents path)
    (dolist (group (hedgehog-group-statements-numbered (buffer-string)))
      (let ((lines (cdr group)))
        (princ (format "%s\0%d\0%s\0%s\0"
                       path
                       (car group)
                       (mapconcat #'cdr lines "\n")
                       (mapconcat #'number-to-string
                                  (mapcar #'car lines) ",")))))))
